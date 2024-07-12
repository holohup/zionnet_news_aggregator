from fastapi import status, HTTPException


credentials_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)  # JWT Token invalid


token_expired_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token expired",
    headers={"WWW-Authenticate": "Bearer"},
)  # JWT Token expired


admin_only_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="This content requires an administrator account"
)  # JWT Token expired

server_error = {
    'result': 'error',
    'status_code': 500,
    'detail': 'Internal server error, check API Gateway logs',
}  # An error if Dapr is not functioning properly.


def http_exception(result):
    """Exception that occured in other modules."""

    return HTTPException(status_code=result['status_code'], detail=result['detail'])
