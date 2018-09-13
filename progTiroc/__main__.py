from flask import Flask

from progTiroc.api import create_api
from progTiroc.db import connect

import os
import sys

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

    connect(db_host, db_port, db_name, db_user, db_pswd)

    blue, api = create_api()

    app = Flask(__name__)
    app.register_blueprint(blue)
    app.run(host='0.0.0.0', port=port, debug=debug)
