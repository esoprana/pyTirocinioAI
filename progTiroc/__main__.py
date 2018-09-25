import asyncio

from progTiroc import server_setup

if __name__ == '__main__':
    app = server_setup()

    app.run(host='0.0.0.0', port=app.config['PORT'], debug=app.config['DEBUG'])
