from flask import Flask, request, jsonify, Blueprint, send_from_directory
from flask_restplus import Api, Resource, fields

from progTiroc import db

from datetime import datetime
import uuid

from .user import ns as user_ns
from .message import ns as message_ns

import os

app = Flask(__name__)

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

app.register_blueprint(blueprint)
