import json
from random import randint

import pytest
from flask import url_for

from backend_tests.constans import UserData
from backend_tests.framework.asserts import assert_data_are_equal
from database.models import User, Role
from resources.auth import LoginApi, SignupApi
from resources.errors import EmailAlreadyExistsError

# from pytest_flask.fixtures import client

PASSWORD = 'simple_user_password'


@pytest.fixture(scope='function')
def delete_if_created():
    emails = []

    def store(email):
        emails.append(email)

    yield store

    for email in emails:
        if User.objects.filter(email=email).count() > 0:
            User.objects.get(email=email).delete()


class TestSingUpApi:
    resource_name = SignupApi.__name__.lower()

    def test_sing_up_simple(self, create_category, client, delete_if_created):
        email = 'simple_user_{}@gmail.com'.format(randint(1, 10000))
        delete_if_created(email)

        response = client.post(url_for(self.resource_name),
                               data=json.dumps({'email': email, 'password': PASSWORD}),
                               content_type='application/json')

        assert_data_are_equal({'status_code': [response.status_code, 201],
                               'count users by email': [User.objects.filter(email=email).count(), 1]})

        user = User.objects.get(email=email)
        assert_data_are_equal({'email': [user.email, email],
                               'password': [user.check_password(PASSWORD), True],
                               'roles': [user.roles, [Role.objects.get(name=UserData.USER_ROLE)]]})

    @pytest.mark.skip('непонятно, как ловить ошибки')
    def test_sing_up_duplicate_email(self, create_category, app, delete_if_created, create_user):
        user = create_user()
        app = app.test_client()

        with app.post(url_for(self.resource_name),
                      data=json.dumps({'email': user.email, 'password': PASSWORD}),
                      content_type='application/json',
                      follow_redirects=True):
            response = app.handle_exception(EmailAlreadyExistsError)

            assert_data_are_equal({'status_code': [response.status_code, 201],
                                   'count users by email': [User.objects.filter(email=user.email).count(), 1]})


class TestLoginApi:
    resource_name = LoginApi.__name__.lower()

    def test_login_correct(self, create_category, client, delete_if_created, create_hashed_user):
        user = create_hashed_user(password=PASSWORD)

        response = client.post(url_for(self.resource_name),
                               data=json.dumps({'email': user.email, 'password': PASSWORD}),
                               content_type='application/json')

        user.reload()
        assert_data_are_equal({'status_code': [response.status_code, 200],
                               'is_authenticated': [user.is_authenticated, True]})
