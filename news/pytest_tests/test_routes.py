import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
        'name',
        ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
        'client, expected_status',
        (
            (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
            (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND)
        )
)
@pytest.mark.parametrize(
        'name',
        ('news:delete', 'news:edit')
)
def test_comments_availability(client, expected_status, name, comment):
    url = reverse(name, args=(comment.pk,))
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, com_id',
    (
        ('news:delete', pytest.lazy_fixture('comment_id')),
        ('news:edit', pytest.lazy_fixture('comment_id'))
    ),
)
def test_redirects_for_anonymous_client(client, name, com_id):
    login_url = reverse('users:login')
    url = reverse(name, args=com_id)
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)