from contextlib import contextmanager
from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session


from fast_zero.app import app
from fast_zero.models import table_registry


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:')
    table_registry.metadata.create_all(engine)  # cria todas as tbls no bd de teste antes de cada teste

    with Session(engine) as session:
        yield session  # noqa: fornece uma instancia de Session que será injetada para cada teste. Essa sessão permite a interação com o bd de teste

    table_registry.metadata.drop_all(engine)  # apos o teste, dropa todas as tabelas criadas em teste
    engine.dispose()  # fecha sessões associadas ao engine

@contextmanager # gerenciador de contexto. Permite que criemos um "with"
def _mock_db_time(*,model,time=datetime(2026,1,1)):
    def fake_time_hook(mapper, connection,target):
        ''' funcao para mockar o created_at '''
        if hasattr(target, 'created_at'):
            target.created_at = time
    event.listen(model, 'before_insert', fake_time_hook)

    yield time # retorna o time na abertura do gerenciamento de contexto

    event.remove(model, 'before_insert', fake_time_hook) # remove após o g. de contexto finalizar

@pytest.fixture
def mock_db_time():
    return _mock_db_time