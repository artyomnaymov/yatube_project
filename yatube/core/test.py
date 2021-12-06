from http import HTTPStatus

from django.test import Client, TestCase


class CorePageTests(TestCase):

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()

    def test_non_exist_url_return_404(self):
        """Несуществующая страница возвращает 404"""
        non_exist_url = '/posts/test/'
        response = self.guest_client.get(non_exist_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_non_exist_url_use_custom_template(self):
        """Страница 404 использует кастомный шаблон"""
        non_exist_url = '/posts/test/'
        template = 'core/404.html'
        response = self.guest_client.get(non_exist_url)
        self.assertTemplateUsed(response, template)
