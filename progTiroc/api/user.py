""" Module to define user rest endpoint, are defined '/' and '/{objectId}' """

import uuid
from datetime import datetime
import typing

import mongoengine

from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_swagger import doc

from bson import ObjectId

import marshmallow


class DocUserGet(doc.Model):
    """ Model of User returned by the api """

    id: str = doc.field(description='The user unique identifier')
    username: str = doc.field(description='The user displayed username')


class DocUserPut(doc.Model):
    """ Model of User to send to the api """

    username: str = doc.field(description='The user displayed username')


class UserPutSchema(marshmallow.Schema):
    """ Model used to translate User to json in the api """

    username = marshmallow.fields.Str(attribute="username", required=True)

    class Meta:
        unknown = 'raise'
        partial = False


class UserList(HTTPMethodView):
    """ Show a list of all the users or insert user in list """

    @doc.summary('List all users')
    @doc.produces(doc.field(type=typing.List[DocUserGet]))
    async def get(self, request: Request):
        """Endpoint for GET method (list all users)

        :param request: request made
        :type request: Request
        """
        with request.app.dbi.context() as db_ctx:
            try:
                data = [{
                    'id': str(user.id),
                    'username': user.username
                } async for user in db_ctx.User.find()]

                return json(data, 200)
            except Exception as err:
                print(err)
                return json({
                    'message': 'Impossible to get the data requested'
                }, 500)

    @doc.summary('Create a single user')
    @doc.consumes(DocUserPut, location='body', required=True)
    @doc.produces(DocUserGet)
    async def put(self, request: Request):
        """Endpoint for PUT method (creates a single user)

        :param request: request made
        :type request: Request
        """
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
    async def get(self, request: Request, oId: str):
        """Endpoint of the GET method (get single user with specified oId)

        :param request: request made
        :type request: Request
        :param oId: path variable that rapresent the id of the user
        :type oId: str
        """

        with request.app.dbi.context() as db_ctx:
            try:
                matchingUsers = [
                    i async for i in db_ctx.User.find({
                        'id': ObjectId(oId)
                    }).limit(2)
                ]  # TODO: Check if possible get only some columns

                if len(matchingUsers) == 0:
                    return json({'message': 'Requested user not found'}, 400)
                elif len(matchingUsers) > 1:
                    return json({
                        'message': 'There should be one user but more than one were found'
                    }, 500)

                user = matchingUsers[0]
                return json({
                    'id': str(user.id),
                    'username': user.username
                }, 200)
            except mongoengine.MultipleObjectsReturned:
                pass  # TODO: tofix

    @doc.summary('Udpate info on existing user')
    @doc.consumes(DocUserPut, location='body', required=True)
    @doc.produces(DocUserGet)
    async def post(self, request: Request, oId: str):
        """Endpoint of the POST method (update info on existing user)

        :param request: request made
        :type request: Request
        :param oId: path variable that rapresent the id of the user
        :type oId: str
        """

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
                matchingUsers = [
                    i async for i in db_ctx.User.find({
                        'id': ObjectId(oId)
                    }).limit(2)
                ]  # TODO: Check if possible get only some columns

                if len(matchingUsers) == 0:
                    return json({'message': 'Requested user not found'}, 400)
                elif len(matchingUsers) > 1:
                    return json({
                        'message': 'There should be one user but more than one were found'
                    }, 500)

                user = matchingUsers[0]

                user.username = data['username']
                user.commit()

                return json({
                    'id': str(user.id),
                    'username': user.username
                }, 200)
            except Exception as e:
                print(e)
                pass


ns = Blueprint('User')
ns.add_route(UserList.as_view(), '/')
ns.add_route(SingleUser.as_view(), '/<oId:string>')
