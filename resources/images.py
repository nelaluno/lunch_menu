import io

from flask import send_file
from flask_restful import Resource

from database.models import Dish


class DishImage(Resource):
    def get(self, document_id):
        """Dish image."""

        document = Dish.objects.get(id=document_id)

        return send_file(io.BytesIO(document.image.read()),
                         attachment_filename='{}.png'.format(document.name),
                         mimetype='image/png')
