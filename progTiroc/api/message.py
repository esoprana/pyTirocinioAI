from flask_restplus import Namespace, Resource, fields, reqparse
from flask import request
import mongoengine

from progTiroc import db

from datetime import datetime


WOZ_BOT_ID = '000000000000000000000000'
NWOZ_BOT_ID = '000000000000000000000001'

ns = Namespace(name='message', description='Message operations')

message = ns.model('Message', {
    'id': fields.String(
            readonly=True,
            description='The message unique identifier'
        ),
    'text': fields.String(
            readonly=True,
            description='Message\'s text'
        ),
    'timestamp': fields.DateTime(
            readonly=True,
            description='The message\'s timestamp'
        )
})

@ns.route('/<string:fr>/<string:to>')
class SingleMessage(Resource):
    """ Save messages """

    #@ns.marshal_with(message)
    @ns.doc(params={'fr': 'The id of the user/bot from that sends the message', 'to': 'The id of the user that receives the message'})
    @ns.doc(body=fields.Raw)
    def put(self, fr: str, to: str):
        text = request.data
        isWoz: bool = fr == WOZ_BOT_ID or to == WOZ_BOT_ID

        if (isWoz):
            if (fr == WOZ_BOT_ID):
                (fr, to) = (to, fr)

                msg = db.WozBotMessage(
                        text=text,
                        timestamp=datetime.now()
                    )
            else:
                msg = db.WozUserMessage(
                        text=text,
                        timestamp=datetime.now()
                    )

            contextsOfUser = db.Context.objects(ofUser=fr, endTimestamp=None)
            if (len(contextsOfUser) > 1):
                ns.abort(
                        500, 'Errore dovrebbe esserci un esattamente un' +
                             ' contesto attivo(>1 al momento)'
                    )
            elif (len(contextsOfUser) == 0):
                ns.abort(
                        500, 'Errore dovrebbe esserci un esattamente un' +
                             ' contesto attivo(0 al momento)\n' +
                             'Controllare che l\'utente esista'
                    )

            context: db.Context = contextsOfUser[0]

            context.messages.append(msg)
            context.save()
        elif (to != NWOZ_BOT_ID):
            ns.abort(
                    400, 'La comunicazione può avvenire solo come:\n' +
                         ' WOZ BOT'
                         ' 000000000000000000000000 -> user\n' +
                         ' user -> 000000000000000000000000\n' +
                         '\n' +
                         ' NON WOZ BOT' +
                         ' user -> 000000000000000000000001\n'
                )
        else:
            ns.abort(
                    501, 'Not yet implemented'
                )

        #return {
        #        'id': str(msg.id),
        #        'text': msg.text,
        #        'timestamp': msg.timestamp
        #    }, 200
        return {
                'status': 'ok'
            }

