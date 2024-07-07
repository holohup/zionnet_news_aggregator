import pytest
from http import HTTPStatus
from config import endpoint_url, logs_to_check


@pytest.fixture
def test_user(anonymous_client, test_user_data, test_user_email):
    response = anonymous_client.post(endpoint_url('register'), content=test_user_data)
    assert response.status_code == HTTPStatus.CREATED  # needed in case there is already a test user in the database, since this fixture deletes the test user on teardown
    yield
    response = anonymous_client.delete(endpoint_url('delete', test_user_email))
    assert response.status_code == HTTPStatus.NO_CONTENT  # to make sure test user is deleted


def test_Given_registered_user_When_same_user_registers_Then_error(anonymous_client, test_user, test_user_data):
    response = anonymous_client.post(endpoint_url('register'), content=test_user_data)
    assert response.status_code == HTTPStatus.CONFLICT


def test_Given_running_services_When_request_Then_logs_log_at_least_something(anonymous_client, test_user_data, test_user_email):
    previous_states = {f: file_contents(f) for f in logs_to_check}
    anonymous_client.post(endpoint_url('register'), content=test_user_data) # change to read when implemented in order not to change state
    after_states = {f: file_contents(f) for f in logs_to_check}
    for filename in logs_to_check:
        assert previous_states[filename] != after_states[filename]
    anonymous_client.delete(endpoint_url('delete', test_user_email)) # remove when done


def file_contents(filename):
    with open(filename, 'r') as f:
        result = f.read()
    return result
