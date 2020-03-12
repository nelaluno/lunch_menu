from .db import db
# from flask_mongoengine import F
from flask_bcrypt import generate_password_hash, check_password_hash


class Rating(db.Document):
    dish = db.ReferenceField('Dish')
    added_by = db.ReferenceField('User')
    mark = db.IntField(required=True, unique=False, min_value=1, max_value=5)  # неизменяемое
    comment = db.StringField(required=False, unique=False)  # неизменяемое


class Dish(db.Document):
    name = db.StringField(max_length=100, required=True, unique=True)
    description = db.StringField(required=True, unique=True)
    price = db.DecimalField(required=True, unique=False)
    category = db.ListField(db.StringField(max_length=30), required=False)
    type = db.ListField(db.StringField(max_length=30), required=False)
    availability = db.BooleanField()
    # picture = db.ImageField(required=False, unique=False)
    rating = db.ListField(db.ReferenceField('Rating', reverse_delete_rule=db.PULL))


Rating.register_delete_rule(Dish, 'dish', db.CASCADE)


class User(db.Document):
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True, min_length=7)
    favorites = db.ListField(db.ReferenceField('Dish', reverse_delete_rule=db.PULL))

    # marks = db.ListField(db.ReferenceField('Rating', reverse_delete_rule=db.PULL))

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)


User.register_delete_rule(Rating, 'added_by', db.CASCADE)
