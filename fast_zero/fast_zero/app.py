from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, Token, UserList, UserPublic, UserSchema
from fast_zero.security import create_access_token, get_password_hash, verify_password

app = FastAPI()

# database "falso" para mockar os dados
database = []


@app.post('/token', response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    """
    Recebe dados através do form_data e tenta recuperar um usuario através do email
    :params:
        - form_data: OAuth2PasswordRequestForm -> classe especial do fastAPI resp por solicitar o user/senha
    :return:
        - JWT e o tipo dele
    """
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Incorrect email or password')
    access_token = create_access_token(data={'sub': user.email})

    return {'access_token': access_token, 'token_type': 'bearer'}


# Response Model: modelo que o pydantic irá validar com base no
# retorno do endpoint
@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá Mundo!'}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    # procurando usuario antes de cria-lo
    db_user = session.scalar(select(User).where((User.username == user.username) | (User.email == user.email)))

    if db_user:
        # validando o que já existe no DB
        if db_user.username == user.username:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Username already exists')
        elif db_user.email == user.email:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Email already exists')

    hashed_password = get_password_hash(user.password)

    db_user = User(username=user.username, password=hashed_password, email=user.email)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/users/', response_model=UserList)
def read_users(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {'users': users}


@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(user_id: int, user: UserSchema, session: Session = Depends(get_session)):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')

    try:
        db_user.username = user.username
        db_user.password = get_password_hash(user.password)
        db_user.email = user.email

        session.commit()
        session.refresh(db_user)

        return db_user

    # possível problema: att um user com dados duplicados no BD
    except IntegrityError:  # noqa: esse erro eh levantado caso o .commit não consiga efetuar a persistencia
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Username or Email already exists')


@app.delete('/users/{user_id}', response_model=Message)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')

    session.delete(db_user)
    session.commit()

    return {'message': 'User deleted'}
