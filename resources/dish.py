from database.models import Dish, Type, Category, User

from mongoengine.errors import (FieldDoesNotExist, NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError)

from resources.errors import (SchemaValidationError, DishAlreadyExistsError, InternalServerError, UpdatingDishError,
                              DeletingDishError, DishNotExistsError)

from flask import Response, request
from flask_restful import Resource, marshal_with
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_security.decorators import roles_accepted


# resource_fields = {'task':   fields.String,'uri':    fields.Url('todo_ep')}
# like через дополнительное поле option

class DishesApi(Resource):
    # @marshal_with(resource_fields)
    def get(self):
        request_args = request.args

        filter_query = {}
        for key, filter_key in [('type', 'type__name'),
                                ('category', 'category__name'),
                                ('q', 'name__icontains'),
                                ('avail', 'availability')]:
            value = request_args.get(key)
            if value is not None:
                filter_query[filter_key] = value

        is_favorite = request_args.get('is_favorite', None)
        current_user = get_jwt_identity()

        if is_favorite and current_user:
            dishes = current_user.favorites.get(**filter_query).to_json()
        else:
            dishes = Dish.objects(**filter_query).to_json()  # order_by будет ли работать при None

        return Response(dishes, mimetype="application/json", status=200)

    @roles_accepted('admin')
    def post(self):
        try:
            body = request.get_json()
            dish = Dish(**body).save()
            id = dish.id
            return {'id': str(id)}, 201
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except NotUniqueError:
            raise DishAlreadyExistsError
        except Exception as e:
            raise InternalServerError

    @jwt_required
    def liked(self, type_id=None, category_id=None):
        pass


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


@jwt_required
@roles_accepted('user')
def like(self, dish_id):
    dish = Dish.objects().get(id=dish_id)
    user = User.objects.get(id=get_jwt_identity())
    user.update(push__favorites=dish)
    return '', 200


@jwt_required
@roles_accepted('user')
def unlike(self, dish_id):
    dish = Dish.objects().get(id=dish_id)
    user = User.objects.get(id=get_jwt_identity())
    user.update(push__favorites=dish)
    return '', 200
