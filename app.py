from flask import Flask
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from database.db import initialize_db
from resources.routes import initialize_routes
from resources.errors import errors

app = Flask(__name__)
app.config['DEBUG'] = True
app.config.from_pyfile('settings.cfg')

api = Api(app, errors=errors)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
mail = Mail(app)

app.config['MONGODB_SETTINGS'] = {'host': 'mongodb://localhost/lunch_menu'
                                  }

initialize_db(app)
initialize_routes(api)
