from database.models import Category

from mongoengine.errors import (FieldDoesNotExist, NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError)

from resources.errors import (SchemaValidationError, CategoryAlreadyExistsError, InternalServerError,
                              UpdatingCategoryError, DeletingCategoryError, CategoryNotExistsError)

from flask import Response, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask_security.decorators import roles_accepted


class CategoriesApi(Resource):
    def get(self):
        category = Category.objects().to_json()
        return Response(category, mimetype="application/json", status=200)

    @roles_accepted('admin')
    def post(self):
        try:
            body = request.get_json()
            category = Category(**body).save()
            return {'id': str(category.id)}, 201
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except NotUniqueError:
            raise CategoryAlreadyExistsError
        except Exception as e:
            raise InternalServerError(e)


class CategoryApi(Resource):
    @roles_accepted('admin')
    def put(self, category_id):
        try:
            body = request.get_json()
            Category.objects.get(id=category_id).update(**body)
            return '', 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise UpdatingCategoryError
        except Exception:
            raise InternalServerError

    # todo fix bug
    @roles_accepted('admin')
    def delete(self, category_id):
        try:
            Category.objects.get(id=category_id).delete()
            return '', 200
        except DoesNotExist:
            raise DeletingCategoryError
        except Exception:
            raise InternalServerError

    def get(self, category_id):
        try:
            category = Category.objects().get(id=category_id).to_json()
            return Response(category, mimetype="application/json", status=200)
        except DoesNotExist:
            raise CategoryNotExistsError
        except Exception:
            raise InternalServerError
