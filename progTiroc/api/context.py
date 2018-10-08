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


class SingleMessage(HTTPMethodView):
    """ Save messages sdds"""

    async def get(self, request: Request, oid: str):
        """ Create a message """

        with request.app.dbi.context() as db_ctx:
            context = await db_ctx.Context.find_one({'id': ObjectId(oid)})

            if context is None:
                return json({'message': 'Context not found'}, 404)

            data, error = db_ctx.Context.Schema().dump(context)
            if error:
                print(error)
                return json({'message': 'Impossible to serialize message'}, 500)

            return json(data, 200)


ns = Blueprint('Message')
ns.add_route(SingleMessage.as_view(), '/<oid:string>/')
