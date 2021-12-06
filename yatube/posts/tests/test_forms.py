import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Test',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст ' * 8
        )

    def setUp(self):
        # Создаем клиент неавторизованного пользователя
        self.guest_client = Client()
        # Создаем клиент авторизованного пользователя
        self.authorized_client = Client()
        self.author = PostCreateFormTests.author
        self.authorized_client.force_login(self.author)

    def tearDown(self):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post"""
        create_url = reverse('posts:post_create')
        redirect_url = reverse('posts:profile',
                               kwargs={'username': self.author.username})
        post_count = Post.objects.count()
        # байт последовательность изображения (для тестирования загрузки)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')
        # загружаем сформированное изображение
        uploaded = SimpleUploadedFile(name='small.gif', content=small_gif,
                                      content_type='image/gif')
        form_data = {
            'text': 'Test text',
            'author': f'{PostCreateFormTests.author}',
            'group': f'{PostCreateFormTests.group.id}',
            'image': uploaded,
        }
        # отправляем POST запрос
        response = self.authorized_client.post(create_url, data=form_data,
                                               follow=True)
        new_post = Post.objects.get(text=form_data.get('text'))
        # проверяем, Http код, который возвращается в запросе
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # проверяем, что после создания поста есть редирект на profile
        self.assertRedirects(response, redirect_url)
        # проверяем, что количество постов изменилось на +1
        self.assertEqual(Post.objects.count(), post_count + 1,
                         'После создания поста не изменилось общее '
                         'количество записей')
        # проверяем, что создался новый пост
        self.assertTrue(
            Post.objects.filter(
                text=form_data.get('text'),
                author=PostCreateFormTests.author,
                group=PostCreateFormTests.group,
            ).exists(), 'Новый пост не был создан'
        )
        # проверяем, что новый пост создался с теми значениями, которые были
        # переданы в форме
        self.assertEqual(new_post.text, form_data.get('text'),
                         'Текст нового поста не соответствует тому, который '
                         'передавался в форму')
        self.assertEqual(new_post.author, PostCreateFormTests.author,
                         'Автор нового поста не соответствует тому, который '
                         'передавался в форму'
                         )
        self.assertEqual(new_post.group, PostCreateFormTests.group,
                         'Группа нового поста не соответствует той, которая '
                         'передавалась в форму'
                         )
        self.assertEqual(new_post.image, 'posts/small.gif',
                         'Изображение нового поста не соответствует тому, '
                         'которое передавалось в форму')

    def test_update_post(self):
        """Валидная форма обновляет запись в Post"""
        edited_post = PostCreateFormTests.post.id
        update_url = reverse('posts:post_edit',
                             kwargs={'post_id': edited_post})
        redirect_url = reverse('posts:post_detail',
                               kwargs={'post_id': PostCreateFormTests.post.id})
        post_count = Post.objects.count()
        # байт последовательность изображения (для тестирования загрузки)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')
        # загружаем сформированное изображение
        uploaded = SimpleUploadedFile(name='small.gif', content=small_gif,
                                      content_type='image/gif')
        form_data = {
            'text': 'Test text_2',
            'author': f'{PostCreateFormTests.author}',
            'group': f'{PostCreateFormTests.group.id}',
            'image': uploaded,
        }
        response = self.authorized_client.post(update_url, data=form_data,
                                               follow=True)
        new_post = Post.objects.get(text=form_data.get('text'))
        # проверяем, Http код, который возвращается в запросе
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # проверяем, что после обновления поста есть редирект на post_detail
        self.assertRedirects(response, redirect_url)
        # проверяем, что количество постов не изменилось
        self.assertEqual(Post.objects.count(), post_count,
                         'После обновления поста, общее количество записей '
                         'изменилось')
        # проверяем, что существует поста с обновленным текстом
        self.assertTrue(
            Post.objects.filter(
                text=form_data.get('text'),
                author=PostCreateFormTests.author,
                group=PostCreateFormTests.group,
            ).exists(), 'Старый пост не обновлен'
        )
        # проверяем, что новый пост создался с теми значениями, которые были
        # переданы в форме
        self.assertEqual(new_post.text, form_data.get('text'),
                         'Текст поста при обновлении не соответствует тому, '
                         'который передавался в форму')
        self.assertEqual(new_post.author, PostCreateFormTests.author,
                         'Автор поста при обновлении не соответствует тому, '
                         'который передавался в форму'
                         )
        self.assertEqual(new_post.group, PostCreateFormTests.group,
                         'Группа поста при обновлении не соответствует той, '
                         'которая передавалась в форму'
                         )
        self.assertEqual(new_post.image, 'posts/small.gif',
                         'Изображение нового поста не соответствует тому, '
                         'которое передавалось в форму')
        # проверяем, что поста со старым текстом не существует
        self.assertFalse(
            Post.objects.filter(
                text=PostCreateFormTests.post.text,
                author=PostCreateFormTests.author,
                group=PostCreateFormTests.group,
            ).exists(), 'Старый пост не обновлен'
        )

    def test_unauthorized_user_cant_create_post(self):
        create_url = reverse('posts:post_create')
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={create_url}'
        post_count = Post.objects.count()
        form_data = {
            'text': 'Test text',
            'author': f'{PostCreateFormTests.author}',
            'group': f'{PostCreateFormTests.group.id}',
        }
        response = self.guest_client.post(create_url, data=form_data,
                                          follow=True)
        # проверяем, Http код, который возвращается в запросе
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # проверяем, что неавторизованного пользователя перенаправляет на
        # страницу авторизации
        self.assertRedirects(response, redirect_url)
        # проверяем, что количество постов не изменилось
        self.assertEqual(Post.objects.count(), post_count)


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст ' * 8
        )

    def setUp(self):
        # Создаем клиент неавторизованного пользователя
        self.guest_client = Client()
        # Создаем клиент авторизованного пользователя
        self.authorized_client = Client()
        self.author = CommentCreateFormTests.author
        self.authorized_client.force_login(self.author)

    def test_unauthorized_user_cant_create_comment(self):
        comment_url = reverse('posts:add_comment',
                              kwargs={
                                  'post_id': CommentCreateFormTests.post.id})
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={comment_url}'
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Test comment',
        }
        response = self.guest_client.post(comment_url, data=form_data,
                                          follow=True)
        # проверяем, Http код, который возвращается в запросе
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # проверяем, что неавторизованного пользователя перенаправляет на
        # страницу авторизации
        self.assertRedirects(response, redirect_url)
        # проверяем, что количество постов не изменилось
        self.assertEqual(Comment.objects.count(), comment_count)

    def test_create_comment(self):
        """Валидная форма создает запись в Comment"""
        comment_url = reverse('posts:add_comment',
                              kwargs={
                                  'post_id': CommentCreateFormTests.post.id})
        redirect_url = reverse('posts:post_detail',
                               kwargs={
                                   'post_id': CommentCreateFormTests.post.id})
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Test comment',
        }
        # отправляем POST запрос
        response = self.authorized_client.post(comment_url, data=form_data,
                                               follow=True)
        new_comment = Comment.objects.get(text=form_data.get('text'))
        # проверяем, Http код, который возвращается в запросе
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # проверяем, что после создания комментария есть редирект на
        # post_detail
        self.assertRedirects(response, redirect_url)
        # проверяем, что количество комментариев изменилось на +1
        self.assertEqual(Comment.objects.count(), comment_count + 1,
                         'После создания комментария не изменилось общее '
                         'количество комментариев')
        # проверяем, что создался новый комментарий
        self.assertTrue(
            Comment.objects.filter(
                text=form_data.get('text'),
            ).exists(), 'Новый комментарий не был создан'
        )
        # проверяем, что новый комментарий создался с теми значениями, которые
        # были переданы в форме
        self.assertEqual(new_comment.text, form_data.get('text'),
                         'Текст нового комментария не соответствует тому, '
                         'который передавался в форму')
