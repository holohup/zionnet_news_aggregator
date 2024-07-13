import pytest
from httpx import Client
from setup import user_endpoint_url


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
def client():
    return Client()


@pytest.fixture
def admin_client(admin_json, client):
    client.post(user_endpoint_url('register'), json=admin_json)
    token_response = client.post(user_endpoint_url('token'), json=admin_json)
    token = token_response.json()['access_token']
    client = Client()
    client.headers.update({'Authorization': f'Bearer {token}'})
    yield client
    admin_client_teardown(client, admin_json['email'])


def admin_client_teardown(client, email):
    client.delete(user_endpoint_url('delete', email))
