import datetime
from random import randint, choice

import pytest
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from backend_tests.constans import UserData
from database.models import LunchTypeSet, Type, Category, User, DayLunch, LunchSet


def create_image(text):
    image = Image.new('RGBA', (512, 512))

    mark = Image.open('cap.jpg').convert("RGBA")
    mark = mark.resize(image.size)
    image.paste(mark, (0, 0), mark)

    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 32)
    draw.text((150, 250), text, (0, 0, 225), font=font)

    image_name = 'images/{}.png'.format(text)
    image.save(image_name)
    return image_name


class TestFullDatabase:
    @pytest.mark.parametrize('name, description',
                             [('business lunch', None),
                              ('hot', 'spicy dishes'),
                              ('vegan', 'without animal products'),
                              ('new', None),
                              ('children', "for children")])
    def test_category(self, create_category, name, description):
        create_category(with_deleting=False, name=name, description=description)

    @pytest.mark.parametrize('name, description',
                             [('soup', None),
                              ('hot', 'Hot dish'),
                              ('salad', None),
                              ('snack', None),
                              ('drink', None)])
    def test_type(self, create_type, name, description):
        create_type(name=name, description=description, with_deleting=False)

    def test_lunch_type_set(self, create_type):
        position_types = [[Type.objects.get(name=pos_name) for pos_name in pos_names] for pos_names in
                          (['soup', 'hot'], ['salad', 'snack'], ['drink'])]
        lunch_type_set = LunchTypeSet(sale=20, position_1=position_types[0], position_2=position_types[1],
                                      position_3=position_types[2])
        lunch_type_set.save()

    @pytest.mark.parametrize('name, description',
                             [('admin', 'Administrator can manage dishes, types, categories and delete reviews.'),
                              ('user', 'User can manage his own reviews.')])
    def test_role(self, create_role, name, description):
        create_role(name=name, description=description, with_deleting=False)

    @pytest.mark.parametrize('role', [None, UserData.USER_ROLE, UserData.USER_ROLE, UserData.ADMIN_ROLE])
    def test_create_user_with_role(self, create_user, role):
        create_user(email='{}_user{}@gmail.com'.format(role or 'simple', randint(1, 10000)),
                    password=UserData.DEFAULT_PASSWORD,
                    role_names=[role], with_deleting=False)

    # def test_create_image(self):
    #     create_image('test')

    def test_dish_with_reviews(self, create_dish, create_review):
        types = Type.objects().all()
        categories = Category.objects().all()
        lunch_type_set = LunchTypeSet.objects().first()
        for weekday in range(7):
            weekday_dishes = {}
            for dish_type in types:
                weekday_dish = create_dish(with_deleting=False,
                                           name='name of {} {}'.format(dish_type.name, weekday),
                                           description='description of {} {}'.format(dish_type.name, weekday),
                                           price=randint(100, 500),
                                           category=choice(categories),
                                           type=dish_type,
                                           availability=True)
                weekday_dish.image.put(create_image(weekday_dish.name))
                weekday_dish.save()
                for user in User.objects.filter(email__startswith=UserData.USER_ROLE):
                    create_review(with_deleting=False, dish=weekday_dish,
                                  added_by=user.id,
                                  mark=randint(1, 5),
                                  comment='comment from user {}'.format(user.email),
                                  created_at=datetime.datetime.now())
                    weekday_dishes[dish_type.name] = weekday_dish
            # day_lunch_set = LunchSet(
            #     **{field_name: weekday_dishes.get(choice(getattr(lunch_type_set, field_name)).name) for field_name
            #        in ['position_1', 'position_2', 'position_3']})
            day_lunch = DayLunch(
                weekday=weekday,
                # lunch_set={field_name: weekday_dishes.get(choice(getattr(lunch_type_set, field_name)).name) for
                #            field_name in ['position_1', 'position_2', 'position_3']},
                price=randint(700, 1000)
            )
            day_lunch.lunch_set = LunchSet(
                **{field_name: weekday_dishes.get(choice(getattr(lunch_type_set, field_name)).name) for field_name
                   in ['position_1', 'position_2', 'position_3']})
            day_lunch.save()
