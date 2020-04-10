from .db import db
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_security import (MongoEngineUserDatastore, UserMixin, RoleMixin)


class Type(db.Document):
    name = db.StringField(required=True, unique=True)
    description = db.StringField(required=False, unique=False)


class Category(db.Document):
    name = db.StringField(required=True, unique=True)
    description = db.StringField(required=False, unique=False)


class Review(db.Document):
    dish = db.ReferenceField('Dish')
    added_by = db.ReferenceField('User', reverse_delete_rule=db.DO_NOTHING)
    mark = db.IntField(required=True, unique=False, min_value=1, max_value=5)  # неизменяемое
    comment = db.StringField(required=False, unique=False)  # неизменяемое


class Dish(db.Document):
    name = db.StringField(max_length=100, required=True, unique=True)
    description = db.StringField(required=True, unique=True)
    price = db.DecimalField(required=True, unique=False)
    category = db.ReferenceField(Category, reverse_delete_rule=db.NULLIFY)
    type = db.ReferenceField(Type, reverse_delete_rule=db.NULLIFY)
    availability = db.BooleanField()
    # picture = db.ImageField(required=False, unique=False)
    reviews = db.ListField(db.ReferenceField(Review, reverse_delete_rule=db.PULL))

    @property
    def rating(self):
        return self.reviews.average('mark')
        # sum([review.mark for review in self.reviews]) / len(self.reviews)


Review.register_delete_rule(Dish, 'reviews', db.CASCADE)


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class User(db.Document, UserMixin):
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True, min_length=7)
    active = db.BooleanField(default=True)
    roles = db.ListField(db.ReferenceField(Role), default=[])
    favorites = db.ListField(db.ReferenceField('Dish', reverse_delete_rule=db.PULL, default=[]))

    # reviews = db.ListField(db.ReferenceField('Review', reverse_delete_rule=db.PULL))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hash_password()

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)


User.register_delete_rule(Review, 'added_by', db.CASCADE)

user_datastore = MongoEngineUserDatastore(db, User, Role)
