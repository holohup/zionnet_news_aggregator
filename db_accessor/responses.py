from schema import DB_Accessor_Response
from http import HTTPStatus


exists_response = DB_Accessor_Response(
    **{
        'result': 'error',
        'status_code': HTTPStatus.CONFLICT,
        'detail': 'This email already exists',
    }
)

user_deleted_response = DB_Accessor_Response(
    **{
        'result': 'ok',
        'status_code': HTTPStatus.NO_CONTENT,
        'detail': '',
    }
)


def created_response(user_info) -> DB_Accessor_Response:
    return DB_Accessor_Response(
        **{
            'result': 'ok',
            'status_code': HTTPStatus.CREATED,
            'detail': f'User {user_info["email"]} created',
        }
    )


def exception_response(exception: str) -> DB_Accessor_Response:
    return DB_Accessor_Response(
        **{
            'result': 'error',
            'status_code': HTTPStatus.CREATED,
            'detail': exception,
        }
    )


def user_not_found(email: str) -> DB_Accessor_Response:
    return DB_Accessor_Response(
        **{
            'result': 'error',
            'status_code': HTTPStatus.NOT_FOUND,
            'detail': f'User {email} not found',
        }
    )
