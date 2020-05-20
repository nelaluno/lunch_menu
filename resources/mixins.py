import json

from flask import Response, request
from flask_restful import Resource, marshal
from flask_security import current_user
from flask_security.decorators import roles_accepted
from mongoengine.errors import (FieldDoesNotExist, NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError)

from resources.errors import (SchemaValidationError, InternalServerError)


class BasicMixin(Resource):
    def get_body(self):
        return request.get_json()


class ProtectAuthorMixin(BasicMixin):
    def get_body(self):
        body = request.get_json()
        body['added_by'] = current_user.id
        return body


class MultipleObjectApiMixin(BasicMixin):
    def __init__(self, collection, not_unique_error, response_fields={}, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collection = collection
        self.not_unique_error = not_unique_error
        self.response_fields = response_fields

    def get(self, *args):
        documents = self.collection.objects()
        if self.response_fields:
            response = json.dumps(marshal([doc for doc in documents], self.response_fields))
        else:
            response = documents.to_json()
        return Response(response, mimetype="application/json", status=200)

    def _post_document(self, *args, **kwargs):
        document = self.collection(**self.get_body()).save()
        return {'id': str(document.id)}, 201

    def _try_post(self, *args, **kwargs):
        try:
            return self._post_document(*args, **kwargs)
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except NotUniqueError:
            raise self.not_unique_error
        except Exception as e:
            raise InternalServerError(e)

    @roles_accepted('admin')
    def post(self):
        return self._try_post()


class SingleObjectApiMixin(BasicMixin):
    def __init__(self, collection, updating_error, deleting_error, does_not_exist_error, response_fields={}, *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.collection = collection
        self.updating_error = updating_error
        self.deleting_error = deleting_error
        self.does_not_exist_error = does_not_exist_error
        self.response_fields = response_fields

    def get_document(self, document_id, *args, **kwargs):
        return self.collection.objects.get(id=document_id)

    def _put_document(self, document_id, *args, **kwargs):
        self.get_document(document_id).update(**self.get_body())
        return '', 200

    def _try_put(self, document_id, *args, **kwargs):
        try:
            return self._put_document(document_id, *args, **kwargs)
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise self.updating_error
        except Exception:
            raise InternalServerError

    @roles_accepted('admin')
    def put(self, document_id, *args, **kwargs):
        return self._try_put(document_id, *args, **kwargs)

    def _delete_document(self, document_id, *args, **kwargs):
        self.get_document(document_id).delete()
        return '', 200

    def _try_delete(self, document_id, *args, **kwargs):
        try:
            return self._delete_document(document_id, *args, **kwargs)
        except DoesNotExist:
            raise self.deleting_error
        except Exception:
            raise InternalServerError

    @roles_accepted('admin')
    def delete(self, document_id, *args, **kwargs):
        return self._try_delete(document_id, *args, **kwargs)

    def _get_document(self, document_id, *args, **kwargs):
        document = self.get_document(document_id, *args, **kwargs)
        if self.response_fields:
            response = json.dumps(marshal(document, self.response_fields))
        else:
            response = document.to_json()
        return Response(response, mimetype="application/json", status=200)

    def _try_get(self, document_id, *args, **kwargs):
        try:
            return self._get_document(document_id, *args, **kwargs)
        except DoesNotExist:
            raise self.does_not_exist_error
        except Exception as e:
            raise InternalServerError(e)

    def get(self, document_id, *args, **kwargs):
        return self._try_get(document_id, *args, **kwargs)
