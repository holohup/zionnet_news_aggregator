host = 'http://127.0.0.1:8000'
endpoints = {
    'register': '/register',
    'delete': '/delete'
}


def endpoint_url(name: str, email: str = None) -> str:
    """Provide endpoints for tests."""

    result = host + endpoints[name]
    if email:
        result += '/' + email
    return result
