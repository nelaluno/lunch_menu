from datetime import datetime
from statistics import mean

from bson.objectid import ObjectId
from flask import url_for
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_restful.utils import OrderedDict
from flask_security import (MongoEngineUserDatastore, UserMixin, RoleMixin)

from .db import db


# class SearchableMixin(object):
#     @classmethod
#     def search(cls, expression, page, per_page):
#         ids, total = query_index(cls.__tablename__, expression, page, per_page)
#         if total == 0:
#             return cls.query.filter_by(id=0), 0
#         when = []
#         for i in range(len(ids)):
#             when.append((ids[i], i))
#         return cls.query.filter(cls.id.in_(ids)).order_by(
#             db.case(when, value=cls.id)), total
#
#     @classmethod
#     def before_commit(cls, session):
#         session._changes = {
#             'add': list(session.new),
#             'update': list(session.dirty),
#             'delete': list(session.deleted)
#         }
#
#     @classmethod
#     def after_commit(cls, session):
#         for obj in session._changes['add']:
#             if isinstance(obj, SearchableMixin):
#                 add_to_index(obj.__tablename__, obj)
#         for obj in session._changes['update']:
#             if isinstance(obj, SearchableMixin):
#                 add_to_index(obj.__tablename__, obj)
#         for obj in session._changes['delete']:
#             if isinstance(obj, SearchableMixin):
#                 remove_from_index(obj.__tablename__, obj)
#         session._changes = None
#
#     @classmethod
#     def reindex(cls):
#         for obj in cls.query:
#             add_to_index(cls.__tablename__, obj)
#
#
# db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
# db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


class Type(db.Document):
    name = db.StringField(required=True, unique=True)
    description = db.StringField(required=False, unique=False)


class Category(db.Document):
    name = db.StringField(required=True, unique=True)
    description = db.StringField(required=False, unique=False)


class Review(db.EmbeddedDocument):
    _id = db.ObjectIdField(required=True, default=lambda: ObjectId())
    added_by = db.ReferenceField('User', null=True, required=False)
    mark = db.IntField(required=True, min_value=1, max_value=5)
    comment = db.StringField(required=False)
    created_at = db.DateTimeField(default=datetime.utcnow, required=True)

    meta = {
        'indexes': ['-created_at', 'added_by'],
        'ordering': ['-created_at'],
    }

    @property
    def id(self):
        return self._id


class CommonReview(db.Document):
    added_by = db.ReferenceField('User', null=True, required=False)
    mark = db.IntField(required=True, min_value=1, max_value=5)
    comment = db.StringField(required=False)
    created_at = db.DateTimeField(default=datetime.utcnow, required=True)

    meta = {
        'indexes': ['-created_at', 'added_by'],
        'ordering': ['-created_at'],
    }


class Dish(db.Document):
    name = db.StringField(max_length=100, required=True, unique=True)
    description = db.StringField(required=True)
    price = db.DecimalField(required=True, unique=False, min_value=0)
    category = db.ReferenceField(Category, reverse_delete_rule=db.NULLIFY)
    type = db.ReferenceField(Type, reverse_delete_rule=db.NULLIFY)
    availability = db.BooleanField(required=True, default=False)
    image = db.ImageField(required=False, unique=False)
    reviews = db.EmbeddedDocumentListField(Review)

    def to_dict(self):
        return OrderedDict({
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'type': self.type,
            'image': self.image,
            'availability': self.availability,
            # 'reviews': self.reviews,
            'rating': self.rating
        })

    @property
    def rating(self):
        return mean([review.mark for review in self.reviews]) if self.reviews else None

    def has_review(self, user_id):
        return Dish.objects.filter(id=self.id, reviews__added_by=user_id).count() > 0

    def add_review(self, **body):
        user = User.objects.get(id=body.get('added_by'))
        if not self.has_review(user):
            review = Review(**body)
            self.update(push__reviews=review)
            self.reload()
            return review
        else:
            return self.update_review(**body)

    def update_review(self, **body):
        user = User.objects.get(id=body.get('added_by'))
        if self.has_review(user):
            review = self.reviews.get(added_by=user)
            review.mark = body.get('mark', review.mark)
            review.comment = body.get('comment', review.comment)
            self.save()
            return review

    def delete_review(self, user):
        if self.has_review(user):
            self.update(pull__reviews__added_by=user)
            self.reload()

    meta = {
        'ordering': ['-availability', 'name']
    }


# User.register_delete_rule(Review, 'added_by', db.CASCADE)
# Review.register_delete_rule(Dish, 'reviews', db.CASCADE)


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class User(db.Document, UserMixin):  # PaginatedAPIMixin
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True, min_length=7)
    active = db.BooleanField(default=True)
    roles = db.ListField(db.ReferenceField(Role), default=[], reverse_delete_rule=db.PULL)
    favorites = db.ListField(db.ReferenceField('Dish', reverse_delete_rule=db.PULL, default=[]))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_favorite(self, dish):
        return dish in self.favorites  # todo

    def like_dish(self, dish):
        if not self.is_favorite(dish):
            self.update(push__favorites=dish)

    def unlike_dish(self, dish):
        if self.is_favorite(dish):
            self.update(pull__favorites=dish)


User.register_delete_rule(Review, 'added_by', db.DO_NOTHING)

user_datastore = MongoEngineUserDatastore(db, User, Role)


class DayLunch(db.Document):
    day = db.StringField(
        required=True, min_length=7, unique=True,
        choices=["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"])
    # set = db
