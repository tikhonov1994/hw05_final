import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        User = get_user_model()
        cls.user = User.objects.create(username='Test')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-group',
            description='тестовое описание',
        )
        cls.post = Post.objects.create(
            group=cls.group,
            text='Тестовый текст',
            author=cls.user,
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.form = PostForm()
        cls.small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                         b'\x01\x00\x80\x00\x00\x00\x00\x00'
                         b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                         b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                         b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                         b'\x0A\x00\x3B')
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif',
        )
        cls.post_new = Post.objects.create(
            text='Тестовая запись №2',
            group=cls.group,
            author=cls.user,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_new_post(self):
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Новый текст поста',
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('index'),
            msg_prefix='Ошибка переадресации при создании нового поста'
        )
        self.assertEqual(
            Post.objects.count(),
            post_count + 1,
            'Ошибка в количстве постов после создания нового поста'
        )
        self.assertTrue(
            Post.objects.filter(text='Новый текст поста').exists(),
            'Не найден пост с текстом новой записи'
        )

    def test_edit_post(self):
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Новый текст поста',
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={'username': 'Test',
                                         'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertRedirects(
            response,
            reverse('post',
                    kwargs={'username': 'Test', 'post_id': self.post.id}),
            msg_prefix='Редирект работает некорректно'
        )
        self.assertEqual(
            Post.objects.count(),
            post_count,
            'Изменилось количество постов при редактировании поста'
        )
        self.assertTrue(
            Post.objects.filter(text='Новый текст поста').exists(),
            'Текст редактируемого поста не изменился'
        )

    def test_context_pages_with_image(self):
        response_1 = self.authorized_client.get(
            reverse('post',
                    kwargs={'username': 'Test', 'post_id': self.post_new.id}),
            follow=True
        )
        post_image0 = response_1.context.get('post').image
        response_array = (
            self.authorized_client.get(
                reverse('group_posts', kwargs={'slug': self.group.slug}),
                follow=True
            ),
            self.authorized_client.get(
                reverse('profile', kwargs={'username': 'Test'})
            ),
        )
        for i in response_array:
            with self.subTest(i=i):
                self.assertEqual(
                    i.context.get('page')[0].image,
                    'posts/small.gif',
                    'Картинка не найдена на странице группы или профайла'
                )
        self.assertEqual(
            post_image0,
            'posts/small.gif',
            'Картинка не найдена на странице поста'
        )

    def test_create_post_with_image(self):
        post_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small2.gif',
            content=self.small_gif,
            content_type='image/gif',
        )
        form_data = {
            'group': self.group.id,
            'text': 'Новый текст поста',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('index'),
            msg_prefix='Ошибка редиректа при создании поста с картинкой'
        )
        self.assertEqual(
            response.context.get('page')[0].image,
            'posts/small2.gif',
            'Картинка не найдена на главной странице'
        )
        self.assertEqual(
            Post.objects.count(),
            post_count + 1,
            'Ошибка в количестве постов при добавлении поста с картинкой'
        )
