from .dish import DishApi, DishesApi
from .auth import SignupApi, LoginApi
from .rating import RatingApi, RatingsApi
# from .reset_password import ForgotPassword, ResetPassword


def initialize_routes(api):
    api.add_resource(DishesApi, '/api/dishes')
    api.add_resource(DishApi, '/api/dishes/<dish_id>')

    api.add_resource(SignupApi, '/api/auth/signup')
    api.add_resource(LoginApi, '/api/auth/login')

    api.add_resource(RatingsApi, '/api/dishes/<dish_id>/rating')
    api.add_resource(RatingApi, '/api/dishes/<dish_id>/rating/<rating_id>')

    # api.add_resource(ForgotPassword, '/lunch_menu/auth/forgot')
    # api.add_resource(ResetPassword, '/lunch_menu/auth/reset')
