import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db, Base, User, TodoInDB

# Setup the test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_todos.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Dependency override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def test_user():
    user_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    return user_data

def test_register(test_user):
    response = client.post("/register", json=test_user)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login(test_user):
    response = client.post("/login", json=test_user)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_create_todo(test_user):
    # First, register and login to get the token
    # client.post("/register", json=test_user)
    login_response = client.post("/login", json=test_user)
    access_token = login_response.json()["access_token"]

    # Create a todo
    todo_data = {"task": "Test Todo"}
    response = client.post("/todos", json=todo_data, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["task"] == "Test Todo"

def test_get_todos(test_user):
    # First, register and login to get the token
    # client.post("/register", json=test_user)
    login_response = client.post("/login", json=test_user)
    access_token = login_response.json()["access_token"]

    # Get todos
    response = client.get("/todos", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_todo(test_user):
    # First, register and login to get the token
    # client.post("/register", json=test_user)
    login_response = client.post("/login", json=test_user)
    access_token = login_response.json()["access_token"]

    # Create a todo
    todo_data = {"task": "Test Todo"}
    create_response = client.post("/todos", json=todo_data, headers={"Authorization": f"Bearer {access_token}"})
    todo_id = create_response.json()["id"]

    # Update the todo
    update_data = {"task": "Updated Todo", "completed": True}
    response = client.put(f"/todos/{todo_id}", json=update_data, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["task"] == "Updated Todo"
    assert response.json()["completed"] is True

def test_delete_todo(test_user):
    # First, register and login to get the token
    # client.post("/register", json=test_user)
    login_response = client.post("/login", json=test_user)
    access_token = login_response.json()["access_token"]

    # Create a todo
    todo_data = {"task": "Test Todo"}
    create_response = client.post("/todos", json=todo_data, headers={"Authorization": f"Bearer {access_token}"})
    todo_id = create_response.json()["id"]

    # Delete the todo
    response = client.delete(f"/todos/{todo_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 204

    # Verify the todo is deleted
    response = client.get(f"/todos/{todo_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 404

if __name__ == "__main__":
    pytest.main()