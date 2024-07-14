import time
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
def admin_client(admin_json, client):
    client.post(user_endpoint_url('register'), json=admin_json)
    token_response = client.post(user_endpoint_url('token'), json=admin_json)
    token = token_response.json()['access_token']
    client = Client()
    client.headers.update({'Authorization': f'Bearer {token}'})
    yield client
    admin_client_teardown(client, admin_json['email'])


@pytest.fixture
def test_gen_client(admin_client, digest_credentials, client):
    client.post(user_endpoint_url('register'), json=digest_credentials)
    token_response = client.post(user_endpoint_url('token'), json=digest_credentials)
    d_client = Client()
    d_client.headers.update({'Authorization': f'Bearer {token_response.json()["access_token"]}'})
    tags_generated = False
    while not tags_generated:
        response = d_client.get(user_endpoint_url('me'))
        tags_generated = response.json()['settings']['tags']
        if not tags_generated:
            time.sleep(1)
    yield d_client
    admin_client.delete(user_endpoint_url('delete', digest_credentials['email']))


def admin_client_teardown(client, email):
    client.delete(user_endpoint_url('delete', email))
