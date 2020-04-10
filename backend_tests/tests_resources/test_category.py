from database.models import Category
from flask import request
from flask import url_for

# from pytest_flask.fixtures import client

MULTIPLE_RESOURCE_NAME = 'categoriesapi'



class TestCategory:
    def test_create_category_without_auth(self):
        pass

    def test_create_category_user(self):
        pass

    def test_create_category_admin(self):
        pass

    def test_get_category_without_auth(self, client):
        categories = client
        categories.get(url_for(MULTIPLE_RESOURCE_NAME))

    def test_get_category_user(self):
        pass

    def test_get_category_admin(self):
        pass
