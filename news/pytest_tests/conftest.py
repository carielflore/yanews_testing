import pytest
from datetime import datetime, timedelta

from django.test.client import Client
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from news.models import News, Comment
from news.forms import BAD_WORDS


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Новость',
        text='Текст новости',
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def comment_id(comment):
    return (comment.id,)


@pytest.fixture
def home_url():
    url = reverse('news:home')
    return url


@pytest.fixture
def add_news():
    News.objects.bulk_create([
        News(
            title=f'Новость {index}',
            text='Текст.',
            date=datetime.today() - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ])


@pytest.fixture
def add_comments(author, news):
    now = timezone.now()
    for index in range(10):
        comment = Comment(
            news=news,
            author=author,
            text=f'Комментарий {index}',
        )
        comment.created = now - timedelta(days=index)
        comment.save()


@pytest.fixture
def form_data():
    data = {
        'text': 'Текст комментария'
    }
    return data


@pytest.fixture
def bad_words_data():
    text = {'text': f'Какой-то текст {BAD_WORDS[0]}, ещё текст'}
    return text


@pytest.fixture
def new_form_data():
    data = {
        'text': 'Новый текст комментария'
    }
    return data
