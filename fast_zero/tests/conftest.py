from asyncio.sslproto import add_flowcontrol_defaults
from contextlib import contextmanager
from datetime import datetime

import pytest_asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry
from fast_zero.security import get_password_hash


@pytest.fixture
def client(session):
    def get_session_override():
        # retornamos nossa fixture de session definida
        return session

    with TestClient(app) as client:
        # substitui a get_session que usamos na aplcação pela nossa session de teste
        app.dependency_overrides[get_session] = get_session_override
        yield client

    # limpa o override que fizemos para o app não usar a fixture de session
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    """
    class notes:
    No ambiente de testes do FastAPI,
    a aplicação e os testes podem rodar em threads diferentes.
    Isso pode levar a um erro com o SQLite, pois os objetos SQLite
    criados em uma thread só podem ser usados na mesma thread.
    """

    # session utilizada para os testes
    # difere da session do app
    engine = create_async_engine('sqlite+aiosqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool) # cria um engine async

    async with engine.begin() as conn: # com o begin() estamos criando uma transacao ao sqlalchemy
            # espera até que uma execução sync seja feita
        await conn.run_sync(table_registry.metadata.create_all) # cria todas as tbls no bd de teste antes de cada teste

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session  # noqa: fornece uma instancia de Session que será injetada para cada teste. Essa sessão permite a interação com o bd de teste

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all) # apos o teste, dropa todas as tabelas criadas em teste
        await engine.dispose()


@contextmanager  # gerenciador de contexto. Permite que criemos um "with"
def _mock_db_time(*, model, time=datetime(2026, 1, 1)):
    def fake_time_handler(mapper, connection, target):
        """funcao para mockar o created_at"""
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_handler)

    yield time  # retorna o time na abertura do gerenciamento de contexto

    event.remove(model, 'before_insert', fake_time_handler)  # remove após o g. de contexto finalizar


@pytest.fixture
def mock_db_time():
    return _mock_db_time


# fixture para criação de registro no BD de teste
@pytest.fixture
def user(session):

    user_password = 'secretest'
    user = User(username='Teste', email='teste@teste.com', password=get_password_hash(user_password))
    session.add(user)

    session.commit()
    session.refresh(user)

    # monkey patch -> modificamos/estendemos o codigo em tempo de execução
    user.clean_password = user_password

    return user


@pytest.fixture
def token(client, user):
    response = client.post('auth/token', data={'username': user.email, 'password': user.clean_password})
    return response.json()['access_token']
