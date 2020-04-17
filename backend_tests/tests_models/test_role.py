from backend_tests.framework.asserts import assert_data_are_equal
from database.models import Role
from random import randint
from hamcrest import assert_that


class TestRoleModel:
    def test_create_delete_role(self, create_role):
        role_data = dict(name='some_role_{}'.format(randint(1, 100000)))
        new_role = create_role(**role_data)
        assert_data_are_equal(
            {'name': [new_role.name, role_data['name']],
             'description': [new_role.description, role_data.get('description')]})

    def test_role_delete_user(self, create_user, create_role):
        new_role = create_role()
        user = create_user(with_deleting=False, role_names=[new_role.name])
        assert_that(user.roles[0], new_role)
        user.delete()
        new_role.reload()
