from datetime import datetime
import marshmallow

from progTiroc import db

import mongoengine

from sanic import Blueprint
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_swagger import doc

WOZ_BOT_ID = '000000000000000000000000'
NWOZ_BOT_ID = '000000000000000000000001'


class DocMessageGet(doc.Model):
    id: str = doc.field(description='The message unique identifier')
    text: str = doc.field(description='Message\'s text')
    timestamp: datetime = doc.field(description='The message\'s timestmap')


class DocMessagePut(doc.Model):
    text: str = doc.field(description='The text of the message')


class MessagePut(marshmallow.Schema):
    text = marshmallow.fields.Str(attribute="text", required=True)

    class Meta:
        unknown = 'raise'
        partial = False


class SingleMessage(HTTPMethodView):
    """ Save messages """

    @doc.consumes(DocMessagePut, location='body')
    @doc.produces(DocMessageGet)
    async def put(self, request, fr: str, to: str):
        if request.json is None:
            return json({'message': 'invalid schema format(json)'}, 400)

        try:
            data, errors = MessagePut().load(request.json)
        except marshmallow.ValidationError as e:
            e.messages['message'] = 'ValidationError'
            return json(e.messages, 400)

        if errors:
            errors['message'] = 'ValidationError'
            return json(errors, 400)

        isWoz: bool = fr == WOZ_BOT_ID or to == WOZ_BOT_ID

        if (not isWoz and to != NWOZ_BOT_ID):
            return json({
                'message': 'La comunicazione può avvenire solo come:\n' +
                ' WOZ BOT\n' + ' 000000000000000000000000 -> user\n' +
                ' user -> 000000000000000000000000\n' + ' NON WOZ BOT\n' +
                ' user -> 000000000000000000000001\n'
            }, 400)

        msg: db.Message = None

        with request.app.dbi.context() as db_ctx:
            if (not isWoz):
                # TODO: Create vera risposta
                msg = db_ctx.UserMessage(text=data['text'])
            elif (fr == WOZ_BOT_ID):
                (fr, to) = (to, fr)

                msg = db_ctx.WozBotMessage(text=data['text'])
            else:
                msg = db_ctx.WozUserMessage(text=data['text'])

            # Get the list of context of user in decresend order of timestamp
            contextsOfUser = db_ctx.Context.objects(
                ofUser=fr).order_by('-timestamp')

            # If no active context send error(at least one should be)
            if not contextsOfUser:
                return json({
                    'message': 'Errore dovrebbe esserci un ' +
                    'contesto attivo(0 al momento)\n' +
                    'Controllare che l\'utente esista'
                }, 500)

            old_context: db_ctx.Context = contextsOfUser[0]

            context = db_ctx.Context(
                ofUser=old_context.ofUser,
                timestamp=datetime.now(),
                params=old_context.params,
                message=msg)
            context.save()

            return json({
                'id': str(context.id),
                'text': context.message.text,
                'timestamp': context.timestamp.isoformat()
            }, 200)


ns = Blueprint('Message')
ns.add_route(SingleMessage.as_view(), '/<fr:string>/<to:string>')
