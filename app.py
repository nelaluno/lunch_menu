import os

from flask import Flask
# from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_restful import Api
from flask_security import Security

from database.db import initialize_db
from database.models import user_datastore
from resources.errors import errors
from resources.routes import initialize_routes

app = Flask(__name__)
app.config.from_pyfile('settings.cfg')
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static/img/uploads')


# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


api = Api(app, errors=errors)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
mail = Mail(app)
security = Security(app, user_datastore)

initialize_db(app)
initialize_routes(api)
