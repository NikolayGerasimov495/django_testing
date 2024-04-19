from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.models import Comment
from .conftest import TEXT_COMMENT


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    new_text_comment = {'text': 'Новый комментарий'}
    initial_comments_count = Comment.objects.count()
    client.post(url, data=new_text_comment)
    assert Comment.objects.count() == initial_comments_count


def test_user_can_create_comment(author_client, author, news):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    new_text_comment = {'text': 'Новый комментарий'}
    initial_comments_count = Comment.objects.count()
    author_client.post(url, data=new_text_comment)
    assert Comment.objects.count() == initial_comments_count + 1
    comment = Comment.objects.last()
    assert comment.text == new_text_comment['text']
    assert comment.news == news
    assert comment.author == author


def test_author_can_delete_comment(author_client, news, comment):
    """Авторизованный пользователь может удалять свои комментарии."""
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = reverse('news:delete', args=(comment.id,))
    initial_comments_count = Comment.objects.count()
    response = author_client.delete(url_to_comments)
    assertRedirects(response, news_url + '#comments')
    assert Comment.objects.count() == initial_comments_count - 1


def test_user_cant_delete_comment_of_another_user(admin_client, comment):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    comment_url = reverse('news:delete', args=(comment.id,))
    initial_comments_count = Comment.objects.count()
    response = admin_client.delete(comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_comments_count


def test_author_can_edit_comment(author_client, news, comment):
    """Авторизованный пользователь может редактировать свои комментарии."""
    news_url = reverse('news:detail', args=(news.id,))
    comment_url = reverse('news:edit', args=(comment.id,))
    new_text_comment = {'text': 'Измененный комментарий'}
    response = author_client.post(comment_url, data=new_text_comment)
    assertRedirects(response, news_url + '#comments')
    comment.refresh_from_db()
    assert comment.text == new_text_comment['text']


def test_user_cant_edit_comment_of_another_user(admin_client, comment):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    comment_url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(
        comment_url, data={'text': 'Новый текст комментария'}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == TEXT_COMMENT
