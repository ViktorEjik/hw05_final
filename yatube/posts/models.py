from core.models import CreatedModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200
    )
    slug = models.SlugField(
        unique=True
    )
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField(
        verbose_name='Текст поста.',
        help_text='Здесь необходимо указать текст вашего поста.'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа к которой принадлежит пост.',
        help_text='Выберете группу из выпадающего списка'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Ссылка на пост'
    )

    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Ссылка на автора поста'
    )
    text = models.TextField(
        verbose_name='Текст комментария.',
        help_text='Здесь необходимо указать текст вашего комментария.'
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique relation'
            )
        ]
