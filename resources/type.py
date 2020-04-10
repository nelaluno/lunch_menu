from database.models import Type

from mongoengine.errors import (FieldDoesNotExist, NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError)

from resources.errors import (SchemaValidationError, TypeAlreadyExistsError, InternalServerError, UpdatingTypeError,
                              DeletingTypeError, TypeNotExistsError)

from flask import Response, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask_security.decorators import roles_accepted
from resources.mixins import MultipleObjectApiMixin, SingleObjectApiMixin


class TypesApi(MultipleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=Type, not_unique_error=TypeAlreadyExistsError, *args, **kwargs)

    collection = Type
    not_unique_error = TypeAlreadyExistsError


class TypeApi(SingleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=Type, updating_error=UpdatingTypeError, deleting_error=DeletingTypeError,
                         does_not_exist_error=TypeNotExistsError, *args, **kwargs)
