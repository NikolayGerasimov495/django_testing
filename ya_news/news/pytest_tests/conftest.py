from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

import pytest

from news.models import News, Comment

TEXT_COMMENT = 'Текст комментария'
TEXT_NEWS = 'Текст новости'
HEADING = 'Заголовок'
AUTHOR = 'Автор'
NEW_TEXT = 'Новый текст'


@pytest.fixture
def author(django_user_model):
    """Фикстура для создания пользователя."""
    return django_user_model.objects.create(username=AUTHOR)


@pytest.fixture
def author_client(author, client):
    """Фикстура для создания автора новости."""
    client.force_login(author)
    return client


@pytest.fixture
def news():
    """Фикстура для создания новости."""
    news = News.objects.create(
        title=HEADING,
        text=TEXT_NEWS,
        date=datetime.today(),
    )
    return news


@pytest.fixture
def comment(news, author):
    """Фикстура для создания коммента."""
    comment = Comment.objects.create(
        text=TEXT_COMMENT,
        news=news,
        author=author
    )
    return comment


@pytest.fixture
def list_comments(news, author):
    """Фикстура для создания списка комментариев."""
    now, list_comment = timezone.now(), []
    for index in range(2):
        comment = Comment.objects.create(
            text='Текст {index}',
            news=news,
            author=author,
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        list_comment.append(comment)


@pytest.fixture
def new_text_comment():
    """Фикстура для создания нового текста для комментария."""
    return {'text': NEW_TEXT}


@pytest.fixture
def list_news():
    """Фикстура для создания списка новостей."""
    today, list_news = datetime.today(), []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE):
        news = News.objects.create(
            title='Новость {index}',
            text=TEXT_NEWS,
        )
        news.date = today - timedelta(days=index)
        news.save()
        list_news.append(news)
    return list_news
