from http import HTTPStatus
import pytest
import time


@pytest.fixture
def test_user(test_user_data, test_user_email, client, admin_client, get_url):
    response = client.post(get_url('register'), json=test_user_data)
    assert (
        response.status_code == HTTPStatus.CREATED
    )  # needed in case there is already a test user in the database, since this fixture deletes the test user on teardown
    yield
    response = admin_client.delete(get_url('delete', test_user_email))
    assert (response.status_code == HTTPStatus.NO_CONTENT)  # to make sure test user is deleted


def test_Given_registered_user_When_same_user_registers_Then_error(test_user, test_user_data, client, get_url):
    response = client.post(get_url('register'), json=test_user_data)
    assert response.status_code == HTTPStatus.CONFLICT


def test_Given_running_services_When_request_Then_logs_log_at_least_something(test_user_email, admin_client, get_url, logs_to_check):
    previous_states = {f: file_contents(f) for f in logs_to_check}
    admin_client.get(get_url('get', test_user_email))
    after_states = {f: file_contents(f) for f in logs_to_check}
    for filename in logs_to_check:
        assert previous_states[filename] != after_states[filename]


def test_Given_running_services_When_pinging_PING_endpoint_Then_all_services_return_PONG(client, get_url):
    response = client.get(get_url('ping'))
    assert response.json() == {'ok': 'all services up'}


def test_Given_new_user_registration_When_at_first_there_are_no_tags_Then_after_a_few_moments_the_AI_generates_them_and_stores_in_DB(client, admin_client, tag_gen_user_credentials_json, get_url):
    email = tag_gen_user_credentials_json['email']
    response = client.post(get_url('register'), json=tag_gen_user_credentials_json)
    assert response.json()['detail']['settings']['tags'] == ''
    time.sleep(3)
    response = admin_client.get(get_url('get', email))
    admin_client.delete(get_url('delete', email))
    assert response.json()['detail']['settings']['tags'] != ''


def test_Given_user_registered_When_creating_digest_Then_result_is_generated_and_tg_bot_sends_it(test_gen_client, digest_credentials, get_url):
    contact = digest_credentials['contact_info']
    log_string = f'Sending digest to user with chat_id {contact}'
    log_before = file_contents('logs/tg_accessor.log')
    response = test_gen_client.post(get_url('digest'))
    assert response.status_code == HTTPStatus.OK
    max_retries, pause_between_retries_seconds = 10, 5
    log_entery_appeared = False
    retry = 0
    while retry < max_retries and not log_entery_appeared:
        diff = file_contents('logs/tg_accessor.log').replace(log_before, '')
        log_entery_appeared = log_string in diff
        retry += 1
        if not log_entery_appeared:
            time.sleep(pause_between_retries_seconds)
    assert log_entery_appeared is True


def file_contents(filename):
    with open(filename, 'r') as f:
        result = f.read()
    return result
