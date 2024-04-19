from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from .base_test_case import BaseTestCase
from notes.models import Note

User = get_user_model()


class TestRoutesPageAvailability(BaseTestCase):

    home_urls = (
        'notes:home',
        'users:login',
        'users:logout',
        'users:signup',
    )

    auth_user_urls = (
        'notes:list',
        'notes:success',
        'notes:add',
    )

    detail_urls = (
        'notes:detail',
        'notes:edit',
        'notes:delete',
    )

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )

    def test_home_availability_for_anonymous_user(self):
        """Для доступа всем пользователям к страницам:
        главная, регистирация, вход/выход в учетку
        """
        for name in self.home_urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Аутентифицированному пользователю доступны
        страницы notes/, done/, add/.
        """
        for name in self.auth_user_urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        """Автору доступно: отдеальная заметка, редактирование, удаление.
        Иначе — вернётся ошибка 404.
        """
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.auth_user_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for name in self.detail_urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects(self):
        """Перенаправление анонимного пользователя на страницу логина
        при попытках зайти на различные страницы.
        """
        login_url = reverse('users:login')

        urls_to_test = self.auth_user_urls + self.detail_urls
        for name in urls_to_test:
            with self.subTest(name=name):
                url = reverse(name,
                              args=(self.note.slug,)
                              ) if name in self.detail_urls else reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
