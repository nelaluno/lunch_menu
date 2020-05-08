from flask import Response, request
from flask_restful import Resource
from flask_security.decorators import roles_accepted
from mongoengine.errors import (FieldDoesNotExist, NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError)

from resources.errors import (SchemaValidationError, InternalServerError)


class MultipleObjectApiMixin(Resource):
    def __init__(self, collection, not_unique_error, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collection = collection
        self.not_unique_error = not_unique_error

    def get(self):
        document = self.collection.objects().to_json()
        return Response(document, mimetype="application/json", status=200)

    @roles_accepted('admin')
    def post(self):
        try:
            body = request.get_json()
            document = self.collection(**body).save()
            return {'id': str(document.id)}, 201
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except NotUniqueError:
            raise self.not_unique_error
        except Exception as e:
            raise InternalServerError(e)


class SingleObjectApiMixin(Resource):
    def __init__(self, collection, updating_error, deleting_error, does_not_exist_error, *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.collection = collection
        self.updating_error = updating_error
        self.deleting_error = deleting_error
        self.does_not_exist_error = does_not_exist_error

    @roles_accepted('admin')
    def put(self, document_id):
        try:
            body = request.get_json()
            self.collection.objects.get(id=document_id).update(**body)
            return '', 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise self.updating_error
        except Exception:
            raise InternalServerError

    @roles_accepted('admin')
    def delete(self, document_id):
        try:
            self.collection.objects.get(id=document_id).delete()
            return '', 200
        except DoesNotExist:
            raise self.deleting_error
        except Exception:
            raise InternalServerError

    def get(self, document_id):
        try:
            document = self.collection.objects().get(id=document_id).to_json()
            return Response(document, mimetype="application/json", status=200)
        except DoesNotExist:
            raise self.does_not_exist_error
        except Exception:
            raise InternalServerError
