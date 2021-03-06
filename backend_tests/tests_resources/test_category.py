import json
from random import randint

import pytest
from flask import url_for

from backend_tests.constans import ResourceNames, UserData
from backend_tests.framework.asserts import assert_data_are_equal
from database.models import Category
from resources.category import CategoryApi, CategoriesApi


@pytest.fixture(scope='function')
def delete_if_created():
    names = []

    def store(name):
        names.append(name)

    yield store

    for name in names:
        if Category.objects.filter(name=name).count() > 0:
            Category.objects.get(name=name).delete()


class TestCategoryApi():
    resource_name = CategoryApi.__name__.lower()

    def test_get_category_without_auth(self, create_category, client):
        category = create_category()

        response = client.get(url_for(self.resource_name, document_id=category.id),
                              content_type='application/json')

        assert_data_are_equal({'status_code': [response.status_code, 200],
                               'name': [response.json.get('name'), category.name],
                               'description': [response.json.get('description'), category.description]})

    @pytest.mark.parametrize('role', [None, UserData.USER_ROLE, UserData.ADMIN_ROLE])
    def test_get_category_authenticated_user_roles(self, create_authenticated_user, create_category, client, role):
        user, token = create_authenticated_user(role_names=[role])
        category = create_category()

        response = client.get(url_for(self.resource_name, document_id=category.id),
                              headers={'Authentication-Token': token},
                              content_type='application/json')

        assert_data_are_equal({'status_code': [response.status_code, 200],
                               'name': [response.json.get('name'), category.name],
                               'description': [response.json.get('description'), category.description]})

    def test_put_category_without_auth(self, create_category, client):
        old_name = 'old name'
        old_description = 'old description'
        category = create_category(description=old_description, name=old_name)

        response = client.put(url_for(self.resource_name, document_id=category.id),
                              data=json.dumps({'description': 'new description'}),
                              content_type='application/json')

        category.reload()
        assert_data_are_equal({'status_code': [response.status_code, 302],
                               'name': [category.name, old_name],
                               'description': [category.description, old_description]})

    @pytest.mark.parametrize('role', [None, UserData.USER_ROLE, UserData.ADMIN_ROLE])
    def test_put_category_with_auth(self, create_category, client, create_authenticated_user, role):
        old_data = {'name': 'old name {}'.format(randint(1, 10000)),
                    'description': 'old description'}
        category = create_category(**old_data)
        _, token = create_authenticated_user(role_names=[role])

        new_data = {'name': 'new name {}'.format(randint(1, 10000)),
                    'description': 'new description'}
        response = client.put(url_for(self.resource_name, document_id=category.id),
                              data=json.dumps(new_data),
                              headers={'Authentication-Token': token},
                              content_type='application/json')

        category.reload()
        if role == UserData.ADMIN_ROLE:
            exp_code = 200
            exp_data = new_data
        else:
            exp_code = 302
            exp_data = old_data

        assert_data_are_equal({'status_code': [response.status_code, exp_code],
                               'name': [category.name, exp_data['name']],
                               'description': [category.description, exp_data['description']]})

    def test_delete_category_without_auth(self, create_category, client):
        category = create_category()

        response = client.delete(url_for(self.resource_name, document_id=category.id),
                                 content_type='application/json')

        assert_data_are_equal({'status_code': [response.status_code, 302],
                               'count by id': [Category.objects.filter(id=category.id).count(), 1]})

    @pytest.mark.parametrize('role', [None, UserData.USER_ROLE, UserData.ADMIN_ROLE])
    def test_delete_category_with_auth(self, create_category, client, create_authenticated_user, role):
        category = create_category(with_deleting=role != UserData.ADMIN_ROLE)
        _, token = create_authenticated_user(role_names=[role])

        response = client.delete(url_for(self.resource_name, document_id=category.id),
                                 headers={'Authentication-Token': token},
                                 content_type='application/json')

        if role == UserData.ADMIN_ROLE:
            exp_code = 200
            exp_count = 0
        else:
            exp_code = 302
            exp_count = 1

        assert_data_are_equal({'status_code': [response.status_code, exp_code],
                               'count by id': [Category.objects.filter(id=category.id).count(), exp_count]})


class TestCategoriesApi():
    resource_name = CategoriesApi.__name__.lower()

    def test_post_category_without_auth(self, create_category, client, delete_if_created):
        data = {'name': 'name {}'.format(randint(1, 10000)),
                'description': 'description'}
        delete_if_created(data['name'])

        response = client.post(url_for(self.resource_name),
                               data=json.dumps(data),
                               content_type='application/json')
        assert_data_are_equal({'status_code': [response.status_code, 302],
                               'count by id': [Category.objects.filter(**data).count(), 0]})

    @pytest.mark.parametrize('role', [None, UserData.USER_ROLE, UserData.ADMIN_ROLE])
    def test_post_category_with_auth(self, create_authenticated_user, create_category, client, delete_if_created, role):
        data = {'name': 'name {}'.format(randint(1, 10000)),
                'description': 'description'}
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
                               'count by id': [Category.objects.filter(**data).count(), exp_count]})

    @pytest.mark.skip("потом доделаю")  # todo добавить параметры в строку запроса
    @pytest.mark.parametrize('is_authenticated, role',
                             [(False, None), (True, None), (True, UserData.USER_ROLE), (True, UserData.ADMIN_ROLE)])
    def test_get_all_categories(self, create_hashed_user, create_category, client, role, is_authenticated):
        if is_authenticated:
            user = create_hashed_user(role_names=[role])
            client.post(url_for(ResourceNames.LOGIN),
                        data=json.dumps({'email': user.email, 'password': UserData.DEFAULT_PASSWORD}),
                        content_type='application/json')

        category = create_category()
        response = client.get(url_for(self.resource_name))
