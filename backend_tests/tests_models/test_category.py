from backend_tests.framework.asserts import assert_data_are_equal
from hamcrest import assert_that, not_
from random import randint

import pytest


def check_category_data(category_document, exp_data):
    assert_data_are_equal(
        {'name': [category_document.name, exp_data['name']],
         'description': [category_document.description, exp_data['description']]})


class TestCategoryModel:
    @pytest.mark.parametrize('description', [None, '', 'description'])
    def test_create_category(self, create_category, description):
        category_data = dict(name='new_category_name_{}'.format(randint(1, 10000)),
                             description=description)
        new_category = create_category(**category_data)
        check_category_data(new_category, category_data)

    def test_category_delete_dish(self, create_dish, create_category):
        new_category = create_category()
        new_dish = create_dish(with_deleting=False, category=new_category.id)
        assert_that(new_dish.category, new_category)
        new_dish.delete()
        new_category.reload()

    # @pytest.mark.parametrize('name, description',
    #                          [('business lunch', 'business lunch'),
    #                           ('vitality', None),
    #                           ('soup bar', None),
    #                           ('le chief', None)])
    # def test_category(self, create_category, name, description):
    #     category_data = dict(name=name,
    #                          description=description)
    #     new_category = create_category(with_deleting=False, **category_data)
    #     check_category_data(new_category, category_data)
