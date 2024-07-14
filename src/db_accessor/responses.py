from http import HTTPStatus

from schema import DB_Accessor_Response, User, UserResponse

exists_response = DB_Accessor_Response(
    **{
        'result': 'error',
        'status_code': HTTPStatus.CONFLICT,
        'detail': 'This email already exists',
    }
).jsons


def user_deleted_response(email):
    return DB_Accessor_Response(
        **{
            'result': 'ok',
            'status_code': HTTPStatus.NO_CONTENT,
            'detail': 'User deleted',
        }
    ).jsons


def created_response(user: User) -> str:
    return DB_Accessor_Response(
        **{
            'result': 'ok',
            'status_code': HTTPStatus.CREATED,
            'detail': user.model_dump(),
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
            'detail': UserResponse.model_validate(user.model_dump()),
        }
    ).jsons


def user_time_updated_response(user: User) -> str:
    return DB_Accessor_Response(
        **{
            'result': 'ok',
            'status_code': HTTPStatus.OK,
            'detail': f'Latest time updated to {user.latest_news_processed}',
        }
    ).jsons


def hash_response(hash: str) -> str:
    return DB_Accessor_Response(
        **{
            'result': 'ok',
            'status_code': HTTPStatus.OK,
            'detail': hash,
        }
    ).jsons
