import datetime
import uuid

import pytest
import mock

from mongoengine.base import BaseDocument

from progTiroc import ai
from progTiroc import db


@pytest.fixture
def patch_datetime_now(monkeypatch):

    class MockedDatetime(datetime.datetime):
        FAKE_TIME = datetime.datetime(2000, 12, 25, 17, 5, 55)

        @classmethod
        def now(cls):
            return MockedDatetime.FAKE_TIME

    with mock.patch('datetime.datetime', MockedDatetime), mock.patch(
            'progTiroc.ai._main.datetime', MockedDatetime):
        yield


def remove_id(a):
    if isinstance(a, BaseDocument):
        return list([(k, remove_id(v))
                     for (k, v) in a.to_mongo().items().copy()
                     if k != '_id'])
    else:
        return a


@pytest.fixture(scope='function')
def db_ctx():
    # Use mongomock instead of real mongo
    dbi = db.DBInstance('db', 'localhost', 27017, 'user', 'pwd', True)
    with dbi.context() as db_ctx:
        yield db_ctx

    dbi.drop_db()


def test_connection(db_ctx):
    assert db_ctx


async def test_user_save(db_ctx):
    user = db_ctx.User(googleSessionId=uuid.uuid4(), username='username')
    await user.commit()


async def test_mongomock_clean(db_ctx):
    assert not [i async for i in db_ctx.User.find().limit(1)]


@pytest.mark.usefixtures('patch_datetime_now')
def test_now():
    assert datetime.datetime.now() == datetime.datetime.FAKE_TIME


async def gen_standard(
        db_ctx
) -> (db.types.User, db.types.Topic, db.types.Rule, db.types.Params):
    user = db_ctx.User(googleSessionId=uuid.uuid4(), username='username')
    await user.commit()

    action = db_ctx.Action(
        text=['dsaa', 'dsab'],
        operations=[{
            'op': 'push'
        }],
        isQuestion=False,
        immediatlyNext=False)

    rule = db_ctx.Rule(condition={'a__eq': 1}, score=3, action=action)
    await rule.commit()

    print("QQQQQQQQQQQQQQQQQQ" + str(type(rule.id)) + "WWWWWWWWWWWWWWWWWWWWWW")
    topic = db_ctx.Topic(name='dsa', rules=[rule.id])
    await topic.commit()

    action.operations[0]['topic'] = str(topic.id)
    await rule.commit()

    firstParam = db_ctx.Params(
        ofTopic=topic,
        values={'ada': 'dsa'},
        startTime=datetime.datetime(1999, 1, 1, 1, 1, 1, 1),
        priority=1)

    return user, topic, rule, firstParam


@pytest.mark.usefixtures('patch_datetime_now')
async def test_update(db_ctx):
    # Prepare
    user, topic, rule, firstParam = await gen_standard(db_ctx)

    # True test
    new_ctx = ai.AI.update_context(db_ctx, [1], rule.action, {
        '_': [],
        'm': {}
    }, {
        'ofUser': user,
        'params': [firstParam],
        'timestamp': datetime.datetime.now(),
        'message': db_ctx.Message(text='aaa')
    })
    await new_ctx.commit()

    test_ctx = db_ctx.Context(
        ofUser=user.id,
        timestamp=datetime.datetime.now(),
        params=[
            firstParam,
            db_ctx.Params(
                ofTopic=topic,
                values={},
                startTime=datetime.datetime.now(),
                priority=0)
        ],
        message=db_ctx.Message(text='aaa'))

    await test_ctx.commit()
    assert remove_id(test_ctx) == remove_id(new_ctx)


