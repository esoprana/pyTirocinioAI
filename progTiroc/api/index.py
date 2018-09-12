from flask import Blueprint
from flask_restplus import Api

from .user import ns as user_ns
from .message import ns as message_ns


def create_api() -> Blueprint:
    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api = Api(
        blueprint,
        version='0.1',
        title='Storygram API',
        description='',
        doc='/docs/',
        ui=True)

    api.add_namespace(user_ns)
    api.add_namespace(message_ns)

    return api
