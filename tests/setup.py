host = 'http://127.0.0.1:8000'
endpoints = {
    'register': '/user/register',
    'delete': '/user/delete',
    'get': '/user/info',
    'token': '/token'
}

logs_to_check = ('logs/db_accessor.log', 'logs/api_gateway.log', 'logs/user_manager.log')


def user_endpoint_url(name: str, email: str = None) -> str:
    """Provide endpoints for tests."""

    result = host + endpoints[name]
    if email:
        result += '/' + email
    return result
