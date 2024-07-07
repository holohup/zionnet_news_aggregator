import json
import logging

from passlib.context import CryptContext


logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def generate_user_data_with_hashed_password(user_data: str):
    data = dict(json.loads(user_data))
    logger.info(f'Generating password hash for {data["email"]}')
    pwd = data.pop('password')
    data['password'] = generate_hash(pwd)
    logger.info('Hash generated')
    return json.dumps(data)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def generate_hash(password):
    return pwd_context.hash(password)