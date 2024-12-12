import pytest
import uuid
from fastapi.testclient import TestClient
from main import app, Base, engine, SessionLocal, User, TodoInDB
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


# Create a test client
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# Set up a temporary SQLite database for tests
@pytest.fixture(scope="function")
def db_session():
    # Set up the database and tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    # Cleanup after test
    db.close()
    Base.metadata.drop_all(bind=engine)


# Fixture to generate a unique username for each test
@pytest.fixture
def unique_username():
    return f"testuser_{uuid.uuid4()}"


# Test user registration
def test_register(client, db_session, unique_username):
    response = client.post("/register", json={"username": unique_username, "password": "password"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


# Test user login
def test_login(client, db_session, unique_username):
    # Register a new user
    client.post("/register", json={"username": unique_username, "password": "password"})

    # Login with the same user
    response = client.post("/login", json={"username": unique_username, "password": "password"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


# Test to get todos for a logged-in user
def test_get_todos(client, db_session, unique_username):
    # Register and login the user
    client.post("/register", json={"username": unique_username, "password": "password"})
    login_response = client.post("/login", json={"username": unique_username, "password": "password"})
    token = login_response.json()["access_token"]

    # Create a new todo for the user
    client.post("/todos", json={"task": "Test Todo 1", "completed": False},
                headers={"Authorization": f"Bearer {token}"})

    # Get todos for the user
    response = client.get("/todos", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["task"] == "Test Todo 1"


# Test to create a new todo
def test_create_todo(client, db_session, unique_username):
    # Register and login the user
    client.post("/register", json={"username": unique_username, "password": "password"})
    login_response = client.post("/login", json={"username": unique_username, "password": "password"})
    token = login_response.json()["access_token"]

    # Create a new todo
    response = client.post("/todos", json={"task": "Test Todo 1", "completed": False},
                           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["task"] == "Test Todo 1"
    assert response.json()["completed"] is False


# Test to update a todo
def test_update_todo(client, db_session, unique_username):
    # Register and login the user
    client.post("/register", json={"username": unique_username, "password": "password"})
    login_response = client.post("/login", json={"username": unique_username, "password": "password"})
    token = login_response.json()["access_token"]

    # Create a new todo
    create_response = client.post("/todos", json={"task": "Test Todo 1", "completed": False},
                                  headers={"Authorization": f"Bearer {token}"})
    todo_id = create_response.json()["id"]

    # Update the todo
    response = client.put(f"/todos/{todo_id}", json={"task": "Updated Todo", "completed": True},
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["task"] == "Updated Todo"
    assert response.json()["completed"] is True


# Test to delete a todo
def test_delete_todo(client, db_session, unique_username):
    # Register and login the user
    client.post("/register", json={"username": unique_username, "password": "password"})
    login_response = client.post("/login", json={"username": unique_username, "password": "password"})
    token = login_response.json()["access_token"]

    # Create a new todo
    create_response = client.post("/todos", json={"task": "Test Todo 1", "completed": False},
                                  headers={"Authorization": f"Bearer {token}"})
    todo_id = create_response.json()["id"]

    # Delete the todo
    response = client.delete(f"/todos/{todo_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204


# Test to mark a todo as complete
def test_mark_todo_complete(client, db_session, unique_username):
    # Register and login the user
    client.post("/register", json={"username": unique_username, "password": "password"})
    login_response = client.post("/login", json={"username": unique_username, "password": "password"})
    token = login_response.json()["access_token"]

    # Create a new todo
    create_response = client.post("/todos", json={"task": "Test Todo 1", "completed": False},
                                  headers={"Authorization": f"Bearer {token}"})
    todo_id = create_response.json()["id"]

    # Mark the todo as complete
    response = client.patch(f"/todos/{todo_id}/complete", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["completed"] is True
