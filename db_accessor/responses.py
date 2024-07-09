from schema import DB_Accessor_Response, User, UserWithEmail
from http import HTTPStatus


exists_response = DB_Accessor_Response(
    **{
        'result': 'error',
        'status_code': HTTPStatus.CONFLICT,
        'detail': 'This email already exists',
    }
).jsons

user_deleted_response = DB_Accessor_Response(
    **{
        'result': 'ok',
        'status_code': HTTPStatus.NO_CONTENT,
        'detail': '',
    }
).jsons


def created_response(user: UserWithEmail) -> str:
    return DB_Accessor_Response(
        **{
            'result': 'ok',
            'status_code': HTTPStatus.CREATED,
            'detail': f'User {user.email} created',
        }
    ).jsons


def exception_response(exception: str) -> str:
    return DB_Accessor_Response(
        **{
            'result': 'error',
            'status_code': HTTPStatus.CREATED,
            'detail': exception,
        }
    ).jsons


def user_not_found(email: str) -> str:
    return DB_Accessor_Response(
        **{
            'result': 'error',
            'status_code': HTTPStatus.NOT_FOUND,
            'detail': f'User {email} not found',
        }
    ).jsons


def user_info_response(user: User) -> str:
    return DB_Accessor_Response(
        **{
            'result': 'ok',
            'status_code': HTTPStatus.OK,
            'detail': user,
        }
    ).jsons
