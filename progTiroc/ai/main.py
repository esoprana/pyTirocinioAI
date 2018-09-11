import progTiroc.db as db

from .text_analysis import analyze_sentiment, analyze_intent, analyze_categories

import itertools
import bisect
from random import randint
import re
import logging
import os
from datetime import datetime
import uuid

import mongoengine

from typing import List, Tuple, Dict, Any, Optional

logging.basicConfig(filename='debug.log', level=logging.INFO)
log = logging.getLogger(__name__)

PROJECT_ID: str = os.environ.get('PROJECT_ID')

if PROJECT_ID is None:
    log.fatal("PROJECT_ID is None")
    exit(1)

LIBRARY_CONDITIONS = ['__type__', '__has__']


def check(condition: Dict[str, Any], value: Dict[str, Any]) -> bool:

    def std_check(k: str, v: Any, value: Dict[str, Any]) -> bool:
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
        std_check(k, v, value)
        for k, v in condition.items()
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

    _ = list([params[iM] for iM in mapping])

    return eval(
        py, globals=None, locals={
            '_': _,
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


def analyze_text(text: str, googleSessionId: uuid) -> Dict[str, Any]:
    intent = analyze_intent(PROJECT_ID, googleSessionId, text, 'en', log)

    intent.intent.name = intent.intent.name[len('projects/') + len(PROJECT_ID) +
                                            len('/agent/intents/'):]

    sentiment = analyze_sentiment(text, log)
    categories = analyze_categories(text, log)

    return {'intent': intent, 'sentiment': sentiment, 'categories': categories}


class AI:

    def create_database(self):
        return None  # TODO: Da implementare

    @staticmethod
    def get_action(msg: Dict[str, Any],
                   ctx: db.Context) -> Optional[Tuple[int, db.Rule, List[int]]]:
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
            res += [(i + 1, rule, mapping)
                    for (rule, mapping) in conditions
                    if mapping is not None]

        actions = list(
            zip(itertools.accumulate([r[1].score for r in res]), res))

        if len(actions) == 0:
            return None
        else:
            selection = actions[bisect.bisect_right([x[0] for x in actions],
                                                    randint(0, actions[-1][0]))]

            return selection[1][0], selection[1][1], selection[1][2]

    @staticmethod
    def update_context(mapping: List[int], action: db.Action,
                       options: Dict[str, Any],
                       init_values: Dict[str, Any]) -> db.Context:
        new_ctx = db.Context(**init_values)

        max_pr = new_ctx.params[-1].priority
        _ = options['_']

        for do in action.operations:

            if do['op'] == 'exportName':
                # Get old param values
                old_param = _[do['index']]

                # Create a new param object
                new_param = db.Params(
                    ofTopic=old_param.ofTopic,
                    values=old_param.values,
                    startTime=datetime.now(),
                    priority=old_param.priority)

                # Change/add value using eval(no globals only locals)
                new_val = eval(do['val'], {}, options)

                if new_val is None:
                    del new_param.values[do['name']]
                else:
                    new_param.values[do['name']] = new_val

                # Sobstitute old Param instance
                new_ctx.params[mapping[do['index']]] = new_param
                _[do['index']] = new_param
            elif do['op'] == 'push':
                max_pr = max_pr - 1
                new_param = db.Params(
                    ofTopic=do['topic'],
                    values={},
                    startTime=datetime.now(),
                    priority=max_pr)

                new_ctx.params.append(new_param)
                _.append(new_param)
                # mapping.append(len(new_ctx.params) - 1)
            elif do['op'] == 'popUntil':
                new_ctx.params = new_ctx.params[:mapping[do['index']] + 1]
            elif do['op'] == 'pop':
                new_ctx.params = new_ctx.params[:-1]

        return new_ctx

    @staticmethod
    def get_message(userId: int, msg: Dict[str, Any]) -> Optional[str]:
        # Se condition è fatto come una condizione mongodb allora posso
        # eseguirla e eventualmente decidere con cosa posso eseguire tale regola

        old_ctx: db.Context
        try:
            contexts: List[db.Context] = db.Context.objects(
                ofUser=userId).order_by('-timestamp')
            if len(contexts) == 0:
                log.error("0 contexts")  # TODO: Use logger
                return None
            else:
                old_ctx = contexts[0]
        except mongoengine.DoesNotExist as e:
            log.error(e)
            return None

        max_priority: int
        rule: db.Rule
        mapping: List[int]

        max_priority, rule, mapping = AI.get_action(msg, old_ctx)

        text: str = rule.action.text[randint(0, len(rule.action.text) - 1)]

        ord_param = sorted(
            old_ctx.params, lambda p: p.priority,
            reverse=True)[:max_priority + 1]

        _ = [ord_param[mpItem] for mpItem in mapping]

        options = {'_': _, 'm': msg}

        new_ctx: db.Context = AI.update_context(
            mapping, rule.action, options,
            dict(
                ofUser=old_ctx.ofUser,
                timestamp=datetime.now(),
                params=ord_param,
                message=db.BotMessage(text=text.format(**options))))

        new_ctx.save()

        return new_ctx.message.text
