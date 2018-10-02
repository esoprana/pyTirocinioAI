"""
Module to define message rest endpoint, are defined '/' and '/{messageId}'
"""

from datetime import datetime

from sanic import Blueprint
from sanic.response import json
from sanic.request import Request
from sanic.views import HTTPMethodView
from sanic_swagger import doc

import attr

import marshmallow

from bson import ObjectId
from google.protobuf.json_format import MessageToDict

import dateutil.parser

WOZ_BOT_ID = '000000000000000000000000'
NWOZ_BOT_ID = '000000000000000000000001'


class DocMessageGet(doc.Model):
    """ Model to show in generated swagger(for get) """
    id: str = doc.field(description='The message unique identifier')
    text: str = doc.field(description='Message\'s text')
    timestamp: datetime = doc.field(description='The message\'s timestmap')


class DocMessagePut(doc.Model):
    """ Model to show in generated swagger(for put) """
    text: str = doc.field(description='The text of the message')


class AfterFilter(doc.Model):
    after: datetime = doc.field(
        description='To filter all messages after a datetime in isoformat')


class ListMessage(HTTPMethodView):
    """ Rappresents the whole of the messages of a user"""

    @doc.summary('Get messages of a specific user')
    @doc.consumes(AfterFilter, location='query', required=False)
    async def get(self, request: Request, oId: str):
        """ Get messages of a specific user """

        find_filter = {'ofUser': ObjectId(oId)}

        after = request.args.get('after')
        if after is not None:
            try:
                find_filter['timestamp'] = {
                    '$gt': dateutil.parser.isoparse(after)
                }
            except ValueError:
                return json({
                    'message': 'after field should be datetime in iso format'
                }, 400)

        with request.app.dbi.context() as db_ctx:
            contexts = [
                context async for context in db_ctx.Context.find(
                    find_filter,
                    sort=[('timestamp', -1)],
                    projection=request.app.dbi.message_schema.__mongodump__)
            ]

            if not contexts:
                return json({
                    'message': 'No context found check the user\'s id sent'
                }, 400)

            data, error = request.app.dbi.message_schema.dump(
                contexts, many=True)

            if error:
                print(error)
                return json({
                    'message': 'Impossible to serialize messages'
                }, 500)

            return json(data, 200)


class SingleMessage(HTTPMethodView):
    """ Save messages sdds"""

    @doc.summary('Create a message')
    @doc.consumes(DocMessagePut, location='body')
    @doc.produces(DocMessageGet)
    async def put(self, request: Request, fr: str, to: str):
        """ Create a message """

        if request.json is None:
            return json({'message': 'invalid schema format(json)'}, 400)

        try:
            data, errors = request.app.dbi.message_schema.load(request.json)
        except marshmallow.ValidationError as e:
            e.messages['message'] = 'ValidationError'
            return json(e.messages, 400)

        if errors:
            errors['message'] = 'ValidationError'
            return json(errors, 400)

        isWoz: bool = WOZ_BOT_ID in (fr, to)

        if (not isWoz and to != NWOZ_BOT_ID):
            return json({
                'message': 'La comunicazione può avvenire solo come:\n' +
                ' WOZ BOT\n' + ' 000000000000000000000000 -> user\n' +
                ' user -> 000000000000000000000000\n' + ' NON WOZ BOT\n' +
                ' user -> 000000000000000000000001\n'
            }, 400)

        with request.app.dbi.context() as db_ctx:
            msg = None

            if not isWoz:
                user = await db_ctx.User.find_one({'id': ObjectId(fr)})

                if user is None:
                    return json({'message': 'User not found'}, 404)

                google_data = request.app.ai.analyze_text(
                    data['text'], user.googleSessionId)

                r = {}
                r['intent'] = google_data['intent']
                r['sentiment'] = google_data['sentiment']
                r['googleTopic'] = google_data['categories']

                msg = db_ctx.UserMessage(text=data['text'], **r)

            elif fr == WOZ_BOT_ID:
                (fr, to) = (to, fr)

                msg = db_ctx.WozBotMessage(text=data['text'])
            else:
                msg = db_ctx.WozUserMessage(text=data['text'])

            # Get the list of context of user in decresend order of timestamp
            old_context: db_ctx.Context = await db_ctx.Context.find_one(
                {
                    'ofUser': ObjectId(fr)
                }, sort=[('timestamp', -1)])

            # If no active context send error(at least one should be)
            if old_context is None:
                return json({
                    'message': 'Errore dovrebbe esserci un contesto attivo' +
                    '(0 al momento)\n' + 'Controllare che l\'utente esista'
                }, 500)

            context = db_ctx.Context(
                ofUser=old_context.ofUser,
                timestamp=datetime.now(),
                params=old_context.params,
                message=msg)
            await context.commit()

            data, error = request.app.dbi.message_schema.dump(context)
            if error:
                print(error)
                return json({'message': 'Impossible to serialize message'}, 500)

            if not isWoz:
                responses = await request.app.ai.get_message(
                    db_ctx, user.id, google_data, request.app.fallback_rule)

                if responses is not None:
                    for r in responses:
                        await r.commit()

                    data['response'] = "\n".join(
                        [r.message.text for r in responses])

            return json(data, 200)


ns = Blueprint('Message')
ns.add_route(SingleMessage.as_view(), '/<fr:string>/<to:string>')
ns.add_route(ListMessage.as_view(), '/user/<oId:string>')
