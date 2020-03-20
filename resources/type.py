from database.models import Type

from mongoengine.errors import (FieldDoesNotExist, NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError)

from resources.errors import (SchemaValidationError, TypeAlreadyExistsError, InternalServerError, UpdatingTypeError,
                              DeletingTypeError, TypeNotExistsError)

from flask import Response, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask_security.decorators import roles_accepted


class TypesApi(Resource):
    def get(self):
        type = Type.objects().to_json()
        return Response(type, mimetype="application/json", status=200)

    @roles_accepted('admin')
    def post(self):
        try:
            body = request.get_json()
            type = Type(**body).save()
            return {'id': str(type.id)}, 200
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except NotUniqueError:
            raise TypeAlreadyExistsError
        except Exception as e:
            raise InternalServerError(e)


class TypeApi(Resource):
    @roles_accepted('admin')
    def put(self, type_id):
        try:
            body = request.get_json()
            Type.objects.get(id=type_id).update(**body)
            return '', 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise UpdatingTypeError
        except Exception:
            raise InternalServerError

    # todo fix bug
    @roles_accepted('admin')
    def delete(self, type_id):
        try:
            type = Type.objects.get(id=type_id)
            type.delete()
            return '', 200
        except DoesNotExist:
            raise DeletingTypeError
        except Exception:
            raise InternalServerError

    def get(self, type_id):
        try:
            type = Type.objects().get(id=type_id).to_json()
            return Response(type, mimetype="application/json", status=200)
        except DoesNotExist:
            raise TypeNotExistsError
        except Exception:
            raise InternalServerError
