import os
import sys

from progTiroc.db import DBInstance
from progTiroc.api import create_api

from sanic import Sanic
from sanic_swagger import swagger_blueprint, openapi_blueprint

if __name__ == '__main__':
    envDebug: str = os.environ.get('DEBUG')
    debug: bool = (envDebug is not None) and (envDebug == '1')

    print(os.environ)

    try:
        port = int(os.environ.get('PORT', 5000))
    except ValueError:
        print('Enviroment varible port should be number')
        sys.exit(5)

    print(envDebug, port)

    if (port >= 65535):
        print('Enviroment varible port is not valid port')
        sys.exit(4)

    db_host: str = os.environ.get('DBHOST', '127.0.0.1')
    db_port: int
    db_name: str = os.environ.get('DBNAME', 'db')
    db_user: str = os.environ.get('DBUSER', 'user')
    db_pswd: str = os.environ.get('DBPSWD', 'example')

    try:
        db_port = int(os.environ.get('DBPORT', 27017))
    except ValueError:
        print('db varible port should be number')
        sys.exit(5)

    db_instance = DBInstance(db_name, db_host, db_port, db_user, db_pswd)

    app = Sanic(__name__)
    api = create_api()
    api.url_prefix = '/api'

    app.blueprint(api)  # For api
    app.blueprint(openapi_blueprint)  # For openapi files
    app.blueprint(swagger_blueprint)  # For swagger UI

    app.dbi = db_instance  # Set db instance

    app.run(host='0.0.0.0', port=port, debug=debug)
