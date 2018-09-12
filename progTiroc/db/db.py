import mongoengine


def mock_connect():
    return mongoengine.connect('db', host='mongomock://localhost')


def connect(database_host: str, database_port: int, database_name: str,
            database_user: str, database_pwd: str):
    if (database_port >= 65535):
        raise Exception('Enviroment variable DBPORT is non valid port')

    try:
        return mongoengine.connect(
            database_name,
            host=database_host,
            port=database_port,
            username=database_user,
            password=database_pwd)
    except Exception as ex:
        pass


class User(mongoengine.Document):
    """
    :ivar str username:
    :ivar uuid googleSessionId
    """

    username = mongoengine.StringField(required=True, null=False)
    googleSessionId = mongoengine.UUIDField(required=True, null=False)

    externallyVisible = ['id', 'username']


class Action(mongoengine.EmbeddedDocument):
    """
    :ivar typing.List[str] text:
    :ivar List[Dict] operations:
    :ivar isQuestion bool:
    :ivar immediatlyNext bool:
    """

    text = mongoengine.ListField(
        mongoengine.StringField(), required=True, null=False)
    operations = mongoengine.ListField(mongoengine.DictField(), required=False)
    isQuestion = mongoengine.BooleanField(required=True, null=False)
    immediatlyNext = mongoengine.BooleanField(required=True, null=False)


class Rule(mongoengine.Document):
    """
    :ivar Dict condition:
    :ivar int score:
    :ivar Action action:
    """
    condition = mongoengine.DictField(required=True, null=False)
    score = mongoengine.IntField(required=True, null=False)
    action = mongoengine.EmbeddedDocumentField(
        Action, required=True, null=False)


class Topic(mongoengine.Document):
    """
    :ivar str name:
    :ivar typing.List[Rule] rules:
    """

    name = mongoengine.StringField(required=True, null=False)
    rules = mongoengine.ListField(
        mongoengine.ReferenceField(Rule), required=True, null=False)


class Params(mongoengine.EmbeddedDocument):
    """
    :ivar Topic ofTopic:
    :ivar Dict values:
    :ivar datetime startTime:
    :ivar int priority:
    """

    ofTopic = mongoengine.ReferenceField(Topic, required=True, null=False)
    values = mongoengine.DictField(
        required=False, default=dict)  # TODO: Ricontrollare
    startTime = mongoengine.DateTimeField(required=True, null=False)
    priority = mongoengine.IntField(required=True, null=False)


class Message(mongoengine.EmbeddedDocument):
    """
    :ivar str text:
    """

    text = mongoengine.StringField(required=True, null=False)
    meta = {'allow_inheritance': True}


class BotMessage(Message):
    """
    :ivar Rule fromRule:
    """
    fromRule = mongoengine.ReferenceField(Rule, required=True, null=False)


class UserMessage(Message):
    """
    :ivar Dict intent:
    :ivar Dict photo:
    :ivar Dict sentiment:
    :ivar Dict googleTopic:
    """

    # All of them can be empty
    intent = mongoengine.DictField(required=False)
    photo = mongoengine.DictField(required=False)
    sentiment = mongoengine.DictField(required=False)
    googleTopic = mongoengine.DictField(required=False)


class WozBotMessage(Message):
    """
    """


class WozUserMessage(Message):
    """
    """


class Context(mongoengine.Document):
    """
    :ivar User ofUser:
    :ivar datetime timestamp:
    :ivar typing.List[Params] params:
    :ivar Message message:
    """
    ofUser = mongoengine.ReferenceField(User, required=True, null=False)
    timestamp = mongoengine.DateTimeField(required=True, null=False)
    params = mongoengine.ListField(mongoengine.EmbeddedDocumentField(Params))
    message = mongoengine.EmbeddedDocumentField(Message)


"""
/* Data */
/* Messages history */
/* Context */

export interface IContextModel extends mongoose.Model<IContext> {
    getCurrentContextByUserId(userId: string): Promise< IContext | null | IError >;
    getCurrentContextByUser(user: IUser): Promise< IContext | null | IError >;
}

function getCurrentContextByUserId(this: IContextModel, userId: string): Promise< IContext | null | IError > {
    return this.findOne({
        ofUser: userId,
        endTimestamp: null,
    }).sort({
        startTimestamp: -1,
    }).then(
        (context) => Promise.resolve(context),
        (err) => {
            const e: IError = {
                message: "Impossible ottenere il context richiesto",
                level: "error",
                original_error: err,
            };

            return Promise.reject(e);
        },
    );
}

function getCurrentContextByUser(this: IContextModel, user: IUser): Promise< IContext | null | IError > {
    return this.findOne({
        ofUser: user._id,
        endTimestamp: null,
    }).sort({
        startTimestamp: -1,
    }).then(
        (context) => Promise.resolve(context),
        (err) => {
            const e: IError = {
                message: "Impossible ottenere il context richiesto",
                level: "error",
                original_error: err,
            };

            return Promise.reject(e);
        },
    );
}

contextSchema.statics.getCurrentContextByUser = getCurrentContextByUser;
contextSchema.statics.getCurrentContextByUserId = getCurrentContextByUserId;
"""
