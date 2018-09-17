import mongoengine
from uuid import uuid4

from . import _db as types


class DBContext:
    """
    :ivar a User: user orm
    :type User: mongoengine.base.metaclasses.TopLevelDocumentMetaclass
    :ivar Context: mongoengine.base.metaclasses.TopLevelDocumentMetaclass
    :ivar Rule: mongoengine.base.metaclasses.TopLevelDocumentMetaclass
    :ivar Topic: mongoengine.base.metaclasses.TopLevelDocumentMetaclass

    :ivar mongoengine.base.metaclasses.DocumentMetaclass Action:
    :ivar mongoengine.base.metaclasses.DocumentMetaclass Message:
    :ivar mongoengine.base.metaclasses.DocumentMetaclass Params:
    :ivar mongoengine.base.metaclasses.DocumentMetaclass UserMessage:
    :ivar mongoengine.base.metaclasses.DocumentMetaclass BotMessage:
    :ivar mongoengine.base.metaclasses.DocumentMetaclass WozBotMessage:
    """

    def __init__(self, db_alias):

        self._user_context = mongoengine.context_managers.switch_db(
            types.User, db_alias)
        self._context_context = mongoengine.context_managers.switch_db(
            types.Context, db_alias)
        self._rule_context = mongoengine.context_managers.switch_db(
            types.Rule, db_alias)
        self._topic_context = mongoengine.context_managers.switch_db(
            types.Topic, db_alias)

    def __enter__(self) -> 'progTiroc.db.DBContext':
        self.User: mongoengine.base.metaclasses.TopLevelDocumentMetaclass = self._user_context.__enter__(
        )
        self.Context: mongoengine.base.metaclasses.TopLevelDocumentMetaclass = self._context_context.__enter__(
        )
        self.Rule: mongoengine.base.metaclasses.TopLevelDocumentMetaclass = self._rule_context.__enter__(
        )
        self.Topic: mongoengine.base.metaclasses.TopLevelDocumentMetaclass = self._topic_context.__enter__(
        )

        self.Action = types.Action  # type: mongoengine.base.metaclasses.DocumentMetaclass
        self.Message = types.Message  # type: mongoengine.base.metaclasses.DocumentMetaclass
        self.Params = types.Params  # type: mongoengine.base.metaclasses.DocumentMetaclass
        self.UserMessage = types.UserMessage  # type: mongoengine.base.metaclasses.DocumentMetaclass
        self.BotMessage = types.BotMessage  # type: mongoengine.base.metaclasses.DocumentMetaclass
        self.WozBotMessage = types.WozUserMessage  # type: mongoengine.base.metaclasses.DocumentMetaclass

        return self

    def __exit__(self, type, value, traceback):
        self._user_context.__exit__(type, value, traceback)
        self._context_context.__exit__(type, value, traceback)
        self._rule_context.__exit__(type, value, traceback)
        self._topic_context.__exit__(type, value, traceback)

        self.Action = None
        self.Message = None
        self.Params = None
        self.UserMessage = None
        self.BotMessage = None
        self.WozBotMessage = None
        self.User = None
        self.Context = None
        self.Rule = None
        self.Topic = None


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
            self._connection = mongoengine.connect(
                database_name,
                alias=self._db_alias,
                host=database_host.replace('mongodb', 'mongomock'),
                port=database_port)
        else:
            self._connection = mongoengine.connect(
                database_name,
                alias=self._db_alias,
                host=database_host,
                port=database_port,
                username=database_user,
                password=database_pwd)

    def context(self) -> DBContext:
        return DBContext(self._db_alias)

    def drop_db(self):
        self._connection.drop_database(self._db_name)
        self._connection.close()


mongoengine.connect('db', alias='default', host='mongomock://localhost')
