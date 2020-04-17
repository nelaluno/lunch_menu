import datetime
from .db import db
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_security import (MongoEngineUserDatastore, UserMixin, RoleMixin)
from statistics import mean


class Type(db.Document):
    name = db.StringField(required=True, unique=True)
    description = db.StringField(required=False, unique=False)

    meta = {
        # 'allow_inheritance': True,
        # 'indexes': ['-created_at', 'slug'],
        'ordering': ['-created_at']
    }


class Category(db.Document):
    name = db.StringField(required=True, unique=True)
    description = db.StringField(required=False, unique=False)


class Review(db.EmbeddedDocument):
    # id = db.ObjectIdField(unique=False, required=True, primary_key=True)
    added_by = db.ReferenceField('User', null=True, required=False)  # unique=True
    mark = db.IntField(required=True, unique=False, min_value=1, max_value=5)  # неизменяемое
    comment = db.StringField(required=False, unique=False)  # неизменяемое
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)

    meta = {
        # 'allow_inheritance': True,
        # 'indexes': ['-created_at', 'slug'],
        'ordering': ['-created_at']
    }


class Dish(db.Document):
    name = db.StringField(max_length=100, required=True, unique=True)
    description = db.StringField(required=True, unique=True)
    price = db.DecimalField(required=True, unique=False, min_value=0)
    category = db.ReferenceField(Category, reverse_delete_rule=db.NULLIFY)
    type = db.ReferenceField(Type, reverse_delete_rule=db.NULLIFY)
    availability = db.BooleanField(required=True, default=False)
    # picture = db.ImageField(required=False, unique=False)
    reviews = db.EmbeddedDocumentListField(Review)  # ReferenceField,

    @property
    def rating(self):
        return mean([review.mark for review in self.reviews])

    def has_review(self, user_id):
        #  self.reviews.filter(added_by=user.id).count() > 0
        return Dish.objects.filter(id=self.id, reviews__added_by=user_id).count() > 0

    def add_review(self, **body):
        user = User.objects.get(id=body.get('added_by'))
        if not self.has_review(user):
            review = Review(**body)
            self.update(push__reviews=review)
            self.reload()
            return review

    # def update_review(self, **body):
    #     user = User.objects.get(id=body.get('added_by'))
    #     if self.has_review(user):
    #         review = self.reviews.get(added_by=user)
    #         review.update(set__mark=body.get('mark', review.mark), set__comment=body.get('comment', review.comment))
    #         self.reload()
    #         return review


def delete_review(self, user):
    if self.has_review(user):
        self.update(pull__reviews__added_by=user)
        self.reload()


meta = {
    # 'allow_inheritance': True,
    # 'indexes': ['-created_at', 'slug'],
    'ordering': ['-availability', 'name']
}


# User.register_delete_rule(Review, 'added_by', db.CASCADE)
# Review.register_delete_rule(Dish, 'reviews', db.CASCADE)


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class User(db.Document, UserMixin):
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True, min_length=7)
    active = db.BooleanField(default=True)
    roles = db.ListField(db.ReferenceField(Role), default=[], reverse_delete_rule=db.PULL)
    favorites = db.ListField(db.ReferenceField('Dish', reverse_delete_rule=db.PULL, default=[]))

    # reviews = db.ListField(db.ReferenceField('Review', reverse_delete_rule=db.PULL))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hash_password()

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
