import json
from random import randint

import pytest
from flask import url_for

from backend_tests.constans import ResourceNames, UserData
from backend_tests.framework.asserts import assert_data_are_equal
from database.models import Dish
from resources.dish import DishApi, DishesApi


@pytest.fixture(scope='function')
def delete_if_created():
    names = []

    def store(name):
        names.append(name)

    yield store

    for name in names:
        if Dish.objects.filter(name=name).count() > 0:
            Dish.objects.get(name=name).delete()


class TestDishApi():
    resource_name = DishApi.__name__.lower()

    def test_get_dish_without_auth(self, create_dish, client):
        dish = create_dish()

        response = client.get(url_for(self.resource_name, document_id=dish.id),
                              content_type='application/json')

        assert_data_are_equal({'status_code': [response.status_code, 200],
                               'name': [response.json.get('name'), dish.name],
                               'description': [response.json.get('description'), dish.description]})

    @pytest.mark.parametrize('role', [None, UserData.USER_ROLE, UserData.ADMIN_ROLE])
    def test_get_dish_authenticated_user_roles(self, create_authenticated_user, create_dish, client, role):
        user, token = create_authenticated_user(role_names=[role])
        dish = create_dish()

        response = client.get(url_for(self.resource_name, document_id=dish.id),
                              headers={'Authentication-Token': token},
                              content_type='application/json')

        assert_data_are_equal({'status_code': [response.status_code, 200],
                               'name': [response.json.get('name'), dish.name],
                               'description': [response.json.get('description'), dish.description]})

    # todo добавить параметры
    def test_put_dish_without_auth(self, create_dish, client):
        old_name = 'old name'
        old_description = 'old description'
        dish = create_dish(description=old_description, name=old_name)

        response = client.put(url_for(self.resource_name, document_id=dish.id),
                              data=json.dumps({'description': 'new description'}),
                              content_type='application/json')

        dish.reload()
        assert_data_are_equal({'status_code': [response.status_code, 302],
                               'name': [dish.name, old_name],
                               'description': [dish.description, old_description]})

    # todo добавить параметры и тесты на неизменяемые параметры
    @pytest.mark.parametrize('role', [None, UserData.USER_ROLE, UserData.ADMIN_ROLE])
    def test_put_dish_with_auth(self, create_dish, client, create_authenticated_user, role):
        old_data = {'name': 'old name {}'.format(randint(1, 10000)),
                    'description': 'old description'}
        dish = create_dish(**old_data)
        _, token = create_authenticated_user(role_names=[role])

        new_data = {'name': 'new name {}'.format(randint(1, 10000)),
                    'description': 'new description'}
        response = client.put(url_for(self.resource_name, document_id=dish.id),
                              data=json.dumps(new_data),
                              headers={'Authentication-Token': token},
                              content_type='application/json')

        dish.reload()
        if role == UserData.ADMIN_ROLE:
            exp_code = 200
            exp_data = new_data
        else:
            exp_code = 302
            exp_data = old_data

        assert_data_are_equal({'status_code': [response.status_code, exp_code],
                               'name': [dish.name, exp_data['name']],
                               'description': [dish.description, exp_data['description']]})

    def test_delete_dish_without_auth(self, create_dish, client):
        dish = create_dish()

        response = client.delete(url_for(self.resource_name, document_id=dish.id),
                                 content_type='application/json')

        assert_data_are_equal({'status_code': [response.status_code, 302],
                               'count by id': [Dish.objects.filter(id=dish.id).count(), 1]})

    @pytest.mark.parametrize('role', [None, UserData.USER_ROLE, UserData.ADMIN_ROLE])
    def test_delete_dish_with_auth(self, create_dish, client, create_authenticated_user, role):
        dish = create_dish(with_deleting=role != UserData.ADMIN_ROLE)
        _, token = create_authenticated_user(role_names=[role])

        response = client.delete(url_for(self.resource_name, document_id=dish.id),
                                 headers={'Authentication-Token': token},
                                 content_type='application/json')

        if role == UserData.ADMIN_ROLE:
            exp_code = 200
            exp_count = 0
        else:
            exp_code = 302
            exp_count = 1

        assert_data_are_equal({'status_code': [response.status_code, exp_code],
                               'count by id': [Dish.objects.filter(id=dish.id).count(), exp_count]})

        # todo добавить тесты


class TestDishesApi():
    resource_name = DishesApi.__name__.lower()

    # todo обавить параметры
    def test_post_dish_without_auth(self, create_dish, client, delete_if_created):
        data = {'name': 'name {}'.format(randint(1, 10000)),
                'description': 'description',
                'price': randint(1, 10000)}
        delete_if_created(data['name'])

        response = client.post(url_for(self.resource_name),
                               data=json.dumps(data),
                               content_type='application/json')
        assert_data_are_equal({'status_code': [response.status_code, 302],
                               'count by id': [Dish.objects.filter(**data).count(), 0]})

    # todo обавить параметры
    @pytest.mark.parametrize('role', [None, UserData.USER_ROLE, UserData.ADMIN_ROLE])
    def test_post_dish_with_auth(self, create_authenticated_user, create_dish, client, delete_if_created, role):
        data = {'name': 'name {}'.format(randint(1, 10000)),
                'description': 'description',
                'price': randint(1, 10000)}
        delete_if_created(data['name'])

        _, token = create_authenticated_user(role_names=[role])

        if role == UserData.ADMIN_ROLE:
            exp_code = 201
            exp_count = 1
        else:
            exp_code = 302
            exp_count = 0

        response = client.post(url_for(self.resource_name),
                               data=json.dumps(data),
                               headers={'Authentication-Token': token},
                               content_type='application/json')
        assert_data_are_equal({'status_code': [response.status_code, exp_code],
                               'count by id': [Dish.objects.filter(**data).count(), exp_count]})

    @pytest.mark.skip("потом доделаю")
    @pytest.mark.parametrize('is_authenticated, role',
                             [(False, None), (True, None), (True, UserData.USER_ROLE), (True, UserData.ADMIN_ROLE)])
    def test_get_all_categories(self, create_hashed_user, create_dish, client, role, is_authenticated):
        if is_authenticated:
            user = create_hashed_user(role_names=[role])
            client.post(url_for(ResourceNames.LOGIN),
                        data=json.dumps({'email': user.email, 'password': UserData.DEFAULT_PASSWORD}),
                        content_type='application/json')

        dish = create_dish()
        response = client.get(url_for(self.resource_name))
