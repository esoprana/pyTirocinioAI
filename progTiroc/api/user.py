import uuid
from datetime import datetime
import typing

from progTiroc import db

import mongoengine

from sanic import Blueprint
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_swagger import doc

import marshmallow


class DocUserGet(doc.Model):
    id: str = doc.field(description='The user unique identifier')
    username: str = doc.field(description='The user displayed username')


class DocUserPut(doc.Model):
    username: str = doc.field(description='The user displayed username')


class UserPutSchema(marshmallow.Schema):
    username = marshmallow.fields.Str(attribute="username", required=True)

    class Meta:
        unknown = 'raise'
        partial = False


class UserList(HTTPMethodView):
    """ Show a list of all the users or insert user in list """

    @doc.summary('List all users')
    @doc.produces(doc.field(type=typing.List[DocUserGet]))
    async def get(self, request):
        with request.app.dbi.context() as db_ctx:
            try:
                data = [{
                    'id': str(user.id),
                    'username': user.username
                } for user in db_ctx.User.objects.only(
                    *db.types.User.externallyVisible)]

                return json(data, 200)
            except Exception as e:
                print(e)
                return json({
                    'message': 'Impossible to get the data requested'
                }, 500)

    @doc.summary('Create a user')
    @doc.consumes(DocUserPut, location='body', required=True)
    @doc.produces(DocUserGet)
    async def put(self, request):
        """ Create a single user """

        if request.json is None:
            return json({'message': 'invalid schema format(json)'}, 400)

        try:
            data, errors = UserPutSchema().load(request.json)
        except marshmallow.ValidationError as e:
            e.messages['message'] = 'ValidationError'
            return json(e.messages, 400)

        if errors:
            errors['message'] = 'ValidationError'
            return json(errors, 400)

        with request.app.dbi.context() as db_ctx:
            user = db_ctx.User(
                username=data['username'],
                googleSessionId=uuid.uuid4(),
            )

            try:
                await user.commit()
            except mongoengine.OperationError as oe:
                print(oe)
                return json({'message': 'Impossible to commit changes'}, 500)

            context = db_ctx.Context(
                ofUser=user,
                timestamp=datetime.now(),
                params=[],
                message=db_ctx.Message(text='Hi!'))

            try:
                await context.commit()
            except mongoengine.OperationError as oe:
                print(oe)
                return json({'message': 'Impossible to commit changes'}, 500)
                # TODO: Gestire caso in cui user è comunque salvato

            return json({
                'id': str(user.id),
                'username': user.username,
            }, 200)


class SingleUser(HTTPMethodView):
    """ Show single user """

    @doc.summary('Get single user')
    @doc.produces(DocUserGet)
    async def get(self, oId: str):
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

    @doc.summary('udpate info on existing user')
    @doc.consumes(DocUserPut, location='body', required=True)
    @doc.produces(DocUserGet)
    def post(self, request, oId: str):
        """ Modify existing user """

        if request.json is None:
            return json({'message': 'invalid schema format(json)'}, 400)

        try:
            data, errors = UserPutSchema().load(request.json)
        except marshmallow.ValidationError as e:
            e.messages['message'] = 'ValidationError'
            return json(e.messages, 400)

        if errors:
            errors['message'] = 'ValidationError'
            return json(errors, 400)

        with request.app.dbi.context() as db_ctx:
            try:
                user = db_ctx.User.objects(
                    id=oId).only(*db.User.externallyVisible).get()
            except mongoengine.MultipleObjectsReturned as e:
                print(e)
                return json({
                    'message': 'There should be one user but more than one were found'
                }, 500)
            except mongoengine.DoesNotExist as e:
                print(e)
                return json({'message': 'Requested user not found'}, 400)

            user.username = data['username']

            user.commit()

            return json({'id': str(user.id), 'username': user.username}, 200)


ns = Blueprint('User')
ns.add_route(UserList.as_view(), '/')
ns.add_route(SingleUser.as_view(), '/<oId:string>')
