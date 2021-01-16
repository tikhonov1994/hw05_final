from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        cls.user = User.objects.create(username='Test')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-group',
            description='тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user,
        )

    def test_verbose(self):
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name,
                    expected,
                    'verbose_name не соответствует шаблону'
                )

    def test_help(self):
        post = PostModelTest.post
        field_help = {
            'text': 'Давай, напиши что-нибудь интересное',
            'group': 'Поле не обязательно для заполнения',
        }
        for value, expected in field_help.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text,
                    expected,
                    'help_text не соответствует шаблону'
                )

    def test_str(self):
        group = PostModelTest.group
        post = PostModelTest.post
        test_str = {
            group: 'Тестовый заголовок',
            post: 'Тестовый текст',
        }
        for value, expected in test_str.items():
            with self.subTest(value=value):
                self.assertEqual(
                    str(value),
                    expected,
                    'Функция __str__ некорректно работает'
                )
