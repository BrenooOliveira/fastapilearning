from jwt import decode

from fast_zero.security import SECRET_KEY, create_access_token


def test_jwt():
    data = {'test': 'test'}  # dados que serão assinados pelo JWT
    token = create_access_token(data)  # encodamos o token

    decoded = decode(token, SECRET_KEY, algorithms=['HS256'])

    assert decoded['test'] == data['test']
    assert 'exp' in decoded
