import json

from flask import Response
from flask_restful import fields, marshal
from flask_security import current_user, login_required
from flask_security.decorators import roles_accepted

from database.models import Dish, Review
from resources.errors import (ReviewAlreadyExistsError, DeletingReviewError,
                              ReviewNotExistsError)
from resources.mixins import ProtectAuthorMixin, MultipleObjectApiMixin, SingleObjectApiMixin

review_fields = {
    'added_by': fields.String,
    'mark': fields.Integer,
    'comment': fields.String,
    'created_at': fields.DateTime(dt_format='rfc822')
}


class ReviewsApi(ProtectAuthorMixin, MultipleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=Review, not_unique_error=ReviewAlreadyExistsError, response_fields=review_fields,
                         *args, **kwargs)

    def get(self, dish_id):
        dish = Dish.objects.get(id=dish_id)
        return Response(json.dumps(marshal(dish.reviews, self.response_fields)),
                        mimetype="application/json", status=200)

    def _post_document(self, dish_id):
        dish = Dish.objects.get(id=dish_id)
        review = dish.add_review(**self.get_body())
        return {'id': str(review.id)}, 201

    @roles_accepted('user')
    def post(self, dish_id):
        return self._try_post(dish_id)


class ReviewApi(ProtectAuthorMixin, SingleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=Review, updating_error=ReviewNotExistsError, deleting_error=DeletingReviewError,
                         does_not_exist_error=ReviewNotExistsError, response_fields=review_fields, *args, **kwargs)

    def get_document(self, dish_id, review_id, *args, **kwargs):
        return Dish.objects.get(id=dish_id).reviews.get(_id=review_id)

    def _put_document(self, document_id, *args, **kwargs):
        dish = Dish.objects.get(id=document_id)
        dish.update_review(**self.get_body())
        return '', 200

    @roles_accepted('user')
    def put(self, dish_id, review_id):
        return self._try_put(dish_id)

    def _delete_document(self, dish_id, review_id,  *args, **kwargs):
        dish = Dish.objects.get(id=dish_id)
        review = dish.reviews.get(_id=review_id)
        if review.added_by.id == current_user.id or current_user.has_role('admin'):
            dish.update(pull__reviews___id=review_id)
            dish.save()
            return '', 200
        else:
            return '', 302

    @login_required
    def delete(self, dish_id, review_id):
        return self._try_delete(dish_id, review_id)

    @login_required
    def get(self, dish_id, review_id):
        return self._try_get(dish_id, review_id)
