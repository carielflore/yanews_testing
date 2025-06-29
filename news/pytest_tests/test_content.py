import pytest

from django.conf import settings
from django.urls import reverse
from news.models import News


@pytest.mark.django_db
def test_news_count(client, home_url, add_news):
    response = client.get(home_url)
    news_quantity = response.context['object_list'].count()
    assert news_quantity == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_ordering(client, home_url, add_news):
    response = client.get(home_url)
    news_objects = response.context['object_list']
    dates = [news.date for news in news_objects]
    expected_dates = sorted(dates, reverse=True)
    assert dates == expected_dates


@pytest.mark.django_db
def test_comment_order(client, add_comments):
    news_id = News.objects.get().id
    url = reverse('news:detail', args=(news_id,))
    response = client.get(url)
    comments = response.context['news'].comment_set.all()
    dates = [comment.created for comment in comments]
    sorted_dates = sorted(dates)
    assert dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, is_author',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False)
    ),
)
def test_authorized_client_has_form(parametrized_client, is_author, news):
    news_id = news.id
    url = reverse('news:detail', args=(news_id,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) == is_author
