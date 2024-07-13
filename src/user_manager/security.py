import json
import logging
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def replace_password_with_hash_in_user_data(user_data: str) -> dict:
    data = dict(json.loads(user_data))
    logger.info(f'Generating password hash for {data["email"]}')
    pwd = data.pop('password')
    data['password'] = generate_hash(pwd)
    logger.info('Hash generated')
    return data


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def generate_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, config):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + config.expire_minutes
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.secret_key, algorithm=config.algorithm)
    logger.info(f'Token created good for {config.expire_minutes}.')
    return encoded_jwt
