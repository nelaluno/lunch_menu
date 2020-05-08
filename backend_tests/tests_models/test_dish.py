from random import randint, choice

import pytest
from hamcrest import assert_that, calling, raises, is_, equal_to, is_not, has_length
from mongoengine.errors import ValidationError, NotUniqueError

from backend_tests.framework.asserts import assert_data_are_equal
from database.models import Category, Type
from backend_tests.constans import UserData

def check_dish_data(dish_document, exp_data):
    category_id = exp_data.get('category')
    type_id = exp_data.get('type')
    assert_data_are_equal(
        {'name': [dish_document.name, exp_data['name']],
         'description': [dish_document.description, exp_data.get('description')],
         'price': [dish_document.price, exp_data.get('price')],
         'category': [dish_document.category, Category.objects.get(id=category_id) if category_id else None],
         'type': [dish_document.type, Type.objects.get(id=type_id) if type_id else None],
         'availability': [dish_document.availability, exp_data.get('availability') or False],
         'reviews': [dish_document.reviews, exp_data.get('reviews', [])]})


class TestDishModel:
    @pytest.mark.parametrize('category_name',
                             [None,
                              choice(['business lunch', 'vitality', 'soup bar', 'le chief'])])
    @pytest.mark.parametrize('type_name',
                             [None, choice(['soup', 'hot', 'salad', 'snack'])])
    def test_create_dish(self, create_dish, category_name, type_name):
        category = Category.objects.get(name=category_name).id if category_name else None
        type_ = Type.objects.get(name=type_name).id if type_name else None
        dish_data = dict(name='new_dish_name_{}'.format(randint(1, 10000)),
                         description='new_dish_desc',
                         price=randint(1, 10000),
                         category=category,
                         type=type_,
                         availability=choice([True, False, None]),
                         # picture = db.ImageField(required=False, unique=False)
                         reviews=[])
        new_dish = create_dish(**dish_data)
        check_dish_data(new_dish, dish_data)

    @pytest.mark.parametrize('price', [None, -randint(1, 10000)])
    def test_create_dish_with_wrong_price(self, create_dish, price):
        assert_that(calling(create_dish).with_args(price=price), raises(ValidationError))

    def test_create_dish_with_existing_name(self, create_dish):
        name = 'new_dish_name_{}'.format(randint(1, 10000))
        create_dish(name=name)
        assert_that(calling(create_dish).with_args(name=name), raises(NotUniqueError))

    def test_dish_delete_category(self, create_dish, create_category):
        new_category = create_category(with_deleting=False)
        new_dish = create_dish(category=new_category.id)
        assert_that(new_dish.category, new_category)
        new_category.delete()
        new_dish.reload()
        assert_that(new_dish.category, is_(None))

    @pytest.mark.skip(reason='Ошибка удаления типа IndexError')
    def test_dish_delete_type(self, create_dish, create_type):
        new_type = create_type(with_deleting=False)
        new_dish = create_dish(type=new_type.id)
        assert_that(new_dish.type, new_type)
        new_type.delete()
        new_dish.reload()
        assert_that(new_dish.type, is_(None))

    @pytest.mark.parametrize('has_review', [True, False])
    def test_has_review(self, create_dish, create_user, create_review, has_review):
        owner = create_user()
        dish = create_dish()
        if has_review:
            create_review(dish=dish, added_by=owner.id)
        assert_that(dish.has_review(owner.id), equal_to(has_review))

    def test_add_review(self, create_dish, create_user):
        dish = create_dish()
        dish.add_review(added_by=create_user().id, mark=randint(1, 5))
        assert_that(dish.reviews, is_not([]))

    def test_rating(self, create_dish, create_user):
        mark = randint(1, 5)
        dish = create_dish()
        dish.add_review(added_by=create_user().id, mark=mark)
        assert_that(dish.rating, equal_to(mark))

    def test_add_2_review_for_1_user(self, create_dish, create_user):
        dish = create_dish()
        user = create_user()
        review_num = 2
        for i in range(1, review_num + 1):
            dish.add_review(added_by=user.id, mark=randint(1, 5))
        assert_that(dish.reviews, has_length(1))

    # def test_update_review(self, create_dish, create_user):
    #     dish = create_dish()
    #     user = create_user()
    #     review = dish.add_review(added_by=user.id, mark=randint(1, 5))
    #     review_data = dict(added_by=user.id,
    #                        mark=randint(1, 5),
    #                        comment='comment_{}'.format(randint(1, 100000)),
    #                        created_at=review.created_at)
    #     dish.update_review(**review_data)
    #     check_review_data(review, review_data)

    def test_delete_review(self, create_dish, create_user):
        dish = create_dish()
        users = []
        review_num = 2
        for i in range(1, review_num + 1):
            role_names = [choice([UserData.USER_ROLE, UserData.ADMIN_ROLE])]
            user = create_user(role_names=role_names,
                               email='{}_user{}@gmail.com'.format(role_names[0] or 'simple', randint(1, 10000)))
            dish.add_review(added_by=user.id, mark=randint(1, 5), comment='some comment {}'.format(randint(1, 10000)))
            assert_that(dish.reviews, has_length(i))
            users.append(user)
        assert True
        # for i, user in enumerate(users, start=1):
        #     dish.delete_review(user=user)
        #     assert_that(dish.reviews, has_length(review_num - i))

    def test_complex_rating(self, create_dish, create_user):
        dish = create_dish()
        marks = []
        review_num = 3
        for i in range(1, review_num + 1):
            mark = randint(1, 5)
            dish.add_review(added_by=create_user().id, mark=mark)
            marks.append(mark)
            assert_that(dish.rating, equal_to(sum(marks) / len(marks)))

    # @pytest.mark.parametrize('dish_data',
    #                          [{"name": "veggi rice",
    #                            "description": "just rice and vegetables",
    #                            "price": 200,
    #                            "category": Category.objects.get(name='business lunch'),
    #                            "type": Type.objects.get(name='hot'),
    #                            "availability": True,
    #                            "reviews": []},
    #                           {"name": "pizza",
    #                            "description": "italian pizza",
    #                            "price": 500,
    #                            "category": Category.objects.get(name='le chief'),
    #                            "type": Type.objects.get(name='snack'),
    #                            "availability": False,
    #                            "reviews": []}], ids=["veggi rice", "pizza"])
    # def test_dish(self, create_dish, dish_data):
    #     new_dish = create_dish(with_deleting=False, **dish_data)
    #     check_dish_data(new_dish, dish_data)
