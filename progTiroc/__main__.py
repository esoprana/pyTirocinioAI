from progTiroc.api import app
import os
import sys


def start_server():
    envDebug: str = os.environ.get('DEBUG')
    debug: bool = (envDebug is not None) and (envDebug == '1')

    print(os.environ)

    try:
        port = int(os.environ.get('PORT', 5000))
    except ValueError:
        print('Enviroment varible port should be number')
        sys.exit(5)

    if (port >= 65535):
        print('Enviroment varible port is not valid port')
        sys.exit(4)

    print(envDebug, port)

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    start_server()

