from flask_restplus import Namespace, Resource, fields, reqparse
import mongoengine

from progTiroc import db

import uuid
from datetime import datetime

ns = Namespace(name='user', description='User operations')

user = ns.model(
    'User', {
        'id': fields.String(
            readonly=True, description='The user unique identifier'),
        'username': fields.String(
            readonly=False, description='The user displayed username')
    })

userPutRQ = reqparse.RequestParser(bundle_errors=True)
userPutRQ.add_argument(
    'username',
    type=str,
    required=True,
    help='The user\'s username',
    location='json')


@ns.route('')
class UserList(Resource):
    """ Show a list of all the users or insert user in list """

    def get(self):
        """ List all users """
        try:
            data = [{
                'id': str(user.id),
                'username': user.username
            } for user in db.User.objects.only(*db.User.externallyVisible)]
        except Exception:
            ns.abort(500, 'Impossible to get the data requested')

        return data, 200

    @ns.doc(body=user)
    @ns.marshal_with(user)
    def put(self):
        """ Create a single user """

        args = userPutRQ.parse_args()

        user = db.User(
            username=args['username'],
            googleSessionId=uuid.uuid4(),
        )

        try:
            user.save()
        except mongoengine.OperationError:
            ns.abort(500, 'Impossible to save changes')

        context = db.Context(
            ofUser=user,
            startTimestamp=datetime.now(),
            endTimestamp=None,
            params=[],
            messages=[])

        try:
            context.save()
        except mongoengine.OperationError:
            ns.abort(500, 'Impossible to save changes')
            # TODO: Gestire caso in cui user è comunque salvato

        return {
            'id': str(user.id),
            'username': user.username,
        }, 200


@ns.route('/<string:oId>')
class SingleUser(Resource):
    """ Show single user """

    @ns.marshal_with(user)
    @ns.doc(params={'oId': 'The id of the required user'})
    def get(self, oId: str):
        """ Get existing user """

        try:
            user = db.User.objects(
                id=oId).only(*db.User.externallyVisible).get()
        except mongoengine.MultipleObjectsReturned:
            ns.abort(500,
                     'There should be one user but more than one were found')
        except mongoengine.DoesNotExist:
            ns.abort(400, 'Requested user not found')

        return {'id': str(user.id), 'username': user.username}, 200

    @ns.marshal_with(user)
    @ns.doc(params={'oId': 'The id of the required user'})
    @ns.doc(body=user)
    def post(self, oId: str):
        """ Modify existing user """

        try:
            user = db.User.objects(
                id=oId).only(*db.User.externallyVisible).get()
        except mongoengine.MultipleObjectsReturned:
            ns.abort(500,
                     'There should be one user but more than one were found')
        except mongoengine.DoesNotExist:
            ns.abort(400, 'Requested user not found')

        args = userPutRQ.parse_args()

        user.username = args['username']

        user.save()

        return {'id': str(user.id), 'username': user.username}, 200
