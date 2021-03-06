from .auth import SignupApi, LoginApi, LogoutApi
from .category import CategoriesApi, CategoryApi
from .common_review import CommonReviewApi, CommonReviewsApi
from .dish import DishApi, DishesApi
from .review import ReviewApi, ReviewsApi
from .type import TypeApi, TypesApi
from .lunch_type_set import LunchTypeSetApi, LunchTypeSetsApi
from .day_lunch import DayLunchApi
from .images import DishImage
from .order import OrdersApi


# from .reset_password import ForgotPassword, ResetPassword


def initialize_routes(api):
    api.add_resource(DishesApi, '/api/dishes')
    api.add_resource(DishApi, '/api/dishes/<document_id>')

    api.add_resource(DishImage, '/api/dish_images/<document_id>')

    api.add_resource(CategoriesApi, '/api/categories')
    api.add_resource(CategoryApi, '/api/categories/<document_id>')

    api.add_resource(TypesApi, '/api/types')
    api.add_resource(TypeApi, '/api/types/<document_id>')

    api.add_resource(SignupApi, '/api/auth/signup')
    api.add_resource(LoginApi, '/api/auth/login')
    api.add_resource(LogoutApi, '/api/auth/logout')

    api.add_resource(ReviewsApi, '/api/dishes/<dish_id>/reviews')
    api.add_resource(ReviewApi, '/api/dishes/<dish_id>/reviews/<review_id>')

    api.add_resource(CommonReviewsApi, '/api/common_reviews')
    api.add_resource(CommonReviewApi, '/api/common_reviews/<document_id>')

    api.add_resource(LunchTypeSetsApi, '/api/lunch_type_set')
    api.add_resource(LunchTypeSetApi, '/api/lunch_type_set/<document_id>')

    api.add_resource(DayLunchApi, '/api/day_lunch')

    api.add_resource(OrdersApi, '/api/order_lunch')
    # api.add_resource(OrdersApi, '/api/order_lunch/<document_id>')

    # api.add_resource(ForgotPassword, '/lunch_menu/auth/forgot')
    # api.add_resource(ResetPassword, '/lunch_menu/auth/reset')
