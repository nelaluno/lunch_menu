from .dish import DishApi, DishesApi
from .auth import SignupApi, LoginApi
from .review import ReviewApi, ReviewsApi
from .type import TypeApi, TypesApi


# from .reset_password import ForgotPassword, ResetPassword


def initialize_routes(api):
    api.add_resource(DishesApi, '/api/dishes/<type_id>#<category_id>')
    api.add_resource(DishApi, '/api/dishes/<dish_id>')

    api.add_resource(TypesApi, '/api/types/')
    api.add_resource(TypeApi, '/api/types/<type_id>')

    api.add_resource(SignupApi, '/api/auth/signup')
    api.add_resource(LoginApi, '/api/auth/login')

    api.add_resource(ReviewsApi, '/api/dishes/<dish_id>/reviews')
    api.add_resource(ReviewApi, '/api/dishes/<dish_id>/reviews/<review_id>')

    # api.add_resource(ForgotPassword, '/lunch_menu/auth/forgot')
    # api.add_resource(ResetPassword, '/lunch_menu/auth/reset')
