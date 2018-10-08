from sanic import Blueprint
from sanic.response import json
from sanic.request import Request
from sanic.views import HTTPMethodView
from sanic_swagger import doc

from bson import ObjectId


class SingleRule(HTTPMethodView):
    """ Save messages sdds"""

    async def get(self, request: Request, oid: str):
        """ Create a message """

        with request.app.dbi.context() as db_ctx:
            rule = await db_ctx.Rule.find_one({'id': ObjectId(oid)})

            if rule is None:
                return json({'message': 'Rule not found'}, 404)

            data, error = db_ctx.Rule.Schema().dump(rule)

            for onP in data['condition']['onParams']:
                onP['__type__'] = str(onP['__type__'])

            if error:
                print(error)
                return json({'message': 'Impossible to serialize message'}, 500)

            return json(data, 200)


ns = Blueprint('Message')
ns.add_route(SingleRule.as_view(), '/<oid:string>/')
