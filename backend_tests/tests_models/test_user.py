from backend_tests.framework.asserts import assert_data_are_equal
from random import randint
from hamcrest import assert_that, is_, equal_to, is_in, not_

import pytest


def check_user_data(user_document, exp_data):
    assert_data_are_equal(
        {'email': [user_document.email, exp_data['email']],
         'password': [user_document.check_password(exp_data['password']), True],
         'active': [user_document.active, exp_data.get('is_active', True)],
         'is_active': [user_document.is_active, exp_data.get('is_active', True)],
         'favorites': [user_document.favorites, exp_data.get('favorites', [])],
         'roles': [[role.name for role in user_document.roles] or [None], exp_data.get('role_names', [])]})


class TestUserModel:
    @pytest.mark.parametrize('role', [None, 'user', 'admin'])
    def test_create_user_with_role(self, create_user, role):
        user_data = dict(email='{}_user{}@gmail.com'.format(role or 'simple', randint(1, 10000)),
                         password='{}_user_password'.format(role or 'simple'),
                         role_names=[role])
        new_user = create_user(**user_data)
        check_user_data(new_user, user_data)

    def test_user_delete_review(self, create_dish, create_user, create_review):
        user = create_user()
        dish = create_dish()
        create_review(with_deleting=False, dish=dish, added_by=user.id)
        dish.delete_review(user)
        user.reload()

    @pytest.mark.skip("Не обновляется список")
    def test_user_delete_role(self, create_user, create_role):
        new_role = create_role(with_deleting=False)
        user = create_user(role_names=[new_role.name])
        assert_that(user.roles[0], new_role)
        new_role.delete()
        user.reload()
        assert_that(user.roles, is_([]))

    @pytest.mark.parametrize('is_favorite', [True, False])
    def test_is_favorite(self, create_user, create_dish, is_favorite):
        fav_dish = create_dish()
        new_user = create_user(favorites=[fav_dish.id] if is_favorite else [])
        assert_that(new_user.is_favorite(fav_dish), equal_to(is_favorite))

    @pytest.mark.parametrize('is_favorite', [True, False])
    def test_like_dish(self, create_user, create_dish, is_favorite):
        fav_dish = create_dish()
        new_user = create_user(favorites=[fav_dish.id] if is_favorite else [])
        new_user.like_dish(fav_dish)
        new_user.reload()
        assert_that(fav_dish, is_in(new_user.favorites))

    @pytest.mark.parametrize('is_favorite', [True, False])
    def test_unlike_dish(self, create_user, create_dish, is_favorite):
        fav_dish = create_dish()
        new_user = create_user(favorites=[fav_dish.id] if is_favorite else [])
        new_user.unlike_dish(fav_dish)
        new_user.reload()
        assert_that(fav_dish, not_(is_in(new_user.favorites)))
