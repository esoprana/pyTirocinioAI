from uuid import uuid4

from . import _db as types

from umongo import Instance
import motor.motor_asyncio

import mongomock  # Used for MongoClient
import umongo.document  # Used for MetaDocumentImplementation

import typing


class DBContext:
    """
    :ivar User: umongo.document.MetaDocumentImplementation: User odm
    :ivar Context: umongo.document.MetaDocumentImplementation: Context odm
    :ivar Rule: umongo.document.MetaDocumentImplementation: Rule odm
    :ivar Topic: umongo.document.MetaDocumentImplementation: Topic odm
    :ivar Action: umongo.document.MetaDocumentImplementation: Action odm
    :ivar Message: umongo.document.MetaDocumentImplementation: Message odm
    :ivar Params: umongo.document.MetaDocumentImplementation: Params odm
    :ivar UserMessage: umongo.document.MetaDocumentImplementation: UserMessage odm
    :ivar BotMessage: umongo.document.MetaDocumentImplementation: BotMessage odm
    :ivar WozBotMessage: umongo.document.MetaDocumentImplementation: WozBotMessage odm
    """

    def __init__(self, instance: 'progTiroc.db.DBInstance'):
        self._instance = instance

    def __enter__(self):
        self.User: umongo.document.MetaDocumentImplementation = self._instance.User
        self.Context: umongo.document.MetaDocumentImplementation = self._instance.Context
        self.Rule: umongo.document.MetaDocumentImplementation = self._instance.Rule
        self.Topic: umongo.document.MetaDocumentImplementation = self._instance.Topic
        self.Action: umongo.document.MetaDocumentImplementation = self._instance.Action
        self.Message: umongo.document.MetaDocumentImplementation = self._instance.Message
        self.Params: umongo.document.MetaDocumentImplementation = self._instance.Params
        self.UserMessage: umongo.document.MetaDocumentImplementation = self._instance.UserMessage
        self.BotMessage: umongo.document.MetaDocumentImplementation = self._instance.BotMessage
        self.WozBotMessage: umongo.document.MetaDocumentImplementation = self._instance.WozBotMessage

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.User = None
        self.Context = None
        self.Rule = None
        self.Topic = None
        self.Action = None
        self.Message = None
        self.Params = None
        self.UserMessage = None
        self.BotMessage = None
        self.WozBotMessage = None


class WebSchema:

    def __init__(self,
                 cls: umongo.document.MetaDocumentImplementation,
                 load_only: typing.Iterable[str] = None,
                 dump_only: typing.Iterable[str] = None):

        if load_only is None:
            load_only = cls.__load_only__

        if load_only is None:
            raise Exception('load_only or cls.__load_only__ must be not null')

        if dump_only is None:
            dump_only = cls.__dump_only__

        if dump_only is None:
            raise Exception('dump_only or cls.__dump_only__ must be not null')

        user_schema = cls.schema.as_marshmallow_schema()

        class DumpSchema(user_schema):

            class Meta:
                fields = dump_only

        class LoadSchema(user_schema):

            class Meta:
                fields = load_only

        self._cls_out = DumpSchema()
        self._cls_in = LoadSchema()

    def load(self, *args, **kwargs) -> dict:
        return self._cls_in.load(*args, **kwargs)

    def dump(self, *args, **kwargs) -> dict:
        return self._cls_out.dump(*args, **kwargs)


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
        self._instance.register(types.WozBotMessage)
        self._instance.register(types.Context)

        self.user_schema = WebSchema(self._instance.User)

    def context(self) -> DBContext:
        return DBContext(self._instance)

    def drop_db(self):
        self._connection.drop_database(self._db_name)
        self._connection.close()