@pytest.mark.usefixtures('patch_datetime_now')
async def test_update2(db_ctx):
    # Prepare
    action2 = db_ctx.Action(
        text=['dsaa', 'dsab'],
        operations=[{
            'op': 'exportName',
            'index': 0,
            'val': str(1),
            'name': 'test'
        }],
        isQuestion=False,
        immediatlyNext=False)

    rule2 = db_ctx.Rule(condition={'a__eq': 1}, score=3, action=action2)
    await rule2.commit()

    user, topic, rule, firstParam = await gen_standard(db_ctx)

    old_ctx = db_ctx.Context(
        ofUser=user.id,
        timestamp=datetime.datetime.now(),
        params=[
            firstParam,
            db_ctx.Params(
                ofTopic=topic,
                values={},
                startTime=datetime.datetime.now(),
                priority=0)
        ],
        message=db_ctx.Message(text='aaa'))
    await old_ctx.commit()

    datetime.datetime.FAKE_TIME = datetime.datetime(2001, 1, 1)

    new_ctx = ai.AI.update_context(db_ctx, [1], rule2.action, {
        '_': [old_ctx.params[1]],
        'm': {}
    }, {
        'ofUser': user,
        'params': old_ctx.params,
        'timestamp': datetime.datetime.now(),
        'message': db_ctx.Message(text='aaa')
    })
    await new_ctx.commit()

    old_ctx.params[1].values['test'] = 1
    old_ctx.params[1].startTime = datetime.datetime.now()
    old_ctx.timestamp = datetime.datetime.now()
    await old_ctx.commit()

    assert remove_id(old_ctx) == remove_id(new_ctx)


@pytest.mark.usefixtures('patch_datetime_now')
async def test_update3(db_ctx):
    action3 = db_ctx.Action(
        text=['dsaa', 'dsab'],
        operations=[{
            'op': 'exportName',
            'index': 0,
            'val': '_[0].values[\'test\']+1',
            'name': 'test'
        }],
        isQuestion=False,
        immediatlyNext=False)

    rule3 = db_ctx.Rule(condition={'a__eq': 1}, score=3, action=action3)
    await rule3.commit()

    user, topic, rule, firstParam = await gen_standard(db_ctx)

    old_ctx = db_ctx.Context(
        ofUser=user.id,
        timestamp=datetime.datetime.now(),
        params=[
            firstParam,
            db_ctx.Params(
                ofTopic=topic,
                values={'test': 1},
                startTime=datetime.datetime.now(),
                priority=0)
        ],
        message=db_ctx.Message(text='aaa'))
    await old_ctx.commit()

    datetime.datetime.FAKE_TIME = datetime.datetime(2041, 1, 1)

    new_ctx = ai.AI.update_context(db_ctx, [1], rule3.action, {
        '_': [old_ctx.params[1]],
        'm': {}
    }, {
        'ofUser': user,
        'params': old_ctx.params,
        'timestamp': datetime.datetime.now(),
        'message': db_ctx.Message(text='aaa')
    })

    await new_ctx.commit()

    old_ctx.params[1].values['test'] = 2
    old_ctx.params[1].startTime = datetime.datetime.now()
    old_ctx.timestamp = datetime.datetime.now()
    await old_ctx.commit()

    assert remove_id(old_ctx) == remove_id(new_ctx)


@pytest.mark.usefixtures('patch_datetime_now')
async def test_update4(db_ctx):
    action4 = db_ctx.Action(
        text=['dsaa', 'dsab'],
        operations=[{
            'op': 'exportName',
            'index': 0,
            'val': 'None',
            'name': 'test'
        }],
        isQuestion=False,
        immediatlyNext=False)

    rule4 = db_ctx.Rule(condition={'a__eq': 1}, score=3, action=action4)
    await rule4.commit()

    user, topic, rule, firstParam = gen_standard(db_ctx)

    old_ctx = db_ctx.Context(
        ofUser=user.id,
        timestamp=datetime.datetime.now(),
        params=[
            firstParam,
            db_ctx.Params(
                ofTopic=topic,
                values={'test': 2},
                startTime=datetime.datetime.now(),
                priority=0)
        ],
        message=db_ctx.Message(text='aaa'))
    await old_ctx.commit()

    datetime.datetime.FAKE_TIME = datetime.datetime(2045, 1, 1)

    new_ctx = ai.AI.update_context(db_ctx, [1], rule4.action, {
        '_': [old_ctx.params[1]],
        'm': {}
    }, {
        'ofUser': user,
        'params': old_ctx.params,
        'timestamp': datetime.datetime.now(),
        'message': db_ctx.Message(text='aaa')
    })

    await new_ctx.commit()

    del old_ctx.params[1].values['test']
    old_ctx.params[1].startTime = datetime.datetime.now()
    old_ctx.timestamp = datetime.datetime.now()
    await old_ctx.commit()

    assert remove_id(old_ctx) == remove_id(new_ctx)


