from database.models import Dish, Type, Category

from mongoengine.errors import (FieldDoesNotExist, NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError)

from resources.errors import (SchemaValidationError, DishAlreadyExistsError, InternalServerError, UpdatingDishError,
                              DeletingDishError, DishNotExistsError)

from flask import Response, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask_security.decorators import roles_accepted


class DishesApi(Resource):
    def get(self, type_id=None, category_id=None):
        dish = Dish.objects(type__id=type_id, category__id=category_id).to_json()  # order_by будет ли работать при None
        return Response(dish, mimetype="application/json", status=200)

    @roles_accepted('admin')
    def post(self):
        try:
            body = request.get_json()
            dish = Dish(**body).save()
            id = dish.id
            return {'id': str(id)}, 200
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except NotUniqueError:
            raise DishAlreadyExistsError
        except Exception as e:
            raise InternalServerError


class DishApi(Resource):
    @roles_accepted('admin')
    def put(self, dish_id):
        try:
            body = request.get_json()
            Dish.objects.get(id=dish_id).update(**body)
            return '', 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise UpdatingDishError
        except Exception:
            raise InternalServerError

    @roles_accepted('admin')
    def delete(self, dish_id):
        try:
            Dish.objects.get(id=dish_id).delete()
            return '', 200
        except DoesNotExist:
            raise DeletingDishError
        except Exception:
            raise InternalServerError

    def get(self, dish_id):
        try:
            dish = Dish.objects().get(id=dish_id).to_json()
            return Response(dish, mimetype="application/json", status=200)
        except DoesNotExist:
            raise DishNotExistsError
        except Exception:
            raise InternalServerError
