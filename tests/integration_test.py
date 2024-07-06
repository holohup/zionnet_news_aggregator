import pytest
from http import HTTPStatus
from config import endpoint_url


@pytest.fixture
def test_user(anonymous_client, test_user_data, test_user_email):
    response = anonymous_client.post(endpoint_url('register'), content=test_user_data)
    assert response.status_code == HTTPStatus.CREATED  # needed in case there is already a test user in the database, since this fixture deletes the test user on teardown
    yield
    response = anonymous_client.delete(endpoint_url('delete', test_user_email))
    assert response.status_code == HTTPStatus.NO_CONTENT  # to make sure test user is deleted


def test_given_registered_user_when_same_user_registers_then_error(anonymous_client, test_user, test_user_data):
    response = anonymous_client.post(endpoint_url('register'), content=test_user_data)
    assert response.status_code == HTTPStatus.CONFLICT