@pytest.mark.usefixtures('patch_datetime_now')
async def test_update5(db_ctx):
    action5 = db_ctx.Action(
        text=['dsaa', 'dsab'],
        operations=[{
            'op': 'popUntil',
            'index': 1,
        }],
        isQuestion=False,
        immediatlyNext=False)

    rule5 = db_ctx.Rule(condition={'a__eq': 1}, score=3, action=action5)
    await rule5.commit()

    user, topic, rule, firstParam = await gen_standard(db_ctx)

    old_ctx = db_ctx.Context(
        ofUser=user.id,
        timestamp=datetime.datetime.now(),
        params=[
            firstParam,
            db_ctx.Params(
                ofTopic=topic,
                values={'test': 2},
                startTime=datetime.datetime.now(),
                priority=0),
            db_ctx.Params(
                ofTopic=topic,
                values={'test': 5},
                startTime=datetime.datetime.now(),
                priority=-1),
            db_ctx.Params(
                ofTopic=topic,
                values={'test': 95},
                startTime=datetime.datetime.now(),
                priority=-2),
            db_ctx.Params(
                ofTopic=topic,
                values={'test': 25},
                startTime=datetime.datetime.now(),
                priority=-3)
        ],
        message=db_ctx.Message(text='aaa'))
    await old_ctx.commit()

    datetime.datetime.FAKE_TIME = datetime.datetime(2045, 1, 1)

    mapp = [0, 1, 3]

    new_ctx = ai.AI.update_context(db_ctx, mapp, rule5.action, {
        '_': [old_ctx.params[i] for i in mapp],
        'm': {}
    }, {
        'ofUser': user,
        'params': old_ctx.params,
        'timestamp': datetime.datetime.now(),
        'message': db_ctx.Message(text='aaa')
    })

    await new_ctx.commit()

    old_ctx.params = [old_ctx.params[0], old_ctx.params[1]]
    old_ctx.timestamp = datetime.datetime.now()
    await old_ctx.commit()

    assert remove_id(old_ctx) == remove_id(new_ctx)


@pytest.mark.usefixtures('patch_datetime_now')
async def test_update6(db_ctx):
    action5 = db_ctx.Action(
        text=['dsaa', 'dsab'],
        operations=[{
            'op': 'pop',
        }],
        isQuestion=False,
        immediatlyNext=False)

    rule5 = db_ctx.Rule(condition={'a__eq': 1}, score=3, action=action5)
    await rule5.commit()

    user, topic, rule, firstParam = await gen_standard(db_ctx)

    old_ctx = db_ctx.Context(
        ofUser=user.id,
        timestamp=datetime.datetime.now(),
        params=[
            firstParam,
            db_ctx.Params(
                ofTopic=topic,
                values={'test': 2},
                startTime=datetime.datetime.now(),
                priority=0),
            db_ctx.Params(
                ofTopic=topic,
                values={'test': 5},
                startTime=datetime.datetime.now(),
                priority=-1),
            db_ctx.Params(
                ofTopic=topic,
                values={'test': 95},
                startTime=datetime.datetime.now(),
                priority=-2),
            db_ctx.Params(
                ofTopic=topic,
                values={'test': 25},
                startTime=datetime.datetime.now(),
                priority=-3)
        ],
        message=db_ctx.Message(text='aaa'))
    await old_ctx.commit()

    datetime.datetime.FAKE_TIME = datetime.datetime(2045, 1, 1)

    mapp = [0, 1, 3]

    new_ctx = ai.AI.update_context(db_ctx, mapp, rule5.action, {
        '_': [old_ctx.params[i] for i in mapp],
        'm': {}
    }, {
        'ofUser': user,
        'params': old_ctx.params,
        'timestamp': datetime.datetime.now(),
        'message': db_ctx.Message(text='aaa')
    })

    await new_ctx.commit()

    old_ctx.params = old_ctx.params[:-1]
    old_ctx.timestamp = datetime.datetime.now()
    await old_ctx.commit()

    assert remove_id(old_ctx) == remove_id(new_ctx)
