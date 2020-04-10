from backend_tests.framework.asserts import assert_data_are_equal
from database.models import Role
from hamcrest import assert_that, not_
from random import randint

import pytest


def check_user_data(user_document, exp_data):
    assert_data_are_equal(
        {'email': [user_document.email, exp_data['email']],
         'active': [user_document.active, exp_data.get('is_active', True)],
         'is_active': [user_document.is_active, exp_data.get('is_active', True)],
         'favorites': [user_document.favorites, exp_data.get('favorites', [])],
         'roles': [[role.name for role in user_document.roles] or [None], exp_data.get('role_names', [])]})
    assert_that(user_document.password, not_(exp_data['password']))


class TestUserModel:
    @pytest.mark.parametrize('role', [None, 'user', 'admin'])
    def test_create_user_with_role(self, create_user, role):
        user_data = dict(email='{}_user{}@gmail.com'.format(role or 'simple', randint(1, 10000)),
                         password='{}_user_password'.format(role or 'simple'),
                         role_names=[role])
        new_user = create_user(**user_data)
        check_user_data(new_user, user_data)
