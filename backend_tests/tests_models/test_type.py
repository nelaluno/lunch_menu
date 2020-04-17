from backend_tests.framework.asserts import assert_data_are_equal
from database.models import Role
from hamcrest import assert_that, not_
from random import randint
from database.models import Type

import pytest


def check_type_data(type_document, exp_data):
    assert_data_are_equal(
        {'name': [type_document.name, exp_data['name']],
         'description': [type_document.description, exp_data['description']]})


@pytest.mark.skip(reason='Ошибка удаления IndexError')
class TestTypeModel:
    @pytest.mark.parametrize('description', [None, '', 'description'],
                             ids=['without description', 'empty description', 'normal description'])
    def test_create_type(self, create_type, description):
        type_data = dict(name='new_type_name_{}'.format(randint(1, 10000)),
                         description=description)
        new_type = create_type(**type_data)
        check_type_data(new_type, type_data)
