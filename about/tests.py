from django.test import Client, TestCase
from django.urls import reverse


class AboutTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authorized_client = Client()

    def test_about_pages(self):
        response_1 = self.authorized_client.get(reverse('about:author'))
        response_2 = self.authorized_client.get(reverse('about:tech'))
        self.assertEqual(
            response_1.status_code,
            200,
            'Страница "Об авторе" не доступна'
        )
        self.assertEqual(
            response_2.status_code,
            200,
            'Страница "Технологии" не доступна'
        )

    def test_template_about_pages(self):
        response_1 = self.authorized_client.get(reverse('about:author'))
        response_2 = self.authorized_client.get(reverse('about:tech'))
        self.assertTemplateUsed(
            response_1,
            'about/author.html',
            'Шаблон страницы "Об авторе" не соответствует ожидаемому'
        )
        self.assertTemplateUsed(
            response_2,
            'about/tech.html',
            'Шаблон страницы "Технологии" не соответствует ожидаемому'
        )
