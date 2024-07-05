from schema import DB_Accessor_Response
from http import HTTPStatus


exists_response = DB_Accessor_Response(
    **{
        'result': 'error',
        'status_code': HTTPStatus.CONFLICT,
        'detail': 'This email already exists',
    }
)


def created_response(user_info):
    return DB_Accessor_Response(
        **{
            'result': 'ok',
            'status_code': HTTPStatus.CREATED,
            'detail': f'User {user_info["email"]} created',
        }
    )


def exception_response(exception: str):
    return DB_Accessor_Response(
        **{
            'result': 'error',
            'status_code': HTTPStatus.CREATED,
            'detail': exception,
        }
    )