import itertools
import bisect
from random import randint
import re
import logging
from datetime import datetime
import uuid
from typing import List, Tuple, Dict, Any, Optional
import json

import mongoengine
from bson import ObjectId
import umongo

from progTiroc import db
from ._text_analysis import analyze_sentiment, analyze_intent, analyze_categories

logging.basicConfig(filename='debug.log', level=logging.INFO)
log = logging.getLogger(__name__)

LIBRARY_CONDITIONS = ['__type__', '__has__', '__nhas__']


def check(condition: Dict[str, Any], value: Dict[str, Any]) -> bool:
    """ Check whole dict given condition an dict to check """

    def std_check(key: str, v: Any, value: Dict[str, Any]) -> bool:
        """ Check single value """

        matches = re.match(r'^(.+?)(?:__(lt|gt|eq|ne|le|ge|in|nin))?$', key)

        if matches is None:
            print('Unrecognied action')
            return False

        to_check: Optional[Any] = value.get(matches.group(1))
        if to_check is None:
            return True

        try:
            suffix: str = matches.group(2)
            print(v, to_check)
            if suffix is None:
                return check(v, to_check)
            if suffix == 'lt':
                return to_check < v
            if suffix == 'gt':
                return to_check > v
            if suffix == 'eq':
                return to_check == v
            if suffix == 'ne':
                return to_check != v
            if suffix == 'le':
                return to_check <= v
            if suffix == 'ge':
                return to_check >= v
            if suffix == 'in':
                return to_check in v

            # suffix == 'nin'
            return to_check not in v
        except Exception as e:
            print(e)
            return False

    # Ottieni la lista dei campi obbligatori e se non
    # corrisponde a quelli reali non considerare questo caso
    has_attr = condition.get('__has__', condition.get('__has_and__'))
    if (has_attr is not None) and any([value.get(k) is None for k in has_attr]):
        return False

    nhas_attr = condition.get('__nhas__', condition.get('__nhas_or__'))
    if (nhas_attr is not None) and any(
        [value.get(k) is not None for k in nhas_attr]):
        return False

    has_attr_or = condition.get('__has_or__')
    if (has_attr_or is not None) and all(
        [value.get(k) is None for k in has_attr_or]):
        return False

    nhas_attr_all = condition.get('__nhas__', condition.get('__nhas_all__'))
    if (nhas_attr_all is not None) and all(
        [value.get(k) is not None for k in nhas_attr_all]):
        return False

    return all([
        std_check(k, v, value)
        for k, v in condition.items()
        if k not in LIBRARY_CONDITIONS
    ])


# __type__ va controllato in inserimento


def possible(params: List[db.types.Params],
             condition: Dict[str, Dict]) -> List[int]:
    """ Get all indexes of params that satisfies condition(only static one, __py__ ignored) """
    poss = []

    for i, p in enumerate(params):
        # Se il tipo non è corretto non considerare questo caso

        if str(p.ofTopic.pk) != str(
                condition['__type__']):  # TODO: Change to __type__
            continue

        # Se qualche condizione(di quelle standard immediatamente controllabili) non è rispettata
        # non considerare questo caso
        if not check(condition, p.values):
            continue

        # Se ha passato tutte le casistiche considera questo caso
        poss.append(i)

    return poss


# (numero, nome, condizione python)
def verify_mapping(msg: Dict[str, Any], params: List[db.types.Params],
                   mapping: List[int], py: Optional[str]) -> bool:
    """ Check if a mapping given associated params and msg satisfies py """
    if py is None:
        return True

    _ = list([params[iM] for iM in mapping])

    return eval(py, None, {
        '_': _,
        'm': msg
    })  # Should be boolean expression in terms of _


# Returns the complete list of valid mappings
def get_multiple_mappings(msg: Dict[str, Any], msg_condition: Dict[str, Any],
                          params: List[db.types.Params],
                          params_conditions: List[Dict[str, Any]],
                          py: str) -> List[List[int]]:
    """ Get all possible mappings """
    if not ((msg is None and msg_condition is None) or
            (msg is not None and msg_condition is not None and
             check(msg_condition, msg))):
        return []

    m = [possible(params, c) for c in params_conditions]

    tops = [
        i for i, w in enumerate(params_conditions)
        if w.get('__top__', False) is True
    ]
    if len(tops) > 1:
        print('MULTIPLE TOPS')
    elif len(tops) == 1:
        if len(params) - 1 in m[tops[0]]:
            m[tops[0]] = [len(params) - 1]
        else:
            m[tops[0]] = []  # TODO: return directly []

    possibilities: List[List[int]] = itertools.product(*m)

    return [
        mapping for mapping in possibilities
        if verify_mapping(msg, params, mapping, py)
    ]


