import os
import sys
from types import MethodType
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

CURRENT_DIR = os.path.dirname(__file__)
APP_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from main import app
from models.database import Base, get_db
Base.metadata.clear()
from models import user as user_models
from services.ai.ollama_client import ollama_client
from backend.app.models.user import User

TEST_DB_PATH = os.path.abspath(os.path.join(APP_DIR, "test_ecritoire.db"))
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

# Creating a dedicated test session
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def fake_auth():
    return User(id=1, email="test@example.com", hashed_password="fake", is_active=True)

def override_get_db():
    #FastAPI dependency override to use the test DB session.
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session", autouse=True)
def override_auth():
    from backend.app.controllers import samples, generation
    app.dependency_overrides[samples.get_current_user] = fake_auth
    app.dependency_overrides[generation.get_current_user] = fake_auth
    yield
    app.dependency_overrides.clear()

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Fresh DB file each session
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    Base.metadata.create_all(bind=engine)
    yield
    try:
        # Cleanup after the entire session
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
    except PermissionError:
        pass

@pytest.fixture(scope="session", autouse=True)
def override_dependencies():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def mock_ollama_for_all_tests():
    # ollama mock test
    original_generate_text = ollama_client.generate_text

    def fake_generate_text(self, prompt, model="llama2:7b-chat", max_tokens=200, temperature=0.7):
        return "MOCK_GENERATION_FROM_OLLAMA"

    ollama_client.generate_text = MethodType(fake_generate_text, ollama_client)
    yield
    ollama_client.generate_text = original_generate_text

@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client():
    # FastAPI test client
    with TestClient(app) as c:
        yield c

@pytest.fixture
def create_user(db_session):
    def _create_user(email="test@example.com", password_hash="hashed", active=True):
        user = user_models.User(
            email=email, hashed_password=password_hash, is_active=active
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    return _create_user