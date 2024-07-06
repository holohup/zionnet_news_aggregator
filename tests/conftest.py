from httpx import Client
import pytest
import json


@pytest.fixture
def anonymous_client():
    return Client()


@pytest.fixture
def test_user_email():
    return 'testtest@testTESTtest.com'


@pytest.fixture
def test_user_data(test_user_email):
    return json.dumps({
        'email': test_user_email,
        'password': 'ThisIsATestPassword'
    })