def get_mapping(msg: Dict[str, Any], msg_condition: Dict[str, Any],
                params: List[db.types.Params],
                params_conditions: List[Dict[str, Any]],
                py: str) -> Optional[List[int]]:
    """ Get a single mapping given data and conditions """
    mappings = get_multiple_mappings(msg, msg_condition, params,
                                     params_conditions, py)
    if not mappings:
        return None

    return mappings[randint(0, len(mappings) - 1)]


class AI:

    def __init__(self, google_project_id: str, log: logging.Logger):
        if google_project_id is None:
            assert google_project_id, "google_project_id must be not null"

        self._google_project_id = google_project_id

    def analyze_text(self, text: str, googleSessionId: uuid) -> Dict[str, Any]:
        """
        Return intent, sentiment and categories from google apis given text
        and sessionid
        """
        intent = analyze_intent(self._google_project_id, googleSessionId, text,
                                'en', log)

        sentiment = analyze_sentiment(text, log)
        categories = analyze_categories(text, log)

        return {
            'intent': intent,
            'sentiment': sentiment,
            'categories': categories
        }

    async def create_database(self, dbi: 'progTiroc.db.DBInstance',
                              path: str) -> Tuple[ObjectId, ObjectId]:
        DATA_LOCK = 'data.lock'

        res: Tuple[ObjectId, ObjectId]

        import os
        if os.path.isfile(DATA_LOCK):  # If database wasn't alredy initialized
            print('DB ALREADY INITIALIZED')

            with open(DATA_LOCK, 'r') as f:
                default_topic = ObjectId(str(f.read(24)))
                fallback_rule = ObjectId(str(f.read(24)))

            res = (default_topic, fallback_rule)
        else:
            print('DB INITIALIZED NOW')
            topics = json.load(open(os.path.join(path, 'topics.json'), 'r'))
            rules = json.load(open(os.path.join(path, 'rules.json'), 'r'))

            res = await self._init_database(dbi, topics, rules)

            with open(DATA_LOCK, 'w') as f:
                f.write(str(res[0]))
                f.write(str(res[1]))
        return res

    async def _init_database(
            self, dbi: 'progTiroc.db.DBInstance', topics: List[Dict[str, Any]],
            rules: List[Dict[str, Any]]) -> Tuple[ObjectId, ObjectId]:
        """ setup the database """

        with dbi.context() as db_ctx:
            hmRules = dict()
            hmTopic = dict()

            firstTopic = topics[0]['tmpUUID']
            fallbackRule = rules[0]['tmpUUID']

            for topicJson in topics:
                topic = db_ctx.Topic()

                topic.name = topicJson['name']

                await topic.commit()

                hmTopic[topicJson['tmpUUID']] = (topic, topicJson['rules'])

            for ruleJson in rules:
                rule = db_ctx.Rule()
                rule.condition = {
                    "onMsg": ruleJson['condition']['onMsg']
                    if 'onMsg' in ruleJson['condition'] else None,
                    "py": ruleJson['condition']['py']
                }

                onParams = []

                for condition in ruleJson['condition']['onParams']:
                    new_condition = {
                        k: v
                        for k, v in condition.items()
                        if k != 'tmpUUID__type__'
                    }
                    new_condition['__type__'] = hmTopic[
                        condition['tmpUUID__type__']][0].id

                    onParams.append(new_condition)

                rule.condition['onParams'] = onParams

                rule.score = ruleJson['score']
                rule.action = {
                    "text": ruleJson['action']['text'],
                    "immediatlyNext": ruleJson['action']['immediatlyNext'],
                    "isQuestion": ruleJson['action']['isQuestion'],
                }

                operations = []
                for op in ruleJson['action']['operations']:
                    if op['op'] == 'push':
                        op['topic'] = str(hmTopic[op['tmpUUIDtopic']][0].id)
                        del op['tmpUUIDtopic']

                    operations.append(op)

                rule.action.operations = operations
                await rule.commit()

                hmRules[ruleJson['tmpUUID']] = rule

            for k, topic in hmTopic.items():
                topic[0].rules = list(
                    [ObjectId(hmRules[ruleId].id) for ruleId in topic[1]])
                await topic[0].commit()

            return hmTopic[firstTopic][0].id, hmRules[fallbackRule].id

    @staticmethod
    async def get_action(msg: Dict[str, Any], ctx: db.types.Context
                        ) -> Optional[Tuple[int, db.types.Rule, List[int]]]:
        """ Get an action(if possible) -> max_priority used, rule, mapping """
        print(msg)

        params: List[db.types.Params] = sorted(
            ctx.params, key=lambda p: p.priority, reverse=True)

        res: List[Tuple[int, db.types.Rule, List[int]]] = []

        for i in range(len(params)):
            ps = params[:i + 1]

            psTopic = await ps[-1].ofTopic.fetch()

            conditions: List[Tuple[db.types.Rule, Optional[List[int]]]] = [
                (rule,
                 get_mapping(msg, rule.condition['onMsg'], params,
                             rule.condition['onParams'], rule.condition['py']))
                for rule in [ await r.fetch() for r in psTopic.rules]
            ]

            # Condition può restituire un singolo oggetto
            res += [(i + 1, rule, mapping)
                    for (rule, mapping) in conditions
                    if mapping is not None]

        actions = list(
            zip(itertools.accumulate([r[1].score for r in res]), res))

        print(actions)

        if not actions:
            return None
        else:
            selection = actions[bisect.bisect_right([x[0] for x in actions],
                                                    randint(
                                                        0, actions[-1][0] - 1))]

            return selection[1][0], selection[1][1], selection[1][2]

    @staticmethod
    def update_context(db_ctx: db.DBContext, mapping: List[int],
                       action: db.types.Action, options: Dict[str, Any],
                       init_values: Dict[str, Any]) -> db.types.Context:
        """
        Update context given current db context, mapping to use, action,
        options and values to initialize Context(previous values)
        """
        new_ctx = db_ctx.Context(**init_values)

        max_pr = new_ctx.params[-1].priority
        _ = options['_']
        mapping = list(mapping)

        for do in action.operations:

            if do['op'] == 'exportName':
                # Get old param values
                old_param = _[do['index']]

                # Create a new param object
                new_param = db_ctx.Params(
                    ofTopic=old_param.ofTopic,
                    values=old_param.values,
                    startTime=datetime.now(),
                    priority=old_param.priority)

                # Change/add value using eval(no globals only locals)
                new_val = eval(do['val'], {}, options)
                name = eval(do['name'], {}, options)

                if new_val is None:
                    del new_param.values[name]
                else:
                    new_param.values[name] = new_val

                # Sobstitute old Param instance
                _[do['index']] = new_param
                new_ctx.params[mapping[do['index']]] = new_param
            elif do['op'] == 'push':
                max_pr = max_pr - 1
                new_param = db_ctx.Params(
                    ofTopic=do['topic'],
                    values={},
                    startTime=datetime.now(),
                    priority=max_pr)

                new_ctx.params.append(new_param)
                _.append(new_param)
                mapping.append(len(new_ctx.params) - 1)
            elif do['op'] == 'popUntil':
                new_ctx.params = new_ctx.params[:mapping[do['index']] + 1]
            elif do['op'] == 'pop':
                new_ctx.params = new_ctx.params[:-1]
            else:
                print("Operation '{}' not recognized".format(do['op']))

        return new_ctx

    @staticmethod
    async def get_message(db_ctx: db.DBContext, userId: int,
                          msg: Optional[Dict[str, Any]],
                          fallback_rule_id: ObjectId) -> List[db.types.Context]:
        """ Get response message given user's message(already analyzed), userId and db context """

        try:
            old_ctx: db.types.Context = await db_ctx.Context.find_one(
                {
                    'ofUser': ObjectId(userId)
                }, sort=[('timestamp', -1)])

            if old_ctx is None:
                log.error("0 contexts")
                return None

        except mongoengine.DoesNotExist as e:
            log.error(e)
            return None

        ctxs = []
        rule_used = []
        stop = False

        repetitions: int = 0

        while not stop:
            max_priority: int
            rule: db.types.Rule
            mapping: List[int]

            res = await AI.get_action(msg, old_ctx)

            ord_param = sorted(
                old_ctx.params, key=lambda p: p.priority, reverse=True)

            # If no action found stop
            if res is None:
                if msg is not None:
                    fallback_rule = await db_ctx.Rule.find_one({
                        'id': fallback_rule_id
                    })

                    no_und_ctx = db_ctx.Context(
                        ofUser=old_ctx.ofUser,
                        timestamp=datetime.now(),
                        params=ord_param,
                        message=db_ctx.BotMessage(
                            text=fallback_rule.action.text[randint(
                                0,
                                len(fallback_rule.action.text) - 1)],
                            fromRule=fallback_rule.id))
                    ctxs.append(no_und_ctx)

                break

            max_priority, rule, mapping = res

            # If the rule doesn't require another immediate action after stop after this one
            if rule.action.immediatlyNext is False:
                stop = True

            text: str = rule.action.text[randint(0, len(rule.action.text) - 1)]

            ord_param = ord_param[:max_priority + 1]

            _ = [ord_param[mpItem] for mpItem in mapping]

            options = {'_': _, 'm': msg}

            new_ctx: db.types.Context = AI.update_context(
                db_ctx, mapping, rule.action, options,
                dict(
                    ofUser=old_ctx.ofUser,
                    timestamp=datetime.now(),
                    params=ord_param,
                    message=db_ctx.BotMessage(
                        text=text.format(**options), fromRule=rule.id)))

            if str(rule.id) in rule_used:
                repetitions = repetitions + 1

                if repetitions == 5:
                    stop = True
            else:
                ctxs.append(new_ctx)
                old_ctx = new_ctx
                rule_used.append(str(rule.id))

            msg = None

        return ctxs
