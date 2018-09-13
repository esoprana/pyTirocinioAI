from flask import Flask
import json

from progTiroc.api import create_api

blue, api = create_api()

app = Flask(__name__)
app.register_blueprint(blue)

with app.test_request_context():
    with open("docs/_static/swagger.json", "w") as f:
        f.write(
            json.dumps(
                api.__schema__,
                sort_keys=True,
                indent=4,
                separators=(',', ': ')))
