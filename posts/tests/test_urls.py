from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        cls.writer = User.objects.create(username='Test')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-group',
            description='тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.writer,
        )
        cls.writer_client = Client()
        cls.writer_client.force_login(cls.writer)
        cls.guest_client = Client()
        cls.user = User.objects.create(username='AndreyG')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_guest(self):
        status_code = {
            reverse('index'): 200,
            reverse('group_posts', kwargs={'slug': 'test-group'}): 200,
            reverse('new_post'): 302,
            reverse('profile', kwargs={'username': 'Test'}): 200,
            reverse('post', kwargs={'username': 'Test',
                                    'post_id': self.post.id}): 200,
            reverse('post_edit', kwargs={'username': 'Test',
                                         'post_id': self.post.id}): 302,
        }
        for url, code in status_code.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url).status_code
                self.assertEqual(
                    response,
                    code,
                    ('Ошибка доступа к странице для '
                     'неавторизованного пользователя')
                )

    def test_authorized(self):
        status_code = {
            reverse('index'): 200,
            reverse('group_posts', kwargs={'slug': 'test-group'}): 200,
            reverse('new_post'): 200,
            reverse('profile', kwargs={'username': 'Test'}): 200,
            reverse('post', kwargs={'username': 'Test',
                                    'post_id': self.post.id}): 200,
            reverse('post_edit', kwargs={'username': 'Test',
                                         'post_id': self.post.id}): 302,
        }
        for url, code in status_code.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url).status_code
                self.assertEqual(
                    response,
                    code,
                    ('Ошибка доступа к странице для '
                     'авторизованного пользователя')
                )

    def test_author(self):
        self.assertEqual(self.writer_client.get(
            reverse(
                'post_edit',
                kwargs={'username': 'Test',
                        'post_id': self.post.id})
            ).status_code, 200)

    def test_correct_template(self):
        pages = {
            reverse('index'): 'index.html',
            reverse(
                'group_posts', kwargs={'slug': 'test-group'}): 'group.html',
            reverse('new_post'): 'new_post.html',
            reverse('post_edit',
                    kwargs={'username': 'Test',
                            'post_id': self.post.id}): 'new_post.html',
        }
        for urls, templates in pages.items():
            with self.subTest(urls=urls):
                response = self.writer_client.get(urls)
                self.assertTemplateUsed(
                    response,
                    templates,
                    'Ошибка вызова шаблона страницы'
                )

    def test_redirect_anonymous(self):
        response = self.guest_client.get(
            reverse('post_edit',
                    kwargs={'username': 'Test', 'post_id': self.post.id}),
            follow=True
        )
        redirect_page = reverse('login')+'?next=%2FTest%2F1%2Fedit%2F'
        self.assertRedirects(
            response,
            redirect_page,
            msg_prefix=('Ошибка переадресации неавторизованного '
                        'пользователя при попытке редактирования поста')
            )

    def test_redirect_not_author(self):
        response = self.authorized_client.get(
            reverse('post_edit', kwargs={'username': 'Test',
                    'post_id': self.post.id}), follow=True)
        redirect_page = reverse('post', kwargs={'username': 'Test',
                                                'post_id': self.post.id})
        self.assertRedirects(
            response,
            redirect_page,
            msg_prefix=('Ошибка переадресации не автора '
                        'поста при попытке редактирования поста')
            )

    def test_404(self):
        response = self.guest_client.get('not_found').status_code
        self.assertEqual(response, 404, 'Ошибка 404 страницы')
