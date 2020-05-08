from flask import request
from flask_restful import Resource
from flask_security import login_user
from mongoengine.errors import (FieldDoesNotExist, NotUniqueError, DoesNotExist)

from database.models import User, Role
from resources.errors import (SchemaValidationError, EmailAlreadyExistsError, UnauthorizedError,
                              InternalServerError)


class SignupApi(Resource):
    def post(self):
        try:
            body = request.get_json()
            user = User(**body)
            user.roles = [Role.objects.get(name='user').id]
            user.hash_password()
            user.save()
            return {'id': user.get_id()}, 201
        except FieldDoesNotExist:
            raise SchemaValidationError
        except NotUniqueError:
            raise EmailAlreadyExistsError
        except Exception as e:
            raise InternalServerError


class LoginApi(Resource):
    def post(self):
        try:
            body = request.get_json()
            user = User.objects.get(email=body.get('email'))
            if not user.check_password(body.get('password')):
                return {'error': 'Email or password is invalid'}, 401

            login_user(user)
            return user.get_auth_token(), 200
        except (UnauthorizedError, DoesNotExist):
            raise UnauthorizedError
        except Exception as e:
            raise InternalServerError

# class LogOutApi(Resource):
#     @jwt_required
#     def post(self):
#         try:
#             user = get_jwt_identity()
#             if not user.check_password(body.get('password')):
#                 return {'error': 'Email or password is invalid'}, 401
#
#             expires = datetime.timedelta(days=7)
#             access_token = create_access_token(identity=str(user.id), expires_delta=expires)
#             return {'token': access_token}, 200
#         except (UnauthorizedError, DoesNotExist):
#             raise UnauthorizedError
#         except Exception as e:
#             raise InternalServerError
