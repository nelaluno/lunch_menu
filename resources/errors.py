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


class ReviewAlreadyExistsError(Exception):
    pass


class UpdatingReviewError(Exception):
    pass


class DeletingReviewError(Exception):
    pass


class ReviewNotExistsError(Exception):
    pass


class EmailAlreadyExistsError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


class EmailDoesNotExistsError(Exception):
    pass


class BadTokenError(Exception):
    pass


class TypeAlreadyExistsError(Exception):
    pass


class UpdatingTypeError(Exception):
    pass


class DeletingTypeError(Exception):
    pass


class TypeNotExistsError(Exception):
    pass


class CategoryAlreadyExistsError(Exception):
    pass


class UpdatingCategoryError(Exception):
    pass


class DeletingCategoryError(Exception):
    pass


class CategoryNotExistsError(Exception):
    pass


errors_templates = {"{}AlreadyExistsError": {"message": "{} with given name already exists",
                                             "status": 400},
                    "Updating{}Error": {"message": "Updating {} added by other is forbidden",
                                        "status": 403,
                                        "lower": True},
                    "Deleting{}Error": {"message": "Deleting {} added by other is forbidden",
                                        "status": 403,
                                        "lower": True},
                    "{}NotExistsError": {"message": "{} with given id doesn't exists",
                                         "status": 400},
                    }

errors = {
    "InternalServerError": {
        "message": "Something went wrong",
        "status": 500
    },
    "SchemaValidationError": {
        "message": "Request is missing required fields",
        "status": 400
    },
    # "DishAlreadyExistsError": {
    #     "message": "Dish with given name already exists",
    #     "status": 400
    # },
    # "UpdatingDishError": {
    #     "message": "Updating dish added by other is forbidden",
    #     "status": 403
    # },
    # "DeletingDishError": {
    #     "message": "Deleting dish added by other is forbidden",
    #     "status": 403
    # },
    # "DishNotExistsError": {
    #     "message": "Dish with given id doesn't exists",
    #     "status": 400
    # },
    # "EmailAlreadyExistsError": {
    #     "message": "User with given email address already exists",
    #     "status": 400
    # },
    # "UnauthorizedError": {
    #     "message": "Invalid username or password",
    #     "status": 401
    # },
    # "ReviewAlreadyExistsError": {
    #     "message": "Review with given name already exists",
    #     "status": 400
    # },
    # "UpdatingReviewError": {
    #     "message": "Updating rating added by other is forbidden",
    #     "status": 403
    # },
    # "DeletingReviewError": {
    #     "message": "Deleting rating added by other is forbidden",
    #     "status": 403
    # },
    # "ReviewNotExistsError": {
    #     "message": "Review with given id doesn't exists",
    #     "status": 400
    # },
    "EmailDoesNotExistsError": {
        "message": "Couldn't find the user with given email address",
        "status": 400
    },
    "BadTokenError": {
        "message": "Invalid token",
        "status": 403
    },
}

for obj_name in ['Dish', 'Review', 'Type', 'Category', 'User']:
    for err_name, err_params in errors_templates.items():
        lower = err_params.get('lower')
        name = err_name.format(obj_name)
        errors[name] = {
            "message": err_params.get("message").format(obj_name.lower() if lower else obj_name),
            "status": err_params.get("status")}
