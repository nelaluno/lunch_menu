from backend_tests.framework.asserts import assert_data_are_equal
from database.models import Category, Type, Dish, User
from hamcrest import assert_that, calling, raises, is_
from random import randint, choice
from mongoengine.errors import ValidationError, NotUniqueError, DoesNotExist
from random import randint
import pytest
import datetime


def check_review_data(review_document, exp_data):
    owner_id = exp_data.get('added_by')
    assert_data_are_equal(
        {'mark': [review_document.mark, exp_data['mark']],
         'comment': [review_document.comment, exp_data.get('comment')],
         'created_at': [review_document.created_at, exp_data.get('created_at')],
         'added_by': [review_document.added_by, User.objects.get(id=owner_id) if owner_id else None]})


class TestReviewModel:
    @pytest.mark.parametrize('comment', ['some_comment_{}'.format(randint(1, 10000)), None])
    def test_create_review(self, create_user, create_dish, create_review, comment):
        review_data = dict(dish=create_dish(),
                           added_by=create_user().id,
                           mark=randint(1, 5),
                           comment=comment,
                           created_at=datetime.datetime.now())
        new_review = create_review(**review_data)
        check_review_data(new_review, review_data)

    @pytest.mark.skip(reason='Непонятное поле')
    def test_create_review_without_user(self, create_dish, create_user, create_review):
        assigned_dish = create_dish()
        assert_that(calling(create_review).with_args(dish=assigned_dish,
                                                     added_by=None), raises(ValidationError))

    @pytest.mark.parametrize('mark', [0, 6])
    def test_create_review_wrong_mark(self, create_dish, create_user, create_review, mark):
        assigned_dish = create_dish()
        owner_id = create_user().id
        assert_that(calling(create_review).with_args(dish=assigned_dish,
                                                     added_by=owner_id,
                                                     mark=mark), raises(ValidationError))

    def test_review_delete_user(self, create_dish, create_user, create_review):
        owner = create_user(with_deleting=False)
        dish = create_dish()
        new_review = create_review(dish=dish,
                                   added_by=owner.id)
        owner.delete()
        dish.reload()
