import progTiroc.db as db

from .text_analysis import analyze_sentiment, analyze_intent, analyze_categories

import itertools
import bisect
from random import randint
import re
import logging
import os
import mongoengine
import datetime

from typing import List, Tuple, Dict, Any, Optional

logging.basicConfig(filename='debug.log', level=logging.INFO)
log = logging.getLogger(__name__)

PROJECT_ID: str = os.environ.get('PROJECT_ID')

if PROJECT_ID is None:
    log.fatal("PROJECT_ID is None")
    exit(1)

LIBRARY_CONDITIONS = ['__type__', '__has__']


def check(condition: Dict[str, Any], value: Dict[str, Any]) -> bool:

    def std_check(k: str, v: Any, value: Dict[str, Any]):
        matches = re.match(r'^(.+?)(?:__(lt|gt|eq|ne|le|ge|in|nin))?$', k)

        if matches is None:
            print('Unrecognied action')
            return False

        to_check: Optional[Any] = value.get(matches.group(1))
        if to_check is None:
            return True

        try:
            suffix: str = matches.group(2)
            if suffix is None:
                return check(v, to_check)
            elif suffix == 'lt':
                return to_check < v
            elif suffix == 'gt':
                return to_check > v
            elif suffix == 'eq':
                return to_check == v
            elif suffix == 'ne':
                return to_check != v
            elif suffix == 'le':
                return to_check <= v
            elif suffix == 'ge':
                return to_check >= v
            elif suffix == 'in':
                return to_check in v
            elif suffix == 'nin':
                return to_check not in v
        except Exception as e:
            print(e)
            return False

    # Ottieni la lista dei campi obbligatori e se non
    # corrisponde a quelli reali non considerare questo caso
    has_attr = condition.get('__has__')
    if (has_attr is not None) and any([value.get(k) is None for k in has_attr]):
        return False

    return all([
        std_check(k, v, value) for k, v in condition.items()
        if k not in LIBRARY_CONDITIONS
    ])


# __type__ va controllato in inserimento


def possible(params: List[db.Params], condition: Dict[str, Dict]) -> List[int]:
    poss = []

    for i in range(len(params)):
        # Se il tipo non è corretto non considerare questo caso
        if params[i].ofTopic != condition['__type__']:
            continue

        # Se qualche condizione(di quelle standard immediatamente controllabili) non è rispettata
        # non considerare questo caso
        if not check(condition, params[i].values):
            continue

        # Se ha passato tutte le casistiche considera questo caso
        poss.append(i)

    return poss


# (numero, nome, condizione python)
def verify_mapping(msg: Dict[str, Any], params: List[db.Params],
                   mapping: List[int], py: Optional[str]) -> bool:
    if py is None:
        return True

    mapped = [params[mapping[i]] for i in range(len(mapping))]

    return eval(
        py, globals=None, locals={
            '_': mapped,
            'm': msg
        })  # Should be boolean expression in terms of _


# Returns the complete list of valid mappings
def get_multiple_mappings(msg: Dict[str, Any], msg_condition: Dict[str, Any],
                          params: List[db.Params],
                          params_conditions: List[Dict[str, Any]],
                          py: str) -> List[List[int]]:
    if check(msg_condition, msg):
        return []

    possibilities: List[List[int]] = itertools.product(
        *[possible(params, c) for c in params_conditions])

    return list(
        filter(lambda mapping: verify_mapping(msg, params, mapping, py),
               possibilities))


def get_mapping(msg: Dict[str, Any], msg_condition: Dict[str, Any],
                params: List[db.Params],
                params_conditions: List[Dict[str, Any]],
                py: str) -> Optional[List[int]]:
    mappings = get_multiple_mappings(msg, msg_condition, params,
                                     params_conditions, py)
    if not mappings:
        return None

    return mappings[randint(0, len(mappings) - 1)]


class AI:

    def create_database(self):
        return None  # TODO: Da implementare

    def get_action(self, msg: Dict[str, Any], ctx: db.Context
                  ) -> Optional[Tuple[int, db.Action, List[int]]]:
        params: List[db.Params] = sorted(
            ctx.params, lambda p: p.priority, reverse=True)

        res: List[Tuple[int, db.Rule, List[int]]] = []

        for i in range(len(params)):
            ps = params[:i + 1]

            conditions: List[Tuple[db.Rule, Optional[List[int]]]] = [
                (rule,
                 get_mapping(msg, rule.condition.onMsg, params,
                             rule.condition.onParams, rule.condition.py))
                for rule in ps[-1].ofTopic.rules
            ]

            # Condition può restituire un singolo oggetto
            res += [(i + 1, rule, mapping) for (rule, mapping) in conditions
                    if mapping is not None]

        actions = list(
            zip(itertools.accumulate([r[1].score for r in res]), res))

        if len(actions) == 0:
            return None
        else:
            selection = actions[bisect.bisect_right([x[0] for x in actions],
                                                    randint(0, actions[-1][0]))]

            return selection[1][0], selection[1][1].action, selection[1][2]

    def get_message(self, userId: int, text: str) -> str:
        # Se condition è fatto come una condizione mongodb allora posso
        # eseguirla e eventualmente decidere con cosa posso eseguire tale regola

        ctx: db.Context
        try:
            ctx = db.Context.objects(ofUser=userId, endTimestamp=None).get()
        except mongoengine.DoesNotExist as e:
            log.fatal(e)
            exit(1)

        intent = analyze_intent(PROJECT_ID, ctx.ofUser.googleSessionId, text,
                                'en', log)

        intent.intent.name = intent.intent.name[
            len('projects/') + len(PROJECT_ID) + len('/agent/intents/'):]

        sentiment = analyze_sentiment(text, log)
        categories = analyze_categories(text, log)

        msg = {
            'intent': intent,
            'sentiment': sentiment,
            'categories': categories
        }

        max_priority: int
        action: db.Action
        mapping: List[int]

        max_priority, action, mapping = self.get_action(msg, ctx)

        text: str = action.text[randint(0, len(action.text) - 1)]

        db.BotMessage

        ord_param = sorted(ctx.params, lambda p: p.priority, reverse=True)[:action[0] + 1]
        _ = [ord_param[mapping[i]] for i in range(len(mapping))]

        # Non ci sono topic di cui fare il push nè nomi da esportare nè
        # togliere argomenti
        if action.operations:
            ctx.endTimestamp = datetime.datetime.now()
            ctx.save()


            new_ctx = db.Context(
                **{k: v for (k, v) in ctx.to_mongo().items() if k != '_id'})
            new_ctx.startTimestamp = ctx.endTimestamp

            changed: bool = False

            # for do in action.operations:
            #     if do.op == 'exportNames':
            #         param: db.Params = _[do.index]
            #         [do.name] = eval(
            #                 do.val,
            #                 globals={},
            #                 locals={'_': _, 'm': msg}
            #         )
            #     elif do.po == 'push':

        return text.format(_=_, m=msg)
