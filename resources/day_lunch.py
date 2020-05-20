import json
from datetime import datetime

from flask import Response, request
from flask_restful import fields, marshal

from database.models import DayLunch
from resources.lunch_type_set import lunch_type_set_fields
from resources.mixins import MultipleObjectApiMixin

day_lunch_fields = {
    'weekday': fields.Integer,
    'lunch_set': fields.Nested(lunch_type_set_fields),
    'price': fields.Price(decimals=2)
}


class DayLunchApi(MultipleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=DayLunch, response_fields=day_lunch_fields, *args, **kwargs)

    def get(self):
        request_args = request.args
        return Response(
            json.dumps(marshal(DayLunch.objects.get(weekday=request_args.get('weekday', datetime.weekday())),
                               self.response_fields)),
            mimetype="application/json",
            status=200)
