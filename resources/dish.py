from database.models import Dish

from mongoengine.errors import (FieldDoesNotExist, NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError)

from resources.errors import (SchemaValidationError, DishAlreadyExistsError, InternalServerError, UpdatingDishError,
                              DeletingDishError, DishNotExistsError)

from flask import Response, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required


class DishesApi(Resource):
    def get(self):
        dish = Dish.objects().to_json()
        return Response(dish, mimetype="application/json", status=200)

    @jwt_required
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
    @jwt_required
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

    @jwt_required
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
