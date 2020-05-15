from flask import Response, request
from flask_security import current_user, login_required
from mongoengine.queryset.visitor import Q

from database.models import Dish, Type, Category
from resources.errors import (DishAlreadyExistsError, UpdatingDishError, DeletingDishError, DishNotExistsError)
from resources.mixins import MultipleObjectApiMixin, SingleObjectApiMixin


# resource_fields = {'task':   fields.String,'uri':    fields.Url('todo_ep')}
# like через дополнительное поле option

class DishesApi(MultipleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=Dish, not_unique_error=DishAlreadyExistsError, *args, **kwargs)

    # @marshal_with(resource_fields)
    def get(self):
        request_args = request.args

        filter_query = Q()

        # not reference fields
        for key, filter_key, func in [('name', 'name', str),
                                      ('q', 'name__icontains', str),
                                      ('avail', 'availability', bool)]:
            value = request_args.get(key)
            if value is not None:
                filter_query = filter_query & Q(**{filter_key: func(value)})

        # reference fields
        for key, collection in [('type', Type),
                                ('category', Category)]:
            value = request_args.get(key)
            if value is not None:
                filter_query = filter_query & Q(**{key: collection.objects.get(name=request_args.get(key))})

        is_favorite = request_args.get('is_favorite', None)
        user = current_user

        if is_favorite and user:
            dishes = user.favorites.filter(filter_query)
        else:
            dishes = Dish.objects(filter_query)

        return Response(dishes.to_json(), mimetype="application/json", status=200)

    @login_required
    def liked(self, type_id=None, category_id=None):
        pass


class DishApi(SingleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=Dish, updating_error=UpdatingDishError, deleting_error=DeletingDishError,
                         does_not_exist_error=DishNotExistsError, *args, **kwargs)
