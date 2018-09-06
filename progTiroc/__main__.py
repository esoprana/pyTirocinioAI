from progTiroc.api import app
import os
import sys


def start_server(debug: bool, port: int):
    if (port >= 65535):
        print('Enviroment varible port is not valid port')
        sys.exit(4)

    app.run(host='0.0.0.0', port=port, debug=debug)


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

    start_server(debug=debug, port=port)
