from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    # Проверяем что Url-адреса доступен
    def test_static_urls_exist_at_desired_location(self):
        """URL-адрес доступен по указанному адресу"""
        url_address = {
            'tech': '/about/tech/',
            'author': '/about/author/',
        }
        for name, address in url_address.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем что Url-адреса используют соответствующие шаблоны
    def test_static_urls_uses_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_name = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, address in templates_url_name.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_static_page_uses_correct_template(self):
        templates_page_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech')
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
