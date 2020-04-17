from database.models import Dish, Review, User

from flask import Response, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_security.decorators import roles_accepted

from mongoengine.errors import (FieldDoesNotExist, NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError)

from resources.errors import (SchemaValidationError, ReviewAlreadyExistsError, InternalServerError, UpdatingReviewError,
                              DeletingReviewError, ReviewNotExistsError)
from resources.mixins import SingleObjectApiMixin


class ReviewsApi(Resource):
    def get(self, dish_id):
        dish = Dish.objects.get(id=dish_id)
        return Response(dish.reviews.to_json(), mimetype="application/json", status=200)

    @roles_accepted('user')
    def post(self, dish_id):
        try:
            body = request.get_json()
            user = User.objects.get(id=get_jwt_identity())
            dish = Dish.objects.get(id=dish_id)
            review = dish.add_review(added_by=user, **body)

            return {'id': str(review.id)}, 201
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except NotUniqueError:
            raise ReviewAlreadyExistsError
        except Exception as e:
            raise InternalServerError


class ReviewApi(Resource):
    @roles_accepted('user')
    def put(self, dish_id, review_id):
        try:
            dish = Dish.objects.get(id=dish_id)
            # dish.add_review(added_by=User.objects.get(id=get_jwt_identity()))
            review = Review.objects.get(id=review_id)
            body = request.get_json()
            review.update(**body)
            return '', 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise ReviewNotExistsError
        except Exception:
            raise InternalServerError

    @jwt_required
    def delete(self, review_id):
        try:
            user = User.objects.get(id=get_jwt_identity())
            Review.objects.get(id=review_id, added_by=user).delete()
            return '', 200
        except DoesNotExist:
            raise DeletingReviewError
        except Exception:
            raise InternalServerError

    @jwt_required
    def get(self, review_id):  # SingleObjectApiMixin
        try:
            review = Review.objects().get(id=review_id).to_json()
            return Response(review, mimetype="application/json", status=200)
        except DoesNotExist:
            raise ReviewNotExistsError
        except Exception:
            raise InternalServerError
