from fastapi import status, HTTPException


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def server_error_dict():
    return {
        'result': 'error',
        'status_code': 500,
        'detail': 'Internal server error, check API Gateway logs',
    }


def http_exception(result):
    return HTTPException(status_code=result['status_code'], detail=result['detail'])
