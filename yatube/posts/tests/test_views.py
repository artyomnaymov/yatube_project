from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post

User = get_user_model()


class PostsPagePaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Group',
            slug='group',
            description='group_description',
        )
        number_of_posts = 13
        post_list = []
        for i in range(number_of_posts):
            text = f'Post_number_{i} ' * 8
            post_list.append(Post(author=cls.user,
                                  group=cls.group,
                                  text=text))
        Post.objects.bulk_create(post_list)

    def setUp(self):
        # Создаем авторизованный клиент
        self.authenticate_client = Client()
        self.user = PostsPagePaginatorTests.user
        self.authenticate_client.force_login(self.user)

    def test_paginator_pages(self):
        """
        Страницы со списком постов, на первой странице, содержат 10 постов.
        На второй странице постов, страница содержит 3 поста
        """
        page_names = {
            'index': reverse('posts:index'),
            'group_list': reverse('posts:group_list', kwargs={
                'slug': PostsPagePaginatorTests.group.slug}),
            'profile': reverse('posts:profile', kwargs={
                'username': self.user.username}),
        }
        for name, reverse_name in page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response_first_page = self.authenticate_client.get(
                    reverse_name
                )
                response_second_page = self.authenticate_client.get(
                    reverse_name + '?page=2'
                )
                self.assertEqual(len(response_first_page.context['page_obj']),
                                 10, 'У авторизованного пользователя, '
                                     'Количество записей на первой '
                                     'странице отличается от ожидаемого')
                self.assertEqual(len(response_second_page.context['page_obj']),
                                 3, 'У авторизованного пользователя, '
                                    'Количество записей на второй странице '
                                    'отличается от ожидаемого')


class PostsPageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        # cls.user = User.objects.create_user(username='test_user1')
        cls.first_group = Group.objects.create(
            title='First_group',
            slug='first_group',
            description='first_group_description',
        )
        cls.second_group = Group.objects.create(
            title='Second_group',
            slug='second_group',
            description='second_group_description',
        )
        cls.post = Post.objects.create(author=cls.author,
                                       group=cls.first_group,
                                       text='Test_text')

    def setUp(self):
        # Создаем авторизованный клиент автора
        self.author_client = Client()
        self.author = PostsPageTests.author
        self.author_client.force_login(self.author)

    def test_page_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': PostsPageTests.first_group.slug}):
                    'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': self.author.username}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': PostsPageTests.post.id}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={
                'post_id': PostsPageTests.post.id}): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_with_list_show_correct_context(self):
        """
        Шаблоны страниц содержащей список постов сформированы с правильным
        контекстом
        """
        context_page_names = {
            reverse('posts:index'): Post.objects.all(),
            reverse('posts:group_list', kwargs={
                'slug': PostsPageTests.first_group.slug}): Post.objects.filter(
                group=PostsPageTests.first_group
            ),
            reverse('posts:profile', kwargs={
                'username': self.author.username}): Post.objects.filter(
                author=self.author
            ),
        }
        for reverse_name, post_obj in context_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                objects = response.context['page_obj'][:]
                posts_list = list(post_obj)[:10]
                post_text = objects[0].text
                post_pub_date = objects[0].created
                post_author = objects[0].author
                post_group = objects[0].group
                post_image = objects[0].image
                self.assertIsInstance(objects, list)
                self.assertEqual(objects, posts_list)
                self.assertEqual(post_text, PostsPageTests.post.text)
                self.assertEqual(post_pub_date, PostsPageTests.post.created)
                self.assertEqual(post_author, PostsPageTests.post.author)
                self.assertEqual(post_group, PostsPageTests.post.group)
                self.assertEqual(post_image, PostsPageTests.post.image)

    def test_post_detail_page_show_correct_context(self):
        """Страница post_detail сформирована с правильным контекстом"""
        url = reverse('posts:post_detail',
                      kwargs={'post_id': PostsPageTests.post.id})
        response = self.author_client.get(url)
        post = Post.objects.get(id=PostsPageTests.post.id)
        self.assertEqual(response.context['post'], post,
                         'На страницу post_detail/ передается некорректный '
                         'контекст')

    def test_create_page_show_correct_context(self):
        """Шаблон create/ сформирован с правильным контекстом"""
        url = reverse('posts:post_create')
        response = self.author_client.get(url)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                field = response.context.get('form').fields.get(value)
                self.assertIsInstance(field, expected,
                                      f'Поле {field} не является экземпляром '
                                      f'класса {expected}')

    def test_edit_page_show_correct_context(self):
        """Шаблон post_edit/ сформирован с правильным контекстом"""
        url = reverse('posts:post_edit',
                      kwargs={'post_id': PostsPageTests.post.id})
        response = self.author_client.get(url)
        post = Post.objects.get(id=PostsPageTests.post.id)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                field = response.context.get('form').fields.get(value)
                self.assertIsInstance(field, expected,
                                      f'Поле {field} не является экземпляром '
                                      f'класса {expected}')
        self.assertEqual(response.context['post'], post,
                         'На страницу post_edit/ передается некорректный '
                         'контекст')

    def test_new_post_showed_on_index_group_profile_pages(self):
        """
        Новый пост, у которого указан группа, отображается на главной
        странице, на странице постов группы и странице постов автора
        """
        form_data = {
            'text': 'Test text',
            'author': f'{PostsPageTests.author}',
            'group': f'{PostsPageTests.first_group.id}',
        }
        self.author_client.post(reverse('posts:post_create'), data=form_data)
        new_post = Post.objects.get(text=form_data.get('text'))
        page_names = {
            'index': reverse('posts:index'),
            'group_list': reverse('posts:group_list', kwargs={
                'slug': PostsPageTests.first_group.slug}),
            'profile': reverse('posts:profile', kwargs={
                'username': self.author.username}),
        }
        for name, reverse_name in page_names.items():
            with self.subTest(reverse_name=reverse_name):
                post_context = self.author_client.get(reverse_name)
                posts_on_page = post_context.context['page_obj'][:]
                self.assertIn(new_post, posts_on_page,
                              'Пост не отображается в группе, к которой '
                              'принадлежит')

    def test_new_post_with_group_showed_only_in_this_group(self):
        """
        Новый пост, у которого указан группа, не отображается на странице со
        списком постов группы, к которой он не принадлежит
        """
        url = reverse('posts:group_list',
                      kwargs={'slug': PostsPageTests.second_group.slug})
        create_url = reverse('posts:post_create')
        form_data = {
            'text': 'Test text',
            'author': f'{PostsPageTests.author}',
            'group': f'{PostsPageTests.first_group.id}',
        }
        self.author_client.post(create_url, data=form_data)
        new_post = Post.objects.get(text=form_data.get('text'))
        posts_on_page = self.author_client.get(url).context['page_obj'][:]
        self.assertNotIn(new_post, posts_on_page,
                         'Пост отображается в группе, которой не принадлежит')

    def test_cash_on_index_page(self):
        """Список постов кешируется на главной страницы """
        index_url = reverse('posts:index')
        post_create_url = reverse('posts:post_create')
        form_data = {
            'text': 'Test_cash_on_index_page text',
            'author': f'{PostsPageTests.author}',
        }
        # создаем новый пост
        self.author_client.post(post_create_url, data=form_data)
        new_post = Post.objects.get(text=form_data.get('text'))
        # получаем список постов на странице index
        response = self.author_client.get(index_url)
        posts_on_page = response.context['page_obj'][:]
        # Проверяем, что новый пост отображается на странице
        self.assertIn(new_post, posts_on_page)
        # удаляем пост
        Post.objects.get(text=form_data.get('text')).delete()
        # получаем список постов на странице index
        posts_on_page = response.context['page_obj'][:]
        # проверяем, что пост отображается на странице без очистки кеша
        self.assertIn(new_post, posts_on_page)
        # Чистим кеш
        cache.clear()
        # получаем список постов на странице index
        response = self.author_client.get(index_url)
        posts_on_page = response.context['page_obj'][:]
        # Проверяем, что пост не отображается на странице после очистки кеша
        self.assertNotIn(new_post, posts_on_page)


class CommentTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test_text'
        )

    def setUp(self):
        # Создаем авторизованный клиент автора
        self.authorized_client = Client()
        self.user = CommentTests.user
        self.authorized_client.force_login(self.user)

    def test_new_comment_showed_on_post_detail_pages(self):
        """Новый комментарий отображается на странице post_detail"""
        comment_url = reverse('posts:add_comment',
                              kwargs={
                                  'post_id': CommentTests.post.id})
        post_detail_url = reverse('posts:post_detail',
                                  kwargs={'post_id': CommentTests.post.id})
        form_data = {
            'text': 'Test comment text',
        }
        self.authorized_client.post(comment_url, data=form_data)
        new_comment = Comment.objects.get(text=form_data.get('text'))
        comment_context = self.authorized_client.get(post_detail_url)
        comment_on_page = comment_context.context['comments']
        self.assertIn(new_comment, comment_on_page,
                      'Комментарий не отображается на странице post_detail')


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author_one')
        cls.author_two = User.objects.create_user(username='author_two')
        cls.follow_user = User.objects.create_user(username='follow_user')
        cls.user = User.objects.create_user(username='user')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Post_test_text'
        )

    def setUp(self):
        # Создаем авторизованный клиент пользователя, который подписан на
        # автора
        self.authorized_client_follow = Client()
        self.follow_user = FollowTests.follow_user
        self.authorized_client_follow.force_login(self.follow_user)
        # Создаем авторизованный клиент пользователя, без подписки на автора
        self.authorized_client_user = Client()
        self.user = FollowTests.user
        self.authorized_client_user.force_login(self.user)
        # Создаем подписку на пользователя
        Follow.objects.create(
            author=FollowTests.author_two,
            user=FollowTests.follow_user
        )

    def test_authorized_user_can_follow_author(self):
        """Авторизованный пользователь может подписаться на автора"""
        follow_url = reverse('posts:profile_follow',
                             kwargs={'username': self.author.username})
        # считаем начальное количество записей подписей на авторов в БД
        follow_count = Follow.objects.count()
        # подписываемся на автора
        self.authorized_client_follow.get(follow_url)
        # проверяем, что подписка на автора осуществилась
        self.assertEqual(Follow.objects.count(), follow_count + 1,
                         'При подписке на автора произошла ошибка')
        self.assertEqual(FollowTests.author_two.username,
                         self.author_two.username,
                         'Автор, на которого подписался пользователь, '
                         'не соответствует тому, на которого он подписывался')

    def test_authorized_user_can_unfollow_author(self):
        """Авторизованный пользователь может отписаться от автора"""
        unfollow_url = reverse('posts:profile_unfollow',
                               kwargs={'username': self.author_two.username})
        # считаем начальное количество записей подписей на авторов в БД
        follow_count = Follow.objects.count()
        # отписываемся от автора
        self.authorized_client_follow.get(unfollow_url)
        # проверяем, что отписка от автора осуществилась
        self.assertEqual(Follow.objects.count(), follow_count - 1,
                         'При отписке от автора произошла ошибка')
        self.assertEqual(FollowTests.author_two.username,
                         self.author_two.username,
                         'Автор, от которого отписывается пользователь, '
                         'не соответствует тому, от которого он отписывается')

    def test_post_showed_on_following_page_for_following_user(self):
        """
        Пост автора отображается в ленте тех, кто на него подписан
        """
        follow_index_url = reverse('posts:follow_index')
        post = Post.objects.create(author=FollowTests.author_two,
                                   text='Post_test_text_two')
        posts_on_follow_page = self.authorized_client_follow.get(
            follow_index_url).context['page_obj'][:]
        # Проверяем, что новый пост автора отображается на странице
        # follow_index пользователя, который подписан на автора
        self.assertIn(post, posts_on_follow_page,
                      'Пост не отображается на странице follow_index')

    def test_post_not_showed_on_following_page_for_unfollowing_user(self):
        """
        Пост автора не отображается в ленте тех, кто на него не подписан
        """
        follow_index_url = reverse('posts:follow_index')
        post = Post.objects.create(author=FollowTests.author_two,
                                   text='Post_test_text_two')
        posts_on_user_page = self.authorized_client_user.get(
            follow_index_url).context['page_obj'][:]
        # Проверяем, что пост автора не отображается на странице
        # follow_index пользователя, который не подписан на автора
        self.assertNotIn(post, posts_on_user_page,
                         'Пост отображается на странице follow_index')
