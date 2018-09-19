from .user import ns as user_ns
from .message import ns as message_ns

from sanic import Blueprint


def create_api():
    blueprint = Blueprint('Api')

    user_ns.url_prefix = '/user'
    user_ns.register(blueprint, {})

    message_ns.url_prefix = '/message'
    message_ns.register(blueprint, {})

    return blueprint
