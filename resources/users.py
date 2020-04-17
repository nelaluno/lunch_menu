from flask import Response, request
from flask_jwt_extended import jwt_required, get_jwt_claims
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_restful import Resource
from flask_security.decorators import roles_accepted

from mongoengine import FieldDoesNotExist, NotUniqueError, DoesNotExist, InvalidQueryError

from resources.errors import (InternalServerError, SchemaValidationError, EmailAlreadyExistsError,
                              DeletingUserError, UpdatingUserError)
from database.models import User
from resources.mixins import SingleObjectApiMixin


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
            user.save()
            return {'id': user.get_id()}, 201
        except FieldDoesNotExist:
            raise SchemaValidationError
        except NotUniqueError:
            raise EmailAlreadyExistsError
        except Exception:
            raise InternalServerError


class UserApi(SingleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=User, updating_error=UpdatingUserError,
                         deleting_error=DeletingUserError, does_not_exist_error=DoesNotExist, *args, **kwargs)
