import json

from flask import Response
from flask_restful import fields, marshal
from flask_security import current_user
from flask_security.decorators import roles_accepted

from database.models import Order, today_lunch, LunchSet, Dish
from resources.dish import dishes_fields
from resources.mixins import ProtectAuthorMixin, MultipleObjectApiMixin, SingleObjectApiMixin

order_fields = {
    'added_by': fields.String,
    'created_at': fields.DateTime(dt_format='rfc822'),
    'lunch_set': fields.Nested({
        row_name: fields.Nested(dishes_fields) for row_name in ['position_1', 'position_2', 'position_3']
    }),
    'price': fields.Price(decimals=2),
}


class OrdersApi(ProtectAuthorMixin, MultipleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=Order, response_fields=order_fields, *args, **kwargs)

    @roles_accepted('user')
    def get(self):
        orders = Order.objects.filter(added_by=current_user.id)
        return Response(json.dumps(marshal([order.to_dict() for order in orders], self.response_fields)),
                        mimetype="application/json", status=200)

    def _post_document(self):
        body = self.get_body()
        if body.get('is_day_lunch'):
            day_lunch = today_lunch()
            order = self.collection(added_by=body['added_by'], lunch_set=day_lunch.lunch_set,
                                    price=day_lunch.price).save()
        else:
            lunch_set = LunchSet(
                **{row_name: Dish.objects.get(id=body.get(row_name)) for row_name in
                   ['position_1', 'position_2', 'position_3']})
            order = self.collection(added_by=body['added_by'],
                                    lunch_set=lunch_set,
                                    price=lunch_set.price).save()
        return {'id': str(order.id)}, 201

    @roles_accepted('user')
    def post(self):
        return self._try_post()
