import json

server_error = json.dumps(
    {
        'result': 'error',
        'status_code': 500,
        'detail': 'Internal server error, check UserManager logs',
    }
)

hash_error = json.dumps(
    {'result': 'error', 'status_code': 500, 'detail': 'Could not fetch password hash'}
)

credentials_error = json.dumps(
    {'result': 'error', 'status_code': 401, 'detail': 'Incorrect username or password'}
)


def token_response(token, token_type):
    return json.dumps(
        {
            'result': 'ok',
            'status_code': 200,
            'detail': {'access_token': token, 'token_type': token_type},
        }
    )
