# Standard libs
import typing
from collections import namedtuple

# 3rd party libs
from umongo import (
    Instance,
    document  # Used for MetaDocumentImplementation
)
import motor.motor_asyncio

import marshmallow

# Custom libs
from . import _db as types


class DBContext:
    """
    :ivar document.MetaDocumentImplementation User: User odm
    :ivar document.MetaDocumentImplementation Context: Context odm
    :ivar document.MetaDocumentImplementation Rule: Rule odm
    :ivar document.MetaDocumentImplementation Topic: Topic odm
    :ivar document.MetaDocumentImplementation Action: Action odm
    :ivar document.MetaDocumentImplementation Message: Message odm
    :ivar document.MetaDocumentImplementation Params: Params odm
    :ivar document.MetaDocumentImplementation UserMessage: UserMessage odm
    :ivar document.MetaDocumentImplementation BotMessage: BotMessage odm
    :ivar document.MetaDocumentImplementation WozBotMessage: WozBotMessage odm
    """

    def __init__(self, instance: 'DBInstance'):
        self._instance = instance

    def __enter__(self):
        self.User: document.MetaDocumentImplementation = self._instance.User
        self.Context: document.MetaDocumentImplementation = self._instance.Context
        self.Rule: document.MetaDocumentImplementation = self._instance.Rule
        self.Topic: document.MetaDocumentImplementation = self._instance.Topic
        self.Action: document.MetaDocumentImplementation = self._instance.Action
        self.Message: document.MetaDocumentImplementation = self._instance.Message
        self.Params: document.MetaDocumentImplementation = self._instance.Params
        self.UserMessage: document.MetaDocumentImplementation = self._instance.UserMessage
        self.BotMessage: document.MetaDocumentImplementation = self._instance.BotMessage
        self.WozBotMessage: document.MetaDocumentImplementation = self._instance.WozBotMessage

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

    load_or_dump = load.union(dump)

    return MetaFields(
        fields=tuple(load_or_dump),
        load_only=tuple(load_or_dump.difference(dump)),
        dump_only=tuple(load_or_dump.difference(load)),
        load=load,
        dump=dump)


class DBInstance:
    """
    Rapresents an instance of the database and its rapresentations(User, Message, ...)

    :ivar marshmallow.Schema user_schema: marshmallow web schema for User
    :ivar marshmallow.Schema message_schema: marshmallow web schema for Message
    """

    def __init__(self,
                 database_name: str,
                 database_host: str,
                 database_port: int,
                 database_user: str,
                 database_pwd: str,
                 loop=None):
        if database_port >= 65535:
            raise Exception('Enviroment variable DBPORT is non valid port')

        self._db_name: str = database_name

        uri: str = 'mongodb://{DBUSER}:{DBPSWD}@{DBHOST}:{DBPORT}/{DBNAME}'.format(
            DBUSER=database_user,
            DBPSWD=database_pwd,
            DBHOST=database_host,
            DBPORT=database_port,
            DBNAME=database_name)
        self._connection = motor.motor_asyncio.AsyncIOMotorClient(
            uri, io_loop=loop)
        self._instance = Instance(self._connection[database_name])

        for odm_model in [
                types.User, types.Action, types.Rule, types.Topic, types.Params,
                types.Message, types.UserMessage, types.BotMessage,
                types.WozUserMessage, types.WozBotMessage, types.Context
        ]:
            self._instance.register(odm_model)

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

    async def drop_db(self):
        await self._connection.drop_database(self._db_name)
        self._connection.close()
