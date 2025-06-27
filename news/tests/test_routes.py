from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from news.models import News, Comment


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(title='Заголовок', text='Текст')
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.comment = Comment.objects.create(
            news=cls.news,
            author=cls.author,
            text='Текст комментария'
        )

    def test_pages_availability(self):
        urls = (
            ('news:home', None),
            ('news:detail', (self.news.pk,)),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )

        for name, args in urls:
            with self.subTest():
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_comments_availability(self):
        urls = (
            ('news:delete', (self.comment.pk,)),
            ('news:edit', (self.comment.pk,)),
        )
        user_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            for name, args in urls:
                with self.subTest():
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')

        for name in ('news:delete', 'news:edit'):
            url = reverse(name, args=(self.comment.id,))
            redirect_url = f'{login_url}?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, redirect_url)
