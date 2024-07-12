import pytest
from http import HTTPStatus
from setup import user_endpoint_url, logs_to_check


@pytest.fixture
def test_user(test_user_data, test_user_email, client, admin_client):
    response = client.post(user_endpoint_url('register'), json=test_user_data)
    assert (
        response.status_code == HTTPStatus.CREATED
    )  # needed in case there is already a test user in the database, since this fixture deletes the test user on teardown
    yield
    response = admin_client.delete(user_endpoint_url('delete', test_user_email))
    assert (response.status_code == HTTPStatus.NO_CONTENT)  # to make sure test user is deleted


def test_Given_registered_user_When_same_user_registers_Then_error(test_user, test_user_data, client):
    response = client.post(user_endpoint_url('register'), json=test_user_data)
    assert response.status_code == HTTPStatus.CONFLICT


def test_Given_running_services_When_request_Then_logs_log_at_least_something(test_user_email, admin_client):
    previous_states = {f: file_contents(f) for f in logs_to_check}
    admin_client.get(user_endpoint_url('get', test_user_email))
    after_states = {f: file_contents(f) for f in logs_to_check}
    for filename in logs_to_check:
        assert previous_states[filename] != after_states[filename]


def test_Given_running_services_When_pinging_PING_endpoint_Then_all_services_return_PONG(client):
    response = client.get(user_endpoint_url('ping'))
    assert response.json() == {'ok': 'all services up'}


def file_contents(filename):
    with open(filename, 'r') as f:
        result = f.read()
    return result
