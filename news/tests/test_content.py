from datetime import datetime, timedelta 

from django.test import TestCase
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from news.models import News, Comment
from news.forms import CommentForm

User = get_user_model()


class TestContent(TestCase):
    HOME_URL = reverse('news:home')

    @classmethod
    def setUpTestData(cls):
        News.objects.bulk_create([
            News(
                title=f'Новость {index}',
                text='Текст.',
                date=datetime.today() - timedelta(days=index),
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        ])

    def test_news_count(self):
        response = self.client.get(self.HOME_URL)
        news_quantity = response.context['object_list'].count()
        self.assertEqual(news_quantity, settings.NEWS_COUNT_ON_HOME_PAGE)

    def test_news_order(self):
        response = self.client.get(self.HOME_URL)
        news_objects = response.context['object_list']
        dates = [news.date for news in news_objects]
        sorted_dates = sorted(dates, reverse=True)
        self.assertEqual(dates, sorted_dates)


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(title='Новость', text='Текст')
        cls.detail_url = reverse('news:detail', args=(cls.news.pk,))
        cls.author = User.objects.create(username='Комментатор')
        now = timezone.now()
        for index in range(10):
            comment = Comment(
                news=cls.news,
                author=cls.author,
                text=f'Комментарий {index}',
            )
            comment.created = now - timedelta(days=index)
            comment.save()

    def test_comment_order(self):
        response = self.client.get(self.detail_url)
        comment_list = response.context['news'].comment_set.all()
        dates = [comment.created for comment in comment_list]
        sorted_dates = sorted(dates)
        self.assertEqual(dates, sorted_dates)

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], CommentForm)

    def test_anonymous_client_has_no_form(self):
        response = self.client.get(self.detail_url)
        self.assertNotIn('form', response.context)
