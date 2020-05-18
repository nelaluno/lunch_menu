import json

from flask import Response, request
from flask_restful import fields, marshal
from flask_security import current_user, login_required
from mongoengine.queryset.visitor import Q

from database.models import Dish, Type, Category
from resources.errors import (DishAlreadyExistsError, UpdatingDishError, DeletingDishError, DishNotExistsError)
from resources.mixins import MultipleObjectApiMixin, SingleObjectApiMixin
from resources.review import review_fields

# resource_fields = {'task':   fields.String,'uri':    fields.Url('todo_ep')}
# like через дополнительное поле option

dish_fields = {
    'id': fields.String,  # URLField
    'name': fields.String,
    'description': fields.String,
    'price': fields.Float,
    'category': fields.String(attribute='category.name'),
    'type': fields.String(attribute='type.name'),
    'availability': fields.Boolean,
    # 'picture': fields.I,
    'reviews': fields.List(fields.Nested(review_fields)),
    'rating': fields.Float
}


class DishesApi(MultipleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=Dish, not_unique_error=DishAlreadyExistsError, response_fields=dish_fields,
                         *args, **kwargs)

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

        return Response(
            json.dumps(marshal([dish.to_dict() for dish in dishes], self.response_fields)),
            mimetype="application/json",
            status=200)

    @login_required
    def liked(self, type_id=None, category_id=None):
        pass


class DishApi(SingleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=Dish, updating_error=UpdatingDishError, deleting_error=DeletingDishError,
                         does_not_exist_error=DishNotExistsError, response_fields=dish_fields, *args, **kwargs)
