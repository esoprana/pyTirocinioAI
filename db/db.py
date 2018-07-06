import os
import sys
import mongoengine

host: str = os.environ.get('DBHOST', '127.0.0.1')
port: str = os.environ.get('DBPORT', '27017')
name: str = os.environ.get('DBNAME', 'db')
user: str = os.environ.get('DBUSER', 'user')
pswd: str = os.environ.get('DBPSWD', 'example')

try:
    port: int = int(port)
except ValueError:
    print('Enviroment variable DBPORT is not integer number')
    sys.exit(1)

if (port >= 65535):
    print('Enviroment variable DBPORT is non valid port')
    sys.exit(2)

try:
    mongoengine.connect(name, host=host, port=port, username=user, password=pswd)
except Exception as ex:
    print(ex)
    sys.exit(3)


class User(mongoengine.Document):
    """
    {
        googleSessionID: {
            type: String,
            required: true,
        },
    }
    """

    username = mongoengine.StringField(required=True, null=False)
    googleSessionId = mongoengine.UUIDField(required=True, null=False)


class Rule(mongoengine.Document):
    pass


class Topic(mongoengine.Document):
    """
    {
        rules: {
            type: [{
                type: mongoose.Schema.Types.ObjectId,
                ref: "Rule",
                required: true,
            }],
        },
    }
    """

    rules = mongoengine.ListField(mongoengine.ReferenceField(Rule), required=True, null=False)


class Params(mongoengine.EmbeddedDocument):
    """
    {
        ofTopic: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "Topic",
            required: true,
        },
        values: {
            type: mongoose.Schema.Types.Mixed,
            required: true,
        },
        startTime: {
            type: Date,
            required: true,
        },
        priority: {
            type: Number,
            required: true
        }
    }
    """

    ofTopic = mongoengine.ReferenceField(Topic, required=True, null=False)
    values = mongoengine.DictField(required=True, default=dict)  # TODO: Ricontrollare
    startTime = mongoengine.DateTimeField(required=True, null=False)
    priority = mongoengine.IntField(required=True, null=False)


class Message(mongoengine.EmbeddedDocument):
    """
    {
        timestamp: {
            type: Date,
            required: true,
        },
        text: {
            type: String,
            required: true,
        },
    }
    """

    timestamp = mongoengine.DateTimeField(required=True, null=False)
    text = mongoengine.StringField(required=True, null=False)
    meta = {'allow_inheritance': True}


class BotMessage(Message):
    """
    {
        selectedVariant: {
            type: Number,
            required: true,
        },
        fromRule: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "Rule",
            required: true,
        },
    }
    """

    selectedVariant = mongoengine.IntField(required=True, null=False)
    fromRule = mongoengine.ReferenceField(Rule, required=True, null=False)


class UserMessage(Message):
    """
    {
        intent: mongoose.Schema.Types.Mixed,
        photo: mongoose.Schema.Types.Mixed,
        sentiment: mongoose.Schema.Types.Mixed,
        googleTopic: mongoose.Schema.Types.Mixed,
    }
    """

    intent = mongoengine.DictField(required=True, null=True)
    photo = mongoengine.DictField(required=True, null=True)
    sentiment = mongoengine.DictField(required=True, null=True)
    googlTopic = mongoengine.DictField(required=True, null=True)


class WozBotMessage(Message):
    """
    """


class WozUserMessage(Message):
    """
    """


class Context(mongoengine.Document):
    """
    {
        ofUser: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "User",
            required: true,
        },
        startTimestamp: {
            type: Date,
            required: true,
        },
        endTimestamp: {
            type: Date,
            required: false,
        },
        params: {
            type: [{
                param: {
                    type: paramsSchema,
                    required: true,
                },
                priority: {
                    type: Number,
                    required: true,
                },
            }],
            required: true,
        },
        messages: {
            type: [{
                type: messageSchema,
                required: true,
            }],
            required: true,
        },
    }
    """
    ofUser = mongoengine.LazyReferenceField(User, required=True, null=False)
    startTimestamp = mongoengine.DateTimeField(required=True, null=False)
    endTimestamp = mongoengine.DateTimeField(required=False, null=True)
    params = mongoengine.ListField(mongoengine.EmbeddedDocumentField(Params))  # TODO: Ricontrollare priorità(usare indice implicito in lista)
    messages = mongoengine.ListField(mongoengine.EmbeddedDocumentField(Message), required=False, default=list)


class TopicAndNames(mongoengine.EmbeddedDocument):
    targetTopic = mongoengine.ReferenceField(Topic, required=True, null=False)
    namesToExport = mongoengine.ListField(mongoengine.StringField(), required=True)


class Action(mongoengine.EmbeddedDocument):
    """
    {
        text: {
            type: [{type: String}],
            required: true,
        },
        exportNames: {
            type: [{
                targetTopic: {
                    type: mongoose.Schema.Types.ObjectId,
                    ref: "Topic",
                    required: true,
                },
                namesToExport: {
                    type: [{type: String, required: true}],
                    required: true,
                },
            }],
            required: true,
        },
        popUntil: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "Topic",
            required: false,
        },
        pushTopic: {
            type: [{
                targetTopic: {
                    type: mongoose.Schema.Types.ObjectId,
                    ref: "Topic",
                    required: true,
                },
                namesToExport: {
                    type: [{type: String, required: true}],
                    required: true,
                },
            }],
            required: true,
        },
        isQuestion: {
            type: Boolean,
            required: true,
        },
    }
    """

    text = mongoengine.ListField(mongoengine.StringField, required=True, null=False)
    exportNames = mongoengine.ListField(TopicAndNames, required=True)
    popUntil = mongoengine.ReferenceField(Topic, required=True, null=False)
    pushTopic = mongoengine.ListField(TopicAndNames, required=True)
    isQuestion = mongoengine.BooleanField(required=True, null=False)


class Rule(mongoengine.Document):
    """
    {
        condition: {
            type: mongoose.Schema.Types.Mixed, // TODO: Da cambiare in tipo più preciso
            required: true,
        },
        score: {
            type: Number,
            required: true,
        },
        action: {
            type: actionSchema,
            required: true,
        },
    }
    """
    condition = mongoengine.DictField(required=True, null=False)
    score = mongoengine.IntField(required=True, null=False)
    action = mongoengine.EmbeddedDocumentField(Action, required=True, null=False)


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

