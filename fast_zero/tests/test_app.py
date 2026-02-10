from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_get_token(client, user):
    response = client.post('/token', data={'username': user.email, 'password': user.clean_password})

    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo!'}


def test_create_user(client):

    # act
    response = client.post(
        url='/users/',
        json={
            'username': 'john',
            'email': 'john.doe@example.com',
            'password': 'secret',
        },
    )

    # assert
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'john',
        'email': 'john.doe@example.com',
        'id': 1,
    }


def test_read_users(client):
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user):
    response = client.put(
        '/users/1',
        # recebe user schema
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'newsecret',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        # retorna user public
        'username': 'bob',
        'email': 'bob@example.com',
        'id': 1,
    }


def test_update_integrity_error(client, user):
    """
    - potencial erro: usuario ser criado e entao
        alterar nome/email para um registro já existente
    """
    # criando user 'fausto'
    client.post('/users/', json={'username': 'fausto', 'email': 'fausto@example.com', 'password': 'secret'})

    # alterando o username que demos update na "test_update_user" para fausto
    # forçando conflito do BD unique
    response_update = client.put(
        f'/users/{user.id}', json={'username': 'fausto', 'email': 'bob@example.com', 'password': 'newsecret'}
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {'detail': 'Username or Email already exists'}


def test_delete_user(client, user):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}
