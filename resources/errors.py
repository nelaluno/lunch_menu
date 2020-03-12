class InternalServerError(Exception):
    pass


class SchemaValidationError(Exception):
    pass


class DishAlreadyExistsError(Exception):
    pass


class UpdatingDishError(Exception):
    pass


class DeletingDishError(Exception):
    pass


class DishNotExistsError(Exception):
    pass


class RatingAlreadyExistsError(Exception):
    pass


class UpdatingRatingError(Exception):
    pass


class DeletingRatingError(Exception):
    pass


class RatingNotExistsError(Exception):
    pass


class EmailAlreadyExistsError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


class EmailDoesnotExistsError(Exception):
    pass


class BadTokenError(Exception):
    pass


errors = {
    "InternalServerError": {
        "message": "Something went wrong",
        "status": 500
    },
    "SchemaValidationError": {
        "message": "Request is missing required fields",
        "status": 400
    },
    "DishAlreadyExistsError": {
        "message": "Dish with given name already exists",
        "status": 400
    },
    "UpdatingDishError": {
        "message": "Updating dish added by other is forbidden",
        "status": 403
    },
    "DeletingDishError": {
        "message": "Deleting dish added by other is forbidden",
        "status": 403
    },
    "DishNotExistsError": {
        "message": "Dish with given id doesn't exists",
        "status": 400
    },
    "EmailAlreadyExistsError": {
        "message": "User with given email address already exists",
        "status": 400
    },
    "UnauthorizedError": {
        "message": "Invalid username or password",
        "status": 401
    },
    "RatingAlreadyExistsError": {
        "message": "Rating with given name already exists",
        "status": 400
    },
    "UpdatingRatingError": {
        "message": "Updating rating added by other is forbidden",
        "status": 403
    },
    "DeletingRatingError": {
        "message": "Deleting rating added by other is forbidden",
        "status": 403
    },
    "RatingNotExistsError": {
        "message": "Rating with given id doesn't exists",
        "status": 400
    },
    "EmailDoesNotExistsError": {
        "message": "Couldn't find the user with given email address",
        "status": 400
    },
    "BadTokenError": {
        "message": "Invalid token",
        "status": 403
    },
}
