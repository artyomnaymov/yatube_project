from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from core.models import CreateModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name='Название группы',
                             max_length=200,
                             help_text='Название группы')
    slug = models.SlugField(unique=True,
                            null=False,
                            blank=False)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(CreateModel):
    image = models.ImageField(verbose_name='Картинка', upload_to='posts/',
                              blank=True, help_text='Изображение поста')
    text = models.TextField(verbose_name='Текст поста',
                            help_text='Текст нового поста')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True,
                              null=True, verbose_name='Группа',
                              related_name='posts',
                              help_text='Группа, к которой будет относиться '
                                        'пост')

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.text[:15]


class Comment(CreateModel):
    post = models.ForeignKey(Post,
                             verbose_name='Пост',
                             on_delete=models.CASCADE, related_name='comments',
                             help_text='Пост')
    author = models.ForeignKey(User,
                               verbose_name='Пользователь',
                               on_delete=models.CASCADE,
                               related_name='comments',
                               help_text='Автор комментария')
    text = models.TextField(verbose_name='Текст комментария',
                            help_text='Текст нового комментария')

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'{self.author} / {self.text}'


class Follow(models.Model):
    user = models.ForeignKey(User,
                             verbose_name='Пользователь',
                             related_name='follower',
                             on_delete=models.CASCADE,
                             help_text='Пользователь')
    author = models.ForeignKey(User,
                               verbose_name='Автор постов',
                               related_name='following',
                               on_delete=models.CASCADE,
                               help_text='Автор постов')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'author'],
                                               name='unique_following_author')
                       ]

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Автор не может быть подписан на самого '
                                  'себя')

    def __str__(self):
        return f'Пользователь: {self.user} / Автор: {self.author}'
