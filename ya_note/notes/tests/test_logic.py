from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from .base_test_case import BaseTestCase
from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify


User = get_user_model()


class TestNotes(BaseTestCase):

    def setUp(self):
        self.data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        url = reverse('notes:add')
        response = self.author_client.post(url, data=self.data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.exists(), True)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.data['title'])
        self.assertEqual(new_note.text, self.data['text'])
        self.assertEqual(new_note.slug, self.data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        url = reverse('notes:add')
        response = self.client.post(url, self.data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.exists(), False)

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:add')
        response = self.author_client.post(url, data={
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': self.note.slug,
        })
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.exists(), True)

    def test_empty_slug(self):
        """Если при создании заметки не заполнен slug,
        то он формируетсz автоматически, с помощью функции
        pytils.translit.slugify.
        """
        url = reverse('notes:add')
        self.data.pop('slug')
        response = self.author_client.post(url, self.data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.exists(), True)
        new_note = Note.objects.get()
        expected_slug = slugify(self.data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_delete_note(self):
        """Пользователь может удалять свои заметки."""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.author_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.exists(), False)

    def test_other_user_cant_delete_note(self):
        """Пользователь не может удалять чужие заметки."""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.auth_user_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.exists(), True)

    def test_author_can_edit_note(self):
        """Пользователь может редактировать свои заметки."""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.author_client.post(url, self.data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.data['title'])
        self.assertEqual(self.note.text, self.data['text'])
        self.assertEqual(self.note.slug, self.data['slug'])

    def test_other_user_cant_edit_note(self):
        """Пользователь не может редактировать чужие заметки."""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.auth_user_client.post(url, self.data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.title, self.data['title'])
        self.assertNotEqual(self.note.text, self.data['text'])
        self.assertNotEqual(self.note.slug, self.data['slug'])
