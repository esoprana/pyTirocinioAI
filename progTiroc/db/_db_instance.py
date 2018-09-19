from uuid import uuid4

from . import _db as types

from umongo import Instance
import mongomock
import motor.motor_asyncio


class DBContext:
    """
    :ivar a User: user orm
    :type User: mongoengine.base.metaclasses.TopLevelDocumentMetaclass:
    :ivar Context: mongoengine.base.metaclasses.TopLevelDocumentMetaclass:
    :ivar Rule: mongoengine.base.metaclasses.TopLevelDocumentMetaclass:
    :ivar Topic: mongoengine.base.metaclasses.TopLevelDocumentMetaclass:

    :ivar Action: mongoengine.base.metaclasses.DocumentMetaclass:
    :ivar Message: mongoengine.base.metaclasses.DocumentMetaclass:
    :ivar Params: mongoengine.base.metaclasses.DocumentMetaclass:
    :ivar UserMessage: mongoengine.base.metaclasses.DocumentMetaclass:
    :ivar BotMessage: mongoengine.base.metaclasses.DocumentMetaclass:
    :ivar WozBotMessage: mongoengine.base.metaclasses.DocumentMetaclass:
    """

    def __init__(self, instance):
        self._instance = instance

        #self._user_context = mongoengine.context_managers.switch_db(
        #    types.User, db_alias)
        #self._context_context = mongoengine.context_managers.switch_db(
        #    types.Context, db_alias)
        #self._rule_context = mongoengine.context_managers.switch_db(
        #    types.Rule, db_alias)
        #self._topic_context = mongoengine.context_managers.switch_db(
        #    types.Topic, db_alias)
        pass

    def __enter__(self) -> 'progTiroc.db.DBContext':
        return self._instance
        #self.User: mongoengine.base.metaclasses.TopLevelDocumentMetaclass = self._user_context.__enter__(
        #)
        #self.Context: mongoengine.base.metaclasses.TopLevelDocumentMetaclass = self._context_context.__enter__(
        #)
        #self.Rule: mongoengine.base.metaclasses.TopLevelDocumentMetaclass = self._rule_context.__enter__(
        #)
        #self.Topic: mongoengine.base.metaclasses.TopLevelDocumentMetaclass = self._topic_context.__enter__(
        #)

        #self.Action = types.Action  # type: mongoengine.base.metaclasses.DocumentMetaclass
        #self.Message = types.Message  # type: mongoengine.base.metaclasses.DocumentMetaclass
        #self.Params = types.Params  # type: mongoengine.base.metaclasses.DocumentMetaclass
        #self.UserMessage = types.UserMessage  # type: mongoengine.base.metaclasses.DocumentMetaclass
        #self.BotMessage = types.BotMessage  # type: mongoengine.base.metaclasses.DocumentMetaclass
        #self.WozBotMessage = types.WozUserMessage  # type: mongoengine.base.metaclasses.DocumentMetaclass

        return self

    def __exit__(self, type, value, traceback):
        #self._user_context.__exit__(type, value, traceback)
        #self._context_context.__exit__(type, value, traceback)
        #self._rule_context.__exit__(type, value, traceback)
        #self._topic_context.__exit__(type, value, traceback)

        #self.Action = None
        #self.Message = None
        #self.Params = None
        #self.UserMessage = None
        #self.BotMessage = None
        #self.WozBotMessage = None
        #self.User = None
        #self.Context = None
        #self.Rule = None
        #self.Topic = None
        pass


class DBInstance:

    def __init__(self,
                 database_name: str,
                 database_host: str,
                 database_port: int,
                 database_user: str,
                 database_pwd: str,
                 isMock: bool = False):
        if (database_port >= 65535):
            raise Exception('Enviroment variable DBPORT is non valid port')

        self._db_name: str = database_name
        self._db_alias: str = 'MONGOENGINE_ALIAS_PYTIROCINIO_' + str(uuid4())

        if database_host.find('mongodb://') == -1:
            database_host = 'mongodb://' + database_host

        if isMock is True:
            print('dsa')
            import mongomock
            self._connection = mongomock.MongoClient(
                db=database_name, host=database_host, port=database_port)
        else:
            DBUSER = "pheirei6choh0uephaug9Rooz0kooYungaeThaing2SheoBehoaG0xie4quie6Lu"
            DBPSWD = "pev4yieyae8xeiP4AeLap6sain5fohsh1aheebie7eu4Aequiefo8aeSi9shiQu8"

            self._connection = motor.motor_asyncio.AsyncIOMotorClient(
                'mongodb://{DBUSER}:{DBPSWD}@localhost:27017/db'.format(
                    DBUSER=DBUSER, DBPSWD=DBPSWD))

        self._instance = Instance(self._connection['db'])
        self._instance.register(types.User)
        self._instance.register(types.Action)
        self._instance.register(types.Rule)
        self._instance.register(types.Topic)
        self._instance.register(types.Params)
        self._instance.register(types.Message)
        self._instance.register(types.UserMessage)
        self._instance.register(types.BotMessage)
        self._instance.register(types.WozUserMessage)
        self._instance.register(types.Context)

    def context(self) -> DBContext:
        return DBContext(self._instance)

    def drop_db(self):
        self._connection.drop_database(self._db_name)
        self._connection.close()


#mongomock.MongoClient(host='mongodb://localhost:27017/db')
