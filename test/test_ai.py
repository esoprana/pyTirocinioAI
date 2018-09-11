import progTiroc.ai as ai
import progTiroc.db as db
from datetime import datetime
import uuid

from mongoengine import EmbeddedDocument


def remove_id(a):
    r = a.to_mongo().items().copy()

    if isinstance(a, EmbeddedDocument):
        return list([(k, remove_id) for (k, v) in r if k != '_id'])
    else:
        return r


# Prepare
user = db.User(googleSessionId=uuid.uuid4(), username='username')
user.save()

action = db.Action(
    text=['dsaa', 'dsab'],
    operations=[{
        'op': 'push'
    }],
    isQuestion=False,
    immediatlyNext=False)

rule = db.Rule(condition={'a__eq': 1}, score=3, action=action)
rule.save()

topic = db.Topic(name='dsa', rules=[rule])
topic.save()

action.operations[0]['topic'] = str(topic.id)
rule.save()

action2 = db.Action(
    text=['dsaa', 'dsab'],
    operations=[{
        'op': 'exportName',
        'index': 0,
        'val': str(1),
        'name': 'swag'
    }],
    isQuestion=False,
    immediatlyNext=False)

rule2 = db.Rule(condition={'a__eq': 1}, score=3, action=action2)
rule2.save()

action3 = db.Action(
    text=['dsaa', 'dsab'],
    operations=[{
        'op': 'exportName',
        'index': 0,
        'val': '_[0].values[\'swag\']+1',
        'name': 'swag'
    }],
    isQuestion=False,
    immediatlyNext=False)

rule3 = db.Rule(condition={'a__eq': 1}, score=3, action=action3)
rule3.save()

action4 = db.Action(
    text=['dsaa', 'dsab'],
    operations=[{
        'op': 'exportName',
        'index': 0,
        'val': 'None',
        'name': 'swag'
    }],
    isQuestion=False,
    immediatlyNext=False)

rule4 = db.Rule(condition={'a__eq': 1}, score=3, action=action4)
rule4.save()

firstParam = db.Params(
    ofTopic=topic,
    values={'ada': 'dsa'},
    startTime=datetime(1999, 1, 1, 1, 1, 1, 1),
    priority=1)

# True test
new_ctx = ai.AI.update_context([1, 3, 4], rule.action, {
    '_': [],
    'm': {}
}, {
    'ofUser': user,
    'params': [firstParam],
    'timestamp': datetime(2000, 1, 1, 1, 1, 1, 1),
    'message': db.Message(text='aaa')
})

test_ctx = db.Context(
    ofUser=user,
    timestamp=datetime(2000, 1, 1, 1, 1, 1, 1),
    params=[
        firstParam,
        db.Params(
            ofTopic=topic,
            values={},
            startTime=new_ctx.params[1].startTime,
            priority=0)
    ],
    message=db.Message(text='aaa'))

new2_ctx = ai.AI.update_context([1, 3, 4], rule2.action, {
    '_': [new_ctx.params[1]],
    'm': {}
}, {
    'ofUser': user,
    'params': new_ctx.params,
    'timestamp': datetime(2001, 1, 1, 1, 1, 1, 1),
    'message': db.Message(text='bbb')
})

new3_ctx = ai.AI.update_context([1, 3, 4], rule3.action, {
    '_': [new2_ctx.params[1]],
    'm': {}
}, {
    'ofUser': user,
    'params': new2_ctx.params,
    'timestamp': datetime(2001, 1, 1, 1, 1, 1, 1),
    'message': db.Message(text='ccc')
})

new4_ctx = ai.AI.update_context([1, 3, 4], rule4.action, {
    '_': [new3_ctx.params[1]],
    'm': {}
}, {
    'ofUser': user,
    'params': new3_ctx.params,
    'timestamp': datetime(2001, 1, 1, 1, 1, 1, 1),
    'message': db.Message(text='ddd')
})
