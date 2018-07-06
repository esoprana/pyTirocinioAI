from flask import Flask, request, jsonify
import db
from datetime import datetime
import uuid

app = Flask(__name__)

WOZ_BOT_ID = '000000000000000000000000'
NWOZ_BOT_ID = '000000000000000000000001'


@app.route('/api/message/<string:fr>/<string:to>', methods=['PUT'])
def message(fr, to):
    isWoz: bool = fr == WOZ_BOT_ID or to == WOZ_BOT_ID

    if (isWoz):
        if (fr == WOZ_BOT_ID):
            (fr, to) = (to, fr)
            msg = db.WozBotMessage(text=request.data, timestamp=datetime.now())
        else:
            msg = db.WozUserMessage(text=request.data, timestamp=datetime.now())

        contextsOfUser = db.Context.objects(ofUser=fr, endTimestamp=None)
        if (len(contextsOfUser) > 1):
            return jsonify({
                'status': 'error',
                'message':  'Errore dovrebbe esserci un esattamente un' +
                            ' contesto attivo(>1 al momento)'
            })
        elif (len(contextsOfUser) == 0):
            return jsonify({
                'status': 'error',
                'message':  'Errore dovrebbe esserci un esattamente un' +
                            ' contesto attivo(0 al momento)\n' +
                            'Controllare che l\'utente esista'
            })

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
        })
    else:
        pass

    return str({'status': 'ok'})


@app.route('/api/user', methods=['PUT'])
def create_user():
    params = request.get_json()
    username = params.get('username')

    if username is None:
        return jsonify({
            'status': 'error',
            'message': 'Il campo body "username" è vuoto'
        })

    user = db.User(
        username=username,
        googleSessionId=uuid.uuid4(),
    )

    user.save()

    context = db.Context(
        ofUser=user,
        startTimestamp=datetime.now(),
        endTimestamp=None,
        params=[],
        messages=[]
    )

    context.save()

    return jsonify({
        'id': str(user.id),
        'username': user.username,
    })

    # TODO: Dividere in due collection distinte i messaggi e i contesti

