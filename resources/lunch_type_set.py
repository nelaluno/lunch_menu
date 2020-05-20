from flask_restful import fields

from database.models import LunchTypeSet
from resources.mixins import MultipleObjectApiMixin, SingleObjectApiMixin

lunch_type_set_fields = {
    'id': fields.String,
    'position_1': fields.String(attribute='position_1.name'),
    'position_2': fields.String(attribute='position_2.name'),
    'position_3': fields.String(attribute='position_3.name'),
    'sale': fields.Price(decimals=2)
}


class LunchTypeSetsApi(MultipleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=LunchTypeSet, response_fields=lunch_type_set_fields, *args, **kwargs)


class LunchTypeSetApi(SingleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=LunchTypeSet, response_fields=lunch_type_set_fields, *args, **kwargs)
