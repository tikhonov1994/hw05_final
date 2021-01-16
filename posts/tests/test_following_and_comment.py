from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls.base import reverse

from ..models import Comment, Follow, Post


class FollowingAndCommentTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        cls.user1 = User.objects.create(username='Test_user1')
        cls.user2 = User.objects.create(username='Test_user2')
        cls.author = User.objects.create(username='Test_author')
        cls.authorized_client1 = Client()
        cls.authorized_client1.force_login(cls.user1)
        cls.authorized_client2 = Client()
        cls.authorized_client2.force_login(cls.user2)
        cls.guest_client = Client()
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.author
        )
        Follow.objects.create(
            user=cls.user2,
            author=cls.author
        )

    def test_following(self):
        response = self.authorized_client1.get( # noqa
            reverse('profile_follow',
                    kwargs={'username': 'Test_author'})
        )
        self.assertTrue(
            Follow.objects.filter(author=self.author,
                                  user=self.user1).exists(),
            'Не удалось подписаться'
        )

    def test_unfollow(self):
        response = self.authorized_client2.get( # noqa
            reverse('profile_unfollow',
                    kwargs={'username': 'Test_author'})
        )
        self.assertFalse(
            Follow.objects.filter(author=self.author,
                                  user=self.user2).exists(),
            'Не удалось отписаться'
        )

    def test_following_index(self):
        response_follower = self.authorized_client2.get(
            reverse('follow_index')
        )
        post_follow = response_follower.context.get('page')[0]
        response_unfollower = self.authorized_client1.get(
            reverse('follow_index')
        )
        post_unfollow = response_unfollower.context.get('page')
        self.assertEqual(post_follow, self.post,
                         'Не найден новый пост в ленте подписчика')
        self.assertEqual(post_unfollow.object_list.count(), 0,
                         'Пост найден в ленте не подписчика')

    def test_comment_authorized_user(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Новый комментарий',
        }
        response_authorized = self.authorized_client1.post(
            reverse(
                'add_comment',
                kwargs={'username': 'Test_author',
                        'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response_authorized,
            reverse(
                'post',
                kwargs={'username': 'Test_author', 'post_id': self.post.id}
            ),
            msg_prefix='Ошибка редиректа'
        )
        self.assertEqual(
            response_authorized.context.get('comments')[0].text,
            'Новый комментарий',
            'Комментарий не найден на странице поста'
        )
        self.assertEqual(
            Comment.objects.count(),
            comment_count + 1,
            'Количество комментариев не изменилось'
        )
        self.assertTrue(
            Comment.objects.filter(text='Новый комментарий').exists(),
            'Добавленный комментарий не найден'
        )

    def test_comment_guest_user(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Новый комментарий',
        }
        response_guest = self.guest_client.post(
            reverse(
                'add_comment',
                kwargs={'username': 'Test_author',
                        'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        redirect_page = reverse(
            'login')+'?next=%2FTest_author%2F1%2Fcomment%2F'
        self.assertRedirects(
            response_guest,
            redirect_page,
            msg_prefix='Ошибка редиректа неавторизованного пользователя'
        )
        self.assertEqual(
            Comment.objects.count(),
            comment_count,
            'Количество комментариев изменилось'
        )
