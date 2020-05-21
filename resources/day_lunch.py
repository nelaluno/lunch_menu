import json
from datetime import datetime

from flask import Response
from flask_restful import fields, marshal

from database.models import DayLunch
from resources.mixins import MultipleObjectApiMixin
from resources.dish import dish_fields

day_lunch_fields = {
    'weekday': fields.Integer,
    'lunch_set': fields.Nested({
        row_name: fields.Nested(dish_fields) for row_name in ['position_1', 'position_2', 'position_3']
    }),
    'price': fields.Price(decimals=2)
}


class DayLunchApi(MultipleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=DayLunch, response_fields=day_lunch_fields, *args, **kwargs)

    def get(self):
        return Response(
            json.dumps(marshal(DayLunch.objects.get(weekday=datetime.weekday(datetime.today())).to_dict(),
                               self.response_fields)),
            mimetype="application/json",
            status=200)
