from sanic import Blueprint

from .user import ns as user_ns
from .message import ns as message_ns


def create_api() -> Blueprint:
    """ Create an api endpoint(that has under an '/user/...' and '/message/...' endponts) """
    blueprint = Blueprint('Api')

    user_ns.url_prefix = '/user'
    user_ns.register(blueprint, {})

    message_ns.url_prefix = '/message'
    message_ns.register(blueprint, {})

    return blueprint