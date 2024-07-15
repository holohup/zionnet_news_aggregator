import time
import pytest
from httpx import Client


host = 'http://127.0.0.1:8000'
endpoints = {
    'register': '/user/register',
    'delete': '/user/delete',
    'get': '/user/info',
    'token': '/token',
    'ping': '/ping',
    'me': '/user/me',
    'digest': '/digest'
}


@pytest.fixture
def get_url():
    """Provide endpoints for tests."""
    def user_endpoint_url(name: str, email: str = None) -> str:

        result = host + endpoints[name]
        if email:
            result += '/' + email
        return result
    return user_endpoint_url


@pytest.fixture
def test_user_email():
    return 'testtest@testTESTtest.com'


@pytest.fixture
def test_user_data(test_user_email):
    return {
        'email': test_user_email,
        'password': 'ThisIsATestPassword',
        'info': 'I am a barbie girl',
        'contact_info': '111'
    }


@pytest.fixture
def admin_json():
    return {
        'email': 'saba_eliezer@doar.co.il',
        'password': 'this_is_a_test_password',
        'info': 'I am a test admin',
        'contact_info': '111'
    }


@pytest.fixture
def tag_gen_user_credentials_json():
    return {
        'email': 'Joshua@cnn.com',
        'password': 'this_is_a_test_password',
        'info': "I'm Johny Mnemonic, and I'm a recent college graduate with a Bachelor's Degree in Web Design. I'm seeking a full-time opportunity where I can employ my programming skills.",
        'contact_info': '111'
    }


@pytest.fixture
def digest_credentials():
    return {
        'email': 'mickey@mail.co.il',
        'password': 'this_is_a_test_password',
        'info': "I'm Johny Mnemonic, and I'm a recent college graduate with a Bachelor's Degree in Web Design. I'm seeking a full-time opportunity where I can employ my programming skills.",
        'contact_info': '128500'
    }


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def admin_client(admin_json, client, get_url):
    client.post(get_url('register'), json=admin_json)
    token_response = client.post(get_url('token'), json=admin_json)
    token = token_response.json()['access_token']
    client = Client()
    client.headers.update({'Authorization': f'Bearer {token}'})
    yield client
    admin_client_teardown(client, admin_json['email'], get_url)


@pytest.fixture
def test_gen_client(admin_client, digest_credentials, client, get_url):
    client.post(get_url('register'), json=digest_credentials)
    token_response = client.post(get_url('token'), json=digest_credentials)
    d_client = Client()
    d_client.headers.update({'Authorization': f'Bearer {token_response.json()["access_token"]}'})
    tags_generated = False
    while not tags_generated:
        response = d_client.get(get_url('me'))
        tags_generated = response.json()['settings']['tags']
        if not tags_generated:
            time.sleep(1)
    yield d_client
    admin_client.delete(get_url('delete', digest_credentials['email']))


def admin_client_teardown(client, email, get_url):
    client.delete(get_url('delete', email))


@pytest.fixture
def logs_to_check():
    return ('logs/db_accessor.log', 'logs/api_gateway.log', 'logs/user_manager.log')
