import os
import sys
from distutils.util import strtobool
import yaml

from sanic import Sanic
from sanic_swagger import swagger_blueprint, openapi_blueprint

from progTiroc.db import DBInstance
from progTiroc.api import create_api

from typing import List, Any


def conf_value(var_name: str, cfg: dict, yml_cfg: dict, default=None) -> Any:
    names = var_name.split('_')

    to_set = os.environ.get(var_name, None)

    if to_set is None:
        yml_curr = yml_cfg
        for name in names[:-1]:
            yml_curr = yml_curr.get(name, None)

            if yml_curr is None:
                break

        if yml_curr is not None:
            to_set = yml_curr.get(names[-1], None)

    if to_set is None:
        to_set = default

    current = cfg
    for var in names[:-1]:
        next_curr = current.get(var, None)

        if next_curr is None:
            val = {}
            current[var] = val
            current = val
        else:
            current = next_curr

    current[names[-1]] = to_set
    return to_set


def setup_app_config(app: Sanic):

    config_file_path = os.environ.get('CONFIG_FILE')
    yml_cfg = yaml.load(open(config_file_path, 'r'), Loader=yaml.Loader)

    conf_value(
        var_name='DEBUG', cfg=app.config, yml_cfg=yml_cfg, default='false')
    conf_value(var_name='PORT', cfg=app.config, yml_cfg=yml_cfg, default=5000)
    conf_value(var_name='DB_HOST', cfg=app.config, yml_cfg=yml_cfg)
    conf_value(var_name='DB_PORT', cfg=app.config, yml_cfg=yml_cfg)
    conf_value(
        var_name='DB_NAME', cfg=app.config, yml_cfg=yml_cfg, default='db')
    conf_value(var_name='DB_USERNAME', cfg=app.config, yml_cfg=yml_cfg)
    conf_value(var_name='DB_PASSWORD', cfg=app.config, yml_cfg=yml_cfg)

    try:
        if type(app.config['DEBUG']) is not bool:
            app.config['DEBUG'] = strtobool(app.config['DEBUG'])
    except ValueError:
        print('Error converting DEBUG to boolean(true/false)')
        sys.exit(1)

    try:
        if type(app.config['PORT']) is not int:
            app.config['PORT'] = int(app.config['PORT'])
    except ValueError:
        print('Error converting PORT to int')
        sys.exit(1)

    try:
        if type(app.config['DB']['PORT']) is not int:
            app.config['DB']['PORT'] = int(app.config['DB']['PORT'])
    except ValueError:
        print('Error converting DB_PORT to int')
        sys.exit(1)

    if app.config['PORT'] >= 65535:
        print('Enviroment varible port is not valid port')
        sys.exit(1)


def setup() -> Sanic:
    app = Sanic(__name__)
    setup_app_config(app)

    api = create_api()
    api.url_prefix = '/api'

    app.blueprint(api)  # For api
    app.blueprint(openapi_blueprint)  # For openapi files
    app.blueprint(swagger_blueprint)  # For swagger UI

    @app.listener('before_server_start')
    def init(sanic, loop):
        app.dbi = DBInstance(
            database_name=app.config['DB']['NAME'],
            database_host=app.config['DB']['HOST'],
            database_port=app.config['DB']['PORT'],
            database_user=app.config['DB']['USERNAME'],
            database_pwd=app.config['DB']['PASSWORD'])  # Set db instance

    return app


if __name__ == '__main__':

    app = setup()

    app.run(host='0.0.0.0', port=app.config['PORT'], debug=app.config['DEBUG'])
