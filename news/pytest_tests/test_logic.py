import pytest

from django.urls import reverse
from pytest_django.asserts import assertFormError

from news.models import Comment
from news.forms import WARNING


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, comments_quantity',
    (
        (pytest.lazy_fixture('author_client'), 1),
        (pytest.lazy_fixture('client'), 0)
    ),
)
def test_create_comment_for_different_users(
        parametrized_client,
        comments_quantity,
        news,
        form_data):
    url = reverse('news:detail', args=(news.pk,))
    parametrized_client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == comments_quantity


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news, bad_words_data):
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(
        url,
        data=bad_words_data
    )
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, comments_quantity',
    (
        (pytest.lazy_fixture('author_client'), 0),
        (pytest.lazy_fixture('not_author_client'), 1)
    ),
)
def test_delete_comment_for_author_and_reader(
    parametrized_client,
    comments_quantity,
    comment
):
    delete_url = reverse('news:delete', args=(comment.news_id,))
    parametrized_client.delete(delete_url)
    comments_count = Comment.objects.count()
    assert comments_count == comments_quantity


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_text',
    (
        (pytest.lazy_fixture('author_client'), 'Новый текст комментария'),
        (pytest.lazy_fixture('not_author_client'), 'Текст комментария')
    ),
)
def test_edit_comment_for_different_users(
    parametrized_client,
    expected_text,
    comment,
    new_form_data
):
    edit_url = reverse('news:edit', args=(comment.news_id,))
    parametrized_client.post(edit_url, data=new_form_data)
    comment.refresh_from_db()
    assert comment.text == expected_text
