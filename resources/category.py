from database.models import Category

from resources.errors import (CategoryAlreadyExistsError, UpdatingCategoryError, DeletingCategoryError,
                              CategoryNotExistsError)

from resources.mixins import MultipleObjectApiMixin, SingleObjectApiMixin


class CategoriesApi(MultipleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=Category, not_unique_error=CategoryAlreadyExistsError, *args, **kwargs)


class CategoryApi(SingleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=Category, updating_error=UpdatingCategoryError,
                         deleting_error=DeletingCategoryError, does_not_exist_error=CategoryNotExistsError,
                         *args, **kwargs)
