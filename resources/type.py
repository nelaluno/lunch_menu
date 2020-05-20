from database.models import Type

from resources.errors import (TypeAlreadyExistsError, UpdatingTypeError,
                              DeletingTypeError, TypeNotExistsError)

from resources.mixins import MultipleObjectApiMixin, SingleObjectApiMixin


class TypesApi(MultipleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=Type, not_unique_error=TypeAlreadyExistsError, *args, **kwargs)


class TypeApi(SingleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=Type, updating_error=UpdatingTypeError, deleting_error=DeletingTypeError,
                         does_not_exist_error=TypeNotExistsError, *args, **kwargs)
