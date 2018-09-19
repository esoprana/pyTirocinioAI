import json

from progTiroc.api import create_api

from sanic import Sanic
from sanic_swagger import openapi_blueprint

api = create_api()

app = Sanic(__name__)
app.register_blueprint(api)
app.register_blueprint(openapi_blueprint)

request, response = app.test_client.get('/openapi/spec.json')

with open("docs/_static/swagger.json", "w") as f:
    f.write(
        json.dumps(
            response.json, sort_keys=True, indent=4, separators=(',', ': ')))
