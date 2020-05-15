import json

from flask import Response, request
from flask_restful import Resource, fields, marshal
from flask_security import current_user, login_required
from flask_security.decorators import roles_accepted
from mongoengine.errors import (FieldDoesNotExist, NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError)

from database.models import Dish
from resources.errors import (SchemaValidationError, ReviewAlreadyExistsError, InternalServerError, DeletingReviewError,
                              ReviewNotExistsError)

resource_fields = {
    'added_by': fields.String,
    'mark': fields.Integer,
    'comment': fields.String,
    'created_at': fields.DateTime(dt_format='rfc822')
}


class ReviewsApi(Resource):
    def get(self, dish_id):
        dish = Dish.objects.get(id=dish_id)
        return Response(json.dumps(marshal(dish.reviews, resource_fields)), mimetype="application/json", status=200)

    @roles_accepted('user')
    def post(self, dish_id):
        try:
            body = request.get_json()
            body['added_by'] = current_user.id
            dish = Dish.objects.get(id=dish_id)
            review = dish.add_review(**body)

            return {'id': str(review.id)}, 201
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except NotUniqueError:
            raise ReviewAlreadyExistsError
        except Exception as e:
            raise InternalServerError


class ReviewApi(Resource):
    def get_body(self):
        body = request.get_json()
        body['added_by'] = current_user.id
        return body

    @roles_accepted('user')
    def put(self, dish_id, review_id):
        try:
            dish = Dish.objects.get(id=dish_id)
            dish.update_review(**self.get_body())
            return '', 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise ReviewNotExistsError
        except Exception:
            raise InternalServerError

    @login_required
    def delete(self, dish_id, review_id):
        try:
            dish = Dish.objects.get(id=dish_id)
            review = dish.reviews.get(_id=review_id)
            if review.added_by.id == current_user.id or current_user.has_role('admin'):
                dish.update(pull__reviews___id=review_id)
                dish.save()
                return '', 200
            else:
                return '', 302
        except DoesNotExist:
            raise DeletingReviewError
        except Exception:
            raise InternalServerError

    @login_required
    def get(self, dish_id, review_id):
        try:
            review = Dish.objects.get(id=dish_id).reviews.get(_id=review_id)
            return Response(json.dumps(marshal(review, resource_fields)), mimetype="application/json", status=200)
        except DoesNotExist:
            raise ReviewNotExistsError
        except Exception:
            raise InternalServerError
