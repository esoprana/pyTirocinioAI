from sanic import Blueprint
from sanic.response import json
from sanic.request import Request
from sanic.views import HTTPMethodView
from sanic_swagger import doc

from bson import ObjectId


class SingleTopic(HTTPMethodView):
    """ Save messages sdds"""

    async def get(self, request: Request, oid: str):
        """ Create a message """

        with request.app.dbi.context() as db_ctx:
            rule = await db_ctx.Topic.find_one({'id': ObjectId(oid)})

            if rule is None:
                return json({'message': 'Topic not found'}, 404)

            data, error = db_ctx.Topic.Schema().dump(rule)

            if error:
                print(error)
                return json({'message': 'Impossible to serialize topic'}, 500)

            return json(data, 200)


ns = Blueprint('Topic')
ns.add_route(SingleTopic.as_view(), '/<oid:string>/')
