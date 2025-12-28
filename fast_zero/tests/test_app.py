from http import HTTPStatus


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
    assert response.json() == {
        'users': [
            {
                'username': 'john',
                'email': 'john.doe@example.com',
                'id': 1,
            }
        ]
    }


def test_update_user(client):
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
