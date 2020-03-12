from database.models import Dish, Rating, User

from flask import Response, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from mongoengine.errors import (FieldDoesNotExist, NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError)

from resources.errors import (SchemaValidationError, RatingAlreadyExistsError, InternalServerError, UpdatingRatingError,
                              DeletingRatingError, RatingNotExistsError)


class RatingApi(Resource):
    def get(self):
        rating = Rating.objects().to_json()
        return Response(rating, mimetype="application/json", status=200)

    @jwt_required
    def post(self, dish_id):
        try:
            user_id = get_jwt_identity()
            body = request.get_json()
            user = User.objects.get(id=user_id)
            dish = Dish.objects.get(id=dish_id)
            rating = Rating(**body, added_by=user, dish=dish)
            rating.save()

            user.update(push__marks=rating)
            user.save()
            user.update(push__marks=rating)
            user.save()

            id = rating.id
            return {'id': str(id)}, 200
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except NotUniqueError:
            raise RatingAlreadyExistsError
        except Exception as e:
            raise InternalServerError


class RatingsApi(Resource):
    @jwt_required
    def put(self, dish_id, rating_id):  # разные индексы
        try:
            user_id = get_jwt_identity()
            # dish = Dish.objects.get(id=dish_id)
            rating = Rating.objects.get(id=rating_id, added_by=user_id)
            body = request.get_json()
            Rating.objects.get(id=rating_id).update(**body)
            return '', 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise RatingNotExistsError
        except Exception:
            raise InternalServerError

    @jwt_required
    def delete(self, index):
        try:
            user_id = get_jwt_identity()
            Rating.objects.get(id=index, added_by=user_id).delete()
            return '', 200
        except DoesNotExist:
            raise DeletingRatingError
        except Exception:
            raise InternalServerError

    def get(self, index):
        try:
            rating = Rating.objects().get(id=index).to_json()
            return Response(rating, mimetype="application/json", status=200)
        except DoesNotExist:
            raise RatingNotExistsError
        except Exception:
            raise InternalServerError
