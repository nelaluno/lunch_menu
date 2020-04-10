from backend_tests.framework.asserts import assert_data_are_equal
from database.models import Role


class TestRoleModel:
    def test_create_delete_role(self, create_user):
        role_data = dict(name='some_role')
        new_role = Role(**role_data)
        new_role.save()
        assert_data_are_equal(
            {'name': [new_role.name, role_data['name']],
             'description': [new_role.description, role_data.get('description')]})
        new_role.delete()
