from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Post


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        User = get_user_model()
        cls.user = User.objects.create(username='Test')

    def test_cashe(self):
        request_1 = self.guest_client.get('/')
        post_new = Post.objects.create( # noqa
            text='Тестовая запись №2',
            author=self.user,
        )
        request_2 = self.guest_client.get('/')
        self.assertHTMLEqual(
            str(request_1.content),
            str(request_2.content),
            'Ошибка кэширования'
        )
