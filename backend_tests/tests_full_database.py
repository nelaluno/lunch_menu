from random import randint

import pytest

from backend_tests.constans import UserData


class TestFullDatabase:
    @pytest.mark.parametrize('name, description',
                             [('business lunch', 'business lunch'),
                              ('vitality', None),
                              ('soup bar', None),
                              ('le chief', None)])
    def test_category(self, create_category, name, description):
        create_category(with_deleting=False, name=name, description=description)

    @pytest.mark.parametrize('name, description',
                             [('soup', None),
                              ('hot', 'Hot dish'),
                              ('salad', None),
                              ('snack', None),
                              ('drink', None)])
    def test_type(self, create_type, name, description):
        create_type(name=name, description=description, with_deleting=True)

    @pytest.mark.parametrize('name, description',
                             [('admin', 'Administrator can manage dishes, types, categories and delete reviews.'),
                              ('user', 'User can manage his own reviews.')])
    def test_role(self, create_role, name, description):
        create_role(name=name, description=description, with_deleting=True)

    @pytest.mark.parametrize('role', [None, UserData.USER_ROLE, UserData.USER_ROLE, UserData.ADMIN_ROLE])
    def test_create_user_with_role(self, create_user, role):
        create_user(email='{}_user{}@gmail.com'.format(role or 'simple', randint(1, 10000)),
                    password=UserData.DEFAULT_PASSWORD,
                    role_names=[role], with_deleting=False)

    # @pytest.mark.parametrize('dish_data',
    #                          [{"name": "veggi rice",
    #                            "description": "just rice and vegetables",
    #                            "price": 200,
    #                            "category": Category.objects.get(name='business lunch'),
    #                            "type": Type.objects.get(name='hot'),
    #                            "availability": True,
    #                            "reviews": []},
    #                           {"name": "pizza",
    #                            "description": "italian pizza",
    #                            "price": 500,
    #                            "category": Category.objects.get(name='le chief'),
    #                            "type": Type.objects.get(name='snack'),
    #                            "availability": False,
    #                            "reviews": []}], ids=["veggi rice", "pizza"])
    # def test_dish_with_reviews(self, create_dish, dish_data):
    #     new_dish = create_dish(with_deleting=False, **dish_data)
    #     check_dish_data(new_dish, dish_data)
