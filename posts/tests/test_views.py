from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class ViewsTests(TestCase):
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
        posts = []
        for i in range(1, 12):
            posts.append(Post(
                text='text' + str(i),
                author=cls.user,
                group=cls.group,
            ))
        cls.post = Post.objects.bulk_create(posts)
        cls.second_group = Group.objects.create(
            title='Тестовый заголовок №2',
            slug='test-group2',
            description='тестовое описание №2',
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post_last = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user,
        )

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': reverse(
                'group_posts',
                kwargs={'slug': 'test-group'}
            ),
            'new_post.html': reverse('new_post'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    'Ошибка вызова шаблона страницы'
                )

    def test_context_index(self):
        response = self.authorized_client.get(reverse('index'))
        post_0 = response.context.get('page')[0]
        quantity_posts = response.context.get(
            'paginator').get_page(1).object_list.count()
        self.assertEqual(
            quantity_posts,
            10,
            'Ошибка пагинатора'
        )
        self.assertEqual(
            post_0,
            self.post_last,
            ('Первый пост на главной странице не соответствует '
             'последнему добавленному')
        )

    def test_context_group(self):
        response = self.authorized_client.get(reverse(
            'group_posts', kwargs={'slug': 'test-group'}))
        group_post_0 = response.context.get('page')[0]
        group = response.context.get('group')
        self.assertEqual(
            group_post_0,
            self.post_last,
            ('Первый пост на странице группы не соответствует '
             'последнему добавленному')
        )
        self.assertEqual(
            group,
            self.group,
            'Группа поста не соответствует указанной'
        )

    def test_context_group2(self):
        response = self.authorized_client.get(reverse(
            'group_posts', kwargs={'slug': 'test-group2'}))
        group_posts = response.context.get('page')
        self.assertEqual(
            group_posts.object_list.count(),
            0,
            'Пост найден в чужой группе'
        )

    def test_context_new_and_edit_post(self):
        response = self.authorized_client.get(
            reverse(
                'post_edit',
                kwargs={'username': 'Test',
                        'post_id': self.post_last.id}
            ), follow=True
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(
                    form_field,
                    expected,
                    'Тип полей шаблона отличается от заданного'
                )
        post_text = response.context.get('post')
        post_group = response.context.get('post').group
        self.assertEqual(
            post_text,
            self.post_last,
            'Данные последнего поста не загружены в шаблон при редактировании'
        )
        self.assertEqual(
            post_group,
            self.group,
            'Группа последнего поста не загружена в шаблон при редактировании'
        )

    def test_context_username(self):
        response = self.authorized_client.get(reverse(
            'profile', kwargs={'username': 'Test'}))
        post = response.context.get('page')[0]
        quantity_posts = response.context.get(
            'paginator').get_page(1).object_list.count()
        self.assertEqual(
            post,
            self.post_last,
            ('Первый пост на странице профайла не соответствует '
             'последнему добавленному')
        )
        self.assertEqual(
            quantity_posts,
            5,
            ('Количество постов на странице профайла '
             'не соответствует ожидаемому')
        )

    def test_context_post(self):
        response = self.authorized_client.get(
            reverse(
                'post',
                kwargs={'username': 'Test', 'post_id': self.post_last.id}
            )
        )
        post = response.context.get('post')
        post_author = response.context.get('author')
        post_count = response.context.get('count')
        self.assertEqual(
            post,
            self.post_last,
            'Пост на странице просмотра поста не соответствует ожидаемому'
        )
        self.assertEqual(
            post_author,
            self.user,
            'Автор на странице просмотра поста не соответствует ожидаемому'
        )
        self.assertEqual(
            post_count,
            12,
            'Общее количество постов автора не соответствует ожидаемому'
        )
