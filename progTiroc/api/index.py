from flask import Flask, request, jsonify, Blueprint
from flask_restplus import Api, Resource, fields

from progTiroc import db

from datetime import datetime
import uuid

from .user import ns as user_ns

app = Flask(__name__)

blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint, version='0.1', title='Storygram API', description='', doc='/docs/', ui=True)

api.add_namespace(user_ns)

WOZ_BOT_ID = '000000000000000000000000'
NWOZ_BOT_ID = '000000000000000000000001'


@app.route('/api/message/<string:fr>/<string:to>', methods=['PUT'])
def message(fr, to):
    isWoz: bool = fr == WOZ_BOT_ID or to == WOZ_BOT_ID

    if (isWoz):
        if (fr == WOZ_BOT_ID):
            (fr, to) = (to, fr)

            msg = db.WozBotMessage(
                    text=request.data,
                    timestamp=datetime.now()
                )
        else:
            msg = db.WozUserMessage(
                    text=request.data,
                    timestamp=datetime.now()
                )

        contextsOfUser = db.Context.objects(ofUser=fr, endTimestamp=None)
        if (len(contextsOfUser) > 1):
            return jsonify({
                    'status': 'error',
                    'message':  'Errore dovrebbe esserci un esattamente un' +
                                ' contesto attivo(>1 al momento)'
                }), 500
        elif (len(contextsOfUser) == 0):
            return jsonify({
                    'status': 'error',
                    'message':  'Errore dovrebbe esserci un esattamente un' +
                                ' contesto attivo(0 al momento)\n' +
                                'Controllare che l\'utente esista'
                }), 500

        context: db.Context = contextsOfUser[0]

        context.messages.append(msg)
        context.save()
    elif (to != NWOZ_BOT_ID):
        return jsonify({
                'status': 'error',
                'message':  'La comunicazione può avvenire solo come:\n' +
                            ' WOZ BOT'
                            ' 000000000000000000000000 -> user\n' +
                            ' user -> 000000000000000000000000\n' +
                            '\n' +
                            ' NON WOZ BOT' +
                            ' user -> 000000000000000000000001\n'
            }), 400
    else:
        pass

    return str({'status': 'ok'})




app.register_blueprint(blueprint)

