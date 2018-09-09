from flask_restplus import Namespace, Resource, fields, reqparse
import mongoengine

from progTiroc import db

from datetime import datetime

WOZ_BOT_ID = '000000000000000000000000'
NWOZ_BOT_ID = '000000000000000000000001'

ns = Namespace(name='message', description='Message operations')

message = ns.model(
    'Message', {
        'id': fields.String(
            readonly=True,
            required=False,
            description='The message unique identifier'),
        'text': fields.String(required=True, description='Message\'s text'),
        'timestamp': fields.DateTime(
            readonly=True,
            required=False,
            description='The message\'s timestamp')
    })

messagePutRQ = reqparse.RequestParser(bundle_errors=True)
messagePutRQ.add_argument(
    'text',
    type=str,
    required=True,
    help='The text of the message',
    location='json')


@ns.route('/<string:fr>/<string:to>')
class SingleMessage(Resource):
    """ Save messages """

    @ns.marshal_with(message)
    @ns.doc(
        params={
            'fr': 'The id of the user/bot from that sends the message',
            'to': 'The id of the user that receives the message'
        })
    @ns.doc(body=messagePutRQ)
    def put(self, fr: str, to: str):
        isWoz: bool = fr == WOZ_BOT_ID or to == WOZ_BOT_ID

        args = messagePutRQ.parse_args()

        if (not isWoz and to != NWOZ_BOT_ID):
            ns.abort(
                400, 'La comunicazione può avvenire solo come:\n' + ' WOZ BOT\n'
                + ' 000000000000000000000000 -> user\n' +
                ' user -> 000000000000000000000000\n' + ' NON WOZ BOT\n' +
                ' user -> 000000000000000000000001\n')
            return

        msg: db.Message = None

        if (not isWoz):
            # TODO: Create vera risposta
            msg = db.UserMessage(text=args['text'])
        elif (fr == WOZ_BOT_ID):
            (fr, to) = (to, fr)

            msg = db.WozBotMessage(text=args['text'])
        else:
            msg = db.WozUserMessage(text=args['text'])

        # Get the list of context of user in decresend order of timestamp
        contextsOfUser = db.Context.objects(ofUser=fr).order_by('-timestamp')

        # If no active context send error(at least one should be)
        if (len(contextsOfUser) == 0):
            ns.abort(
                500, 'Errore dovrebbe esserci un ' +
                'contesto attivo(0 al momento)\n' +
                'Controllare che l\'utente esista')

        old_context: db.Context = contextsOfUser[0]

        context: db.Context = db.Context(
            ofUser=old_context.ofUser,
            timestamp=datetime.now(),
            params=old_context.params,
            message=msg)
        context.save()

        return {
            'id': str(context.id),
            'text': context.message.text,
            'timestamp': context.timestamp
        }, 200
