import json
from random import randint

from calendar import timegm
from email.utils import formatdate

import pytest
from flask import url_for

from backend_tests.constans import ResourceNames, UserData
from backend_tests.framework.asserts import assert_data_are_equal
from database.models import Review
from resources.review import ReviewApi, ReviewsApi


@pytest.fixture(scope='function')
def delete_if_created():
    dish_and_name = []

    def store(dish, name):
        dish_and_name.append((dish, name))

    yield store

    for dish, name in dish_and_name:
        if dish.reviews.filter(name=name).count() > 0:
            dish.reviews.filter(name=name).delete()


# @pytest.mark.skip('проблема с адресацией - нет id')
class TestReviewApi():
    resource_name = ReviewApi.__name__.lower()

    def test_get_review_without_auth(self, create_dish, create_authenticated_user, create_review, client):
        dish = create_dish(comment='some comment')
        user, token = create_authenticated_user(role_names=['user'])
        review = create_review(added_by=user.id, dish=dish)

        response = client.get(url_for(self.resource_name, dish_id=dish.id, review_id=review.id),
                              content_type='application/json',
                              headers={'Authentication-Token': token})

        assert_data_are_equal({'status_code': [response.status_code, 200],
                               'mark': [response.json.get('mark'), review.mark],
                               'comment': [response.json.get('comment'), review.comment],
                               'created_at': [response.json.get('created_at'),
                                              formatdate(timegm(review.created_at.utctimetuple()))],
                               'added_by': [response.json.get('added_by'), review.added_by.get_id()],
                               '_id': [response.json.get('_id'), None]})
