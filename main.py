"""
Main application module for the FastAPI application.

This module initializes the FastAPI application, sets up routes,
configures the database, and provides dependency injection for database access.
"""

from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from passlib.context import CryptContext
from jose import JWTError, jwt
# pylint: disable=no-name-in-module
from pydantic import BaseModel

# Constants
SECRET_KEY = "xjkqsbxkhjqbcjckxcjsqbhkjchqshkbcjqbjckjbkjnkjbx,whkbw,nxbxvhn"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    """
    Hash the password using bcrypt.
    Args:
        password (str): The password to hash.
    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    """
    Verify the hashed password .
    """
    return pwd_context.verify(plain_password, hashed_password)


# JWT Token utility
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    The function to create an access token .
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# OAuth2PasswordBearer to extract token from request headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency to get current user from JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc
    return username


# pylint: disable=too-few-public-methods
class User(Base):
    """
    Represents a user in the system.
    Attributes:
        id (int): The user ID.
        username (str): The user's username.
        hashed_password (str): The hashed password for the user.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)


# pylint: disable=too-few-public-methods
class TodoInDB(Base):
    """
    Represents a task todo in the system.
    Attributes:
        id (int): The todo ID.
        task (str): The task .
        owner_id (int): The user who owns the task.
    """
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    task = Column(String)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User")


# pylint: disable=too-few-public-methods
class TodoBase(BaseModel):
    """
    Represents a todo base model.
    """
    task: str
    completed: bool = False


# pylint: disable=too-few-public-methods
class TodoCreate(TodoBase):
    """
    Represents a todo model.
    """


# pylint: disable=too-few-public-methods
class TodoUpdate(BaseModel):
    """
    Represents a todo model.
    """
    task: Optional[str] = None
    completed: Optional[bool] = None


# pylint: disable=too-few-public-methods
class TodoResponse(TodoBase):
    """
    Represents a todo model.
    """
    id: int

    class Config:
        """
        The Config class.
        """
        orm_mode = True


# pylint: disable=too-few-public-methods
class UserCreate(BaseModel):
    """
    Represents a user model.
    """
    username: str
    password: str


# pylint: disable=too-few-public-methods
class Token(BaseModel):
    """
    Represents a token model.
    """
    access_token: str
    token_type: str


# Database setup
engine = create_engine("sqlite:///todos.db")
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# pylint: disable=too-few-public-methods
def get_db():
    """
    The database session factory method.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# FastAPI instance
app = FastAPI()


# Routes
@app.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    The registration method for registering a new user.
    :param user:
    :param db:
    :return:JWT-Token
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/login", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    """
    The login method for login.
    :param user:
    :param db:
    :return: JWT-Token
    """
    db_user = (db.query(User)
               .filter(User.username == user.username)
               .first())
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400,
                            detail="Invalid username or password")
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/todos", response_model=List[TodoResponse])
def get_todos(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    """
    The todos method for getting todos.
    :param db:
    :param current_user:
    :return: list of todos
    """
    user = (db.query(User)
            .filter(User.username == current_user)
            .first())
    todos = db.query(TodoInDB).filter(TodoInDB.owner_id == user.id).all()
    return todos


@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo_by_id(todo_id: int, db: Session = Depends(get_db),
                   current_user: str = Depends(get_current_user)):
    """
    The todos method for getting todos by id.
    :param todo_id:
    :param db:
    :param current_user:
    :return: a todo
    """
    # Get the current user from the database
    user = db.query(User).filter(User.username == current_user).first()

    # Query for the specific Todo item based on todo_id and owner_id (current user)
    db_todo = (db.query(TodoInDB)
               .filter(TodoInDB.id == todo_id, TodoInDB.owner_id == user.id)
               .first())

    # If the Todo doesn't exist, raise a 404 error
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    return db_todo


@app.post("/todos", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db),
                current_user: str = Depends(get_current_user)):
    """
    The todos method for creating todos.
    :param todo:
    :param db:
    :param current_user:
    :return: The created todo
    """
    user = (db.query(User)
            .filter(User.username == current_user)
            .first())
    db_todo = TodoInDB(**todo.dict(), owner_id=user.id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db),
                current_user: str = Depends(get_current_user)):
    """
    The todos method for updating todos.
    :param todo_id:
    :param todo:
    :param db:
    :param current_user:
    :return: The updated todo
    """
    user = (db.query(User)
            .filter(User.username == current_user)
            .first())
    db_todo = (db.query(TodoInDB)
               .filter(TodoInDB.id == todo_id, TodoInDB.owner_id == user.id)
               .first())
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo.task is not None:
        db_todo.task = todo.task
    if todo.completed is not None:
        db_todo.completed = todo.completed
    db.commit()
    db.refresh(db_todo)
    return db_todo


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: Session = Depends(get_db),
                current_user: str = Depends(get_current_user)):
    """
    The todos method for deleting todos.
    :param todo_id:
    :param db:
    :param current_user:
    :return: Deletion message
    """
    user = (db.query(User)
            .filter(User.username == current_user)
            .first())
    db_todo = (db.query(TodoInDB)
               .filter(TodoInDB.id == todo_id, TodoInDB.owner_id == user.id)
               .first())
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(db_todo)
    db.commit()
    return {"message": "Todo deleted successfully"}


@app.patch("/todos/{todo_id}/complete", response_model=TodoResponse)
def mark_todo_as_complete(todo_id: int, db: Session = Depends(get_db),
                          current_user: str = Depends(get_current_user)):
    """
    The todos method for marking a todo as completed.
    :param todo_id:
    :param db:
    :param current_user:
    :return:
    """
    user = (db.query(User)
            .filter(User.username == current_user)
            .first())
    db_todo = (db.query(TodoInDB)
               .filter(TodoInDB.id == todo_id, TodoInDB.owner_id == user.id)
               .first())
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db_todo.completed = True
    db.commit()
    db.refresh(db_todo)
    return db_todo


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
