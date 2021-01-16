from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField('Название группы', max_length=200)
    slug = models.SlugField(unique=True, blank=False)
    description = models.TextField('Описание группы')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Давай, напиши что-нибудь интересное'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts'
    )
    group = models.ForeignKey(
        Group, blank=True, null=True, on_delete=models.SET_NULL,
        verbose_name='Группа',
        related_name='post_group',
        help_text='Поле не обязательно для заполнения'
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True, null=True,
        verbose_name='Картинка',
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        related_name='comment',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments'
    )
    text = models.TextField('Текст комментария', max_length=80)
    created = models.DateTimeField(auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following'
    )
