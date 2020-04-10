from database.models import Dish, Type, Category, User

from mongoengine.errors import (FieldDoesNotExist, NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError)

from resources.errors import (SchemaValidationError, DishAlreadyExistsError, InternalServerError, UpdatingDishError,
                              DeletingDishError, DishNotExistsError)

from flask import Response, request
from flask_restful import Resource, marshal_with
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_security.decorators import roles_accepted
from resources.mixins import MultipleObjectApiMixin, SingleObjectApiMixin


# resource_fields = {'task':   fields.String,'uri':    fields.Url('todo_ep')}
# like через дополнительное поле option

class DishesApi(MultipleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=Dish, not_unique_error=DishAlreadyExistsError, *args, **kwargs)

    # @marshal_with(resource_fields)
    def get(self):
        request_args = request.args

        filter_query = {}
        for key, filter_key in [('name', 'name'),
                                ('type', 'type__name'),
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

    @jwt_required
    def liked(self, type_id=None, category_id=None):
        pass


class DishApi(SingleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=Dish, updating_error=UpdatingDishError, deleting_error=DeletingDishError,
                         does_not_exist_error=DishNotExistsError, *args, **kwargs)


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
