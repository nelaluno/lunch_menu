from flask import Response, request
from flask_jwt_extended import jwt_required, get_jwt_claims
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_restful import Resource
from flask_security.decorators import roles_accepted

from mongoengine import FieldDoesNotExist, NotUniqueError, DoesNotExist, InvalidQueryError

from resources.errors import (InternalServerError, SchemaValidationError, EmailAlreadyExistsError,
                              DeletingUserError, UpdatingUserError)
from database.models import User


class UsersApi(Resource):
    @roles_accepted('admin')
    def get(self):
        try:
            users = User.objects().to_json()
            return Response(users, mimetype='application/json', status=200)
        except NoAuthorizationError:
            raise NoAuthorizationError
        except Exception:
            raise InternalServerError

    @roles_accepted('admin')
    def post(self):
        try:
            body = request.get_json()
            user = User(**body)
            user.hash_password()
            user.save()
            id = user.id
            return {'id': str(id)}, 201
        except FieldDoesNotExist:
            raise SchemaValidationError
        except NotUniqueError:
            raise EmailAlreadyExistsError
        except Exception:
            raise InternalServerError


class UserApi(Resource):
    @roles_accepted('admin')
    def delete(self, user_id):
        try:
            user = User.objects().get(id=user_id)
            user.delete()
            return 'None', 204
        except DoesNotExist:
            raise DeletingUserError
        except Exception:
            raise InternalServerError

    @roles_accepted('admin')
    def put(self, user_id):
        try:
            User.objects.get(id=user_id)
            body = request.get_json()
            User.objects.get(id=id).update(**body)
            return 'None', 204
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise UpdatingUserError
        except Exception:
            raise InternalServerError
