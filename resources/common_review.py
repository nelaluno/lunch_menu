from flask_security import current_user
from flask_security.decorators import roles_accepted, login_required

from database.models import CommonReview
from resources.errors import (CommonReviewAlreadyExistsError, UpdatingCommonReviewError, DeletingCommonReviewError,
                              CommonReviewNotExistsError)
from resources.mixins import MultipleObjectApiMixin, SingleObjectApiMixin, ProtectAuthorMixin


class CommonReviewsApi(ProtectAuthorMixin, MultipleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=CommonReview, not_unique_error=CommonReviewAlreadyExistsError, *args, **kwargs)

    @roles_accepted('user')
    def post(self):
        return self._try_post()


class CommonReviewApi(ProtectAuthorMixin, SingleObjectApiMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(collection=CommonReview, updating_error=UpdatingCommonReviewError,
                         deleting_error=DeletingCommonReviewError, does_not_exist_error=CommonReviewNotExistsError,
                         *args, **kwargs)

    def _put_document(self, document_id, *args, **kwargs):
        document = self.get_document(document_id)
        if document.added_by == current_user.id:
            document.update(**self.get_body())
            return '', 200
        else:
            return '', 302

    @roles_accepted('user')
    def put(self, document_id):
        return self._try_put(document_id)

    def _delete_document(self, document_id, *args, **kwargs):
        document = self.get_document(document_id)
        if document.added_by == current_user.id or current_user.has_role('admin'):
            document.delete()
            return '', 200
        else:
            return '', 302

    @login_required
    def delete(self, document_id):
        return self._try_delete(document_id)
