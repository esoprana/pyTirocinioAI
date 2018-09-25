from progTiroc import server_setup

if __name__ == '__main__':
    app = server_setup()

    app.run(
        host=app.config['INTERFACE'],
        port=app.config['PORT'],
        debug=app.config['DEBUG'])
