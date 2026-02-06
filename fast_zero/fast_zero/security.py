from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from jwt import encode
from pwdlib import PasswordHash

SECRET_KEY = 'your-secret-key'  # Isso é provisório, vamos ajustar!
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = PasswordHash.recommended()  # argon2 como algoritmo padrão


def create_access_token(data: dict):
    """
    Forma um payload do JWT e então codifica as infos em um JWT que é retornado
    :param data: Dicionario de dados do usuario
    :type data: dict

    :return: bb
    :type return: aa
    """

    to_enconde = data.copy()  # aquilo que queremos encondar

    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_enconde.update({'exp': expire})

    encoded_jwt = encode(to_enconde, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def get_password_hash(password: str):
    return pwd_context.hash(password)


# noqa: autenticação de uma via só: assim, as senhas sempre vão para o servidor e não retornam dele isso cria uma camada de verificação e não exposição de senhas
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
