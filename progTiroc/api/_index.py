from sanic import Blueprint

from .user import ns as user_ns
from .message import ns as message_ns
from .context import ns as context_ns
from .rule import ns as rule_ns


def create_api() -> Blueprint:
    """ Create an api endpoint(that has under an '/user/...' and '/message/...' endponts) """
    blueprint = Blueprint('Api')

    user_ns.url_prefix = '/user'
    user_ns.register(blueprint, {})

    message_ns.url_prefix = '/message'
    message_ns.register(blueprint, {})

    context_ns.url_prefix = '/context'
    context_ns.register(blueprint, {})

    rule_ns.url_prefix = '/rule'
    rule_ns.register(blueprint, {})

    return blueprint
