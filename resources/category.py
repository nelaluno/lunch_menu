from database.models import Category

from mongoengine.errors import (FieldDoesNotExist, NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError)

from resources.errors import (SchemaValidationError, CategoryAlreadyExistsError, InternalServerError,
                              UpdatingCategoryError, DeletingCategoryError, CategoryNotExistsError)

from flask import Response, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask_security.decorators import roles_accepted
from resources.mixins import MultipleObjectApiMixin, SingleObjectApiMixin


class CategoriesApi(MultipleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=Category, not_unique_error=CategoryAlreadyExistsError, *args, **kwargs)


class CategoryApi(SingleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=Category, updating_error=UpdatingCategoryError,
                         deleting_error=DeletingCategoryError, does_not_exist_error=CategoryNotExistsError,
                         *args, **kwargs)
