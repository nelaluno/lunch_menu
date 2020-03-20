from flask import Flask
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_security import Security
from database.db import initialize_db
from database.models import user_datastore
from resources.routes import initialize_routes
from resources.errors import errors

app = Flask(__name__)
app.config.from_pyfile('settings.cfg')

api = Api(app, errors=errors)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
mail = Mail(app)
security = Security(app, user_datastore)

initialize_db(app)
initialize_routes(api)
