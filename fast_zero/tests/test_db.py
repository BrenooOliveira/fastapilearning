from dataclasses import asdict

from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:  # inica o g. de contexto
        new_user = User(username='john', password='secret', email='test@test')
        session.add(new_user)
        session.commit()

    user = session.scalar(select(User).where(User.username == 'john'))

    assert asdict(user) == {
        'id': 1,
        'username': 'john',
        'password': 'secret',
        'email': 'test@test',
        'created_at': time,  # usa o time gerado
        'updated_at': time,
    }
    """
    Isso faz com que durante o commit,
    quando os objetos são persistidos da sessão para o banco de dados,
    o evento de before_insert seja executado para cada objeto do modelo passado em mock_db_time(model=*MODEL*)
    """
