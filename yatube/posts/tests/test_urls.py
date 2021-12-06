from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тест',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст ' * 8
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованный клиент, автора
        self.authorized_client = Client()
        self.author = PostURLTests.author
        self.authorized_client.force_login(self.author)
        # Создаем клиент не автора
        self.not_author_client = Client()
        self.user = PostURLTests.user
        self.not_author_client.force_login(self.user)

    def test_urls_uses_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_name = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': PostURLTests.group.slug}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': self.author.username}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': PostURLTests.post.id}): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={
                'post_id': PostURLTests.post.id}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for address, template in templates_url_name.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_available_auauthorized_user(self):
        """
        URL-адрес доступен по указанному адресу не авторизованному
        пользователю
        """
        url_address = {
            'index': reverse('posts:index'),
            'group_list': reverse('posts:group_list',
                                  kwargs={'slug': PostURLTests.group.slug}),
            'post_detail': reverse('posts:post_detail',
                                   kwargs={'post_id': PostURLTests.post.id}),
            'add_comment': reverse('posts:add_comment',
                                   kwargs={'post_id': PostURLTests.post.id}),
            'profile_follow': reverse('posts:profile_follow',
                                      kwargs={
                                          'username': self.author.username}),
            'profile_unfollow': reverse('posts:profile_follow',
                                        kwargs={
                                            'username': self.author.username}),
        }
        for name, address in url_address.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_available_authorized_user(self):
        """URL-адрес доступен авторизованному пользователю"""
        url_address = {
            'index': reverse('posts:index'),
            'group_list': reverse('posts:group_list',
                                  kwargs={'slug': PostURLTests.group.slug}),
            'post_detail': reverse('posts:post_detail',
                                   kwargs={'post_id': PostURLTests.post.id}),
            'post_crate': reverse('posts:post_create'),
            'post_edit': reverse('posts:post_edit',
                                 kwargs={'post_id': PostURLTests.post.id}),
        }
        for name, address in url_address.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_url_redirect_non_author(self):
        """
        Страница edit/ перенаправляет не автора поста на страницу
        детальной информации о посте
        """
        edit_url = reverse('posts:post_edit',
                           kwargs={'post_id': PostURLTests.post.id})
        redirect_url = reverse('posts:post_detail',
                               kwargs={'post_id': PostURLTests.post.id})
        response = self.not_author_client.get(edit_url, follow=True)
        self.assertRedirects(response, redirect_url)

    def test_url_redirect_anonymous(self):
        """
        При попытке перейти на страницу для авторизованных пользователей, не
        авторизованный пользователь перенаправляется на страницу авторизации
        """
        login_url = reverse('users:login')
        url_address = {
            'post_crate': reverse('posts:post_create'),
            'post_edit': reverse('posts:post_edit',
                                 kwargs={'post_id': PostURLTests.post.id}),
            'add_comment': reverse('posts:add_comment',
                                   kwargs={'post_id': PostURLTests.post.id}),
            'profile_follow': reverse('posts:profile_follow',
                                      kwargs={
                                          'username': self.author.username}),
            'profile_unfollow': reverse('posts:profile_follow',
                                        kwargs={
                                            'username': self.author.username}),
        }
        for name, address in url_address.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, f'{login_url}?next={address}')
