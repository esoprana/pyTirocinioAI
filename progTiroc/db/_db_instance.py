# Standard libs
import typing
from collections import namedtuple

# 3rd party libs
from umongo import Instance
import motor.motor_asyncio

import mongomock  # Used for MongoClient
import umongo.document  # Used for MetaDocumentImplementation

import marshmallow

# Custom libs
from . import _db as types


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


MetaFields = namedtuple('MetaFields',
                        ['fields', 'load_only', 'dump_only', 'load', 'dump'])


def get_meta_fields(load: typing.Iterable[str], dump: typing.Iterable[str]):
    load = set(load)
    dump = set(dump)

    un = load.union(dump)

    return MetaFields(
        fields=tuple(un),
        load_only=tuple(un.difference(dump)),
        dump_only=tuple(un.difference(load)),
        load=load,
        dump=dump)


class DBInstance:
    """
    Rapresents an instance of the database and its rapresentations(User, Message, ...)

    :ivar user_schema: marshmallow.Schema: marshmallow web schema for User
    :ivar message_schema: marshmallow.Schema: marshmallow web schema for Message
    """

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

        if database_host.find('mongodb://') == -1:
            database_host = 'mongodb://' + database_host

        if isMock is True:
            self._connection = mongomock.MongoClient(
                db=database_name, host=database_host, port=database_port)
        else:
            self._connection = motor.motor_asyncio.AsyncIOMotorClient(
                'mongodb://{DBUSER}:{DBPSWD}@{DBHOST}:{DBPORT}/{DBNAME}'.format(
                    DBUSER=database_name,
                    DBPSWD=database_pwd,
                    DBHOST=database_host,
                    DBPORT=database_port,
                    DBNAME=database_name))

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

        user_meta = get_meta_fields(load=('username',), dump=('id', 'username'))

        message_meta = get_meta_fields(
            load=('text',), dump=('id', 'text', 'timestamp'))

        class UserWebSchema(self._instance.User.schema.as_marshmallow_schema()):
            __mongoload__ = user_meta.load
            __mongodump__ = user_meta.dump

            class Meta:
                fields = user_meta.fields
                load_only = user_meta.load_only
                dump_only = user_meta.dump_only

        class MessageWebSchema(
                self._instance.Context.schema.as_marshmallow_schema()):
            __mongoload__ = message_meta.load
            __mongodump__ = ('id', 'message.text', 'timestamp')

            text = marshmallow.fields.Method('_get_text')

            def _get_text(self, obj):
                return obj.message.text

            class Meta:
                fields = message_meta.fields
                load_only = message_meta.load_only
                dump_only = message_meta.dump_only

        self.user_schema = UserWebSchema()
        self.message_schema = MessageWebSchema()

    def context(self) -> DBContext:
        return DBContext(self._instance)

    def drop_db(self):
        self._connection.drop_database(self._db_name)
        self._connection.close()
