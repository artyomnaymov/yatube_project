from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тест',
            slug='test',
            description='Тестовое описание',
        )

    def test_fields_group_model(self):
        """
        verbose_name поля title модели Group совпадает с ожидаемым
        help_text поля title модели Group совпадает с ожидаемым
        """
        group = GroupModelTest.group
        verbose_name = group._meta.get_field('title').verbose_name
        help_text = group._meta.get_field('title').help_text
        fields = {
            verbose_name: 'Название группы',
            help_text: 'Название группы',
        }
        for field, expected_value in fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_value)

    def test_group_object_name_is_title_fild(self):
        """__str__  group - это строчка с содержимым group.title."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст ' * 8
        )

    def test_fields_post_model(self):
        """
        verbose_name поля title модели Post совпадает с ожидаемым
        help_text поля title модели Post совпадает с ожидаемым
        """
        post = PostModelTest.post
        verbose_name = post._meta.get_field('text').verbose_name
        help_text = post._meta.get_field('text').help_text
        fields = {
            verbose_name: 'Текст поста',
            help_text: 'Текст нового поста',
        }
        for field, expected_value in fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_value)

    def test_post_object_name_is_title_fild(self):
        """__str__  post - это строчка с содержимым post.title."""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))
