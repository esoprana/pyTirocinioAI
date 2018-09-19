from umongo import Document, fields, EmbeddedDocument


class User(Document):
    """
    :ivar str username:
    :ivar uuid googleSessionId
    """

    username = fields.StringField(required=True, null=False)
    googleSessionId = fields.UUIDField(required=True, null=False)

    externallyVisible = ['id', 'username']


class Action(EmbeddedDocument):
    """
    :ivar typing.List[str] text:
    :ivar List[Dict] operations:
    :ivar isQuestion bool:
    :ivar immediatlyNext bool:
    """

    text = fields.ListField(fields.StringField(), required=True, null=False)
    operations = fields.ListField(fields.DictField(), required=False)
    isQuestion = fields.BooleanField(required=True)
    immediatlyNext = fields.BooleanField(required=True)


class Rule(Document):
    """
    :ivar Dict condition:
    :ivar int score:
    :ivar Action action:
    """
    condition = fields.DictField(required=True)
    score = fields.IntField(required=True)
    action = fields.EmbeddedField(Action, required=True)


class Topic(Document):
    """
    :ivar str name:
    :ivar typing.List[Rule] rules:
    """

    name = fields.StringField(required=True)
    rules = fields.ListField(
        fields.ReferenceField(Rule, dbRef=True), required=True)


class Params(EmbeddedDocument):
    """
    :ivar Topic ofTopic:
    :ivar Dict values:
    :ivar datetime startTime:
    :ivar int priority:
    """

    ofTopic = fields.ReferenceField(Topic, dbRef=True, required=True)
    values = fields.DictField(required=False)
    startTime = fields.DateTimeField(required=True)
    priority = fields.IntegerField(required=True)


class Message(EmbeddedDocument):
    """
    :ivar str text:
    """

    text = fields.StringField(required=True)

    class Meta:
        allow_inheritance = True
        abstract = False


class BotMessage(Message):
    """
    :ivar Rule fromRule:
    """
    fromRule = fields.ReferenceField(Rule, dbRef=True, required=True)


class UserMessage(Message):
    """
    :ivar Dict intent:
    :ivar Dict photo:
    :ivar Dict sentiment:
    :ivar Dict googleTopic:
    """

    # All of them can be empty
    intent = fields.DictField(required=False)
    photo = fields.DictField(required=False)
    sentiment = fields.DictField(required=False)
    googleTopic = fields.DictField(required=False)


class WozBotMessage(Message):
    """
    """


class WozUserMessage(Message):
    """
    """


class Context(Document):
    """
    :ivar User ofUser:
    :ivar datetime timestamp:
    :ivar typing.List[Params] params:
    :ivar Message message:
    """
    ofUser = fields.ReferenceField(User, dbRef=True, required=True)
    timestamp = fields.DateTimeField(required=True)
    params = fields.ListField(fields.EmbeddedField(Params))
    message = fields.EmbeddedField(Message)
