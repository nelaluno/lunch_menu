import json
import os
import tempfile
from random import randint

import pytest
from flask import url_for

from app import app as app_obj
from backend_tests.constans import UserData
# import pytest_flask.fixtures
from database.models import User, Role, Dish, Category, Type, Review
from resources.auth import LoginApi


@pytest.fixture
def app():
    # mocker.patch("funkyflask.do_something.get_something", return_value='bar')
    db_fd, app_obj.config['MONGODB_SETTINGS'] = tempfile.mkstemp()
    app_obj.config['TESTING'] = True

    yield app_obj

    os.close(db_fd)
    os.unlink(app_obj.config['MONGODB_SETTINGS'])


# @pytest.fixture
# def client_request_context():
#     db_fd, app.config['MONGODB_SETTINGS'] = tempfile.mkstemp()
#     app.config['TESTING'] = True
#
#     with app.test_client() as client:
#         with app.app_context():
#             yield app, client
#
#     os.close(db_fd)
#     os.unlink(app.config['MONGODB_SETTINGS'])
#
#
# @pytest.fixture
# def client_request_context(request):
#     db_fd, app.config['MONGODB_SETTINGS'] = tempfile.mkstemp()
#     app.config['TESTING'] = True
#
#     with app.test_request_context(request) as client:
#         with app.app_context():
#             yield client
#
#     os.close(db_fd)
#     os.unlink(app.config['MONGODB_SETTINGS'])


@pytest.fixture(scope='function')
def create_user():
    emails = []

    def create(with_deleting=True, **kwargs):
        roles = [Role.objects.get(name=role_name).id for role_name in kwargs.get('role_names', []) if role_name]
        user = User(email=kwargs.get('email', 'default_user{}@gmail.com'.format(randint(1, 10000))),
                    password=kwargs.get('password', UserData.DEFAULT_PASSWORD),
                    roles=roles,
                    favorites=kwargs.get('favorites', []))
        user.save()
        if with_deleting:
            emails.append(user.email)
        return user

    yield create

    for email in emails:
        # User.objects.get(email=email).reviews.delete()  # todo
        User.objects.get(email=email).delete()


@pytest.fixture(scope='function')
def create_hashed_user(create_user):
    def create(**kwargs):
        user = create_user(**kwargs)
        user.hash_password()
        user.save()
        return user

    yield create


@pytest.fixture(scope='function')
def create_dish():
    ids = []

    def create(with_deleting=True, **kwargs):
        dish = Dish(name=kwargs.get('name', 'new_dish_name_{}'.format(randint(1, 10000))),
                    description=kwargs.get('description', 'new_dish_desc'),
                    price=kwargs.get('price', 0),
                    category=kwargs.get('category'),
                    type=kwargs.get('type'),
                    availability=kwargs.get('availability'),
                    # picture = db.ImageField(required=False, unique=False)
                    reviews=kwargs.get('reviews', None))
        # dish.category = kwargs.get('category')
        # dish.type = kwargs.get('type')
        dish.save()
        if with_deleting:
            ids.append(dish.id)
        return dish

    yield create

    for dish_id in ids:
        dish = Dish.objects.get(id=dish_id)
        if dish:
            dish.delete()


@pytest.fixture(scope='function')
def create_category():
    ids = []

    def create(with_deleting=True, **kwargs):
        category = Category(name=kwargs.get('name', 'new_category_name_{}'.format(randint(1, 10000))),
                            description=kwargs.get('description', 'some category'))
        category.save()
        if with_deleting:
            ids.append(str(category.id))
        return category

    yield create

    for category_id in ids:
        Category.objects.get(id=category_id).delete()


@pytest.fixture(scope='module')
def create_type():
    ids = []

    def create(with_deleting=True, **kwargs):
        type_ = Type(name=kwargs.get('name', 'new_type_name_{}'.format(randint(1, 10000))),
                     description=kwargs.get('description'))
        type_.save()
        if with_deleting:
            ids.append(str(type_.id))
        return type_

    yield create

    for type_id in ids:
        type_ = Type.objects.get(id=type_id)
        type_.delete()


@pytest.fixture(scope='function')
def create_review():
    data = []

    def create(with_deleting=True, **kwargs):
        dish = kwargs.get('dish')
        review = Review(added_by=kwargs.get('added_by'),
                        mark=kwargs.get('mark', randint(1, 5)),
                        comment=kwargs.get('comment'),
                        created_at=kwargs.get('created_at'))
        dish.update(push__reviews=review)
        dish.reload()
        if with_deleting:
            data.append((dish.id, review.added_by))
        return review

    yield create

    for dish_id, added_by in data:
        Dish.objects.get(id=dish_id).update(pull__reviews__added_by=added_by)


@pytest.fixture(scope='module')
def create_role():
    ids = []

    def create(with_deleting=True, **kwargs):
        role = Role.objects.create(name=kwargs.get('name', 'new_role_name_{}'.format(randint(1, 10000))),
                                   description=kwargs.get('description'))
        role.save()
        if with_deleting:
            ids.append(str(role.id))
        return role

    yield create

    for role_id in ids:
        Role.objects.get(id=role_id).delete()


@pytest.fixture(scope='function')
def create_authenticated_user(create_hashed_user, client):
    def create(**kwargs):
        user = create_hashed_user(**kwargs)
        token = json.loads(client.post(url_for(LoginApi.__name__.lower()),
                                       data=json.dumps({'email': user.email,
                                                        'password': kwargs.get('password', UserData.DEFAULT_PASSWORD)}),
                                       content_type='application/json').data.decode())
        return user, token

    yield create
