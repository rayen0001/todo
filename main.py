from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional, List

# Constants
SECRET_KEY = "xjkqsbxkhjqbcjckxcjsqbhkjchqshkbcjqbjckjbkjnkjbx,whkbw,nxbxvhn"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# JWT Token utility
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# OAuth2PasswordBearer to extract token from request headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency to get current user from JWT token
def get_current_user(token: str = Depends(oauth2_scheme)):
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
    except JWTError:
        raise credentials_exception
    return username

# SQLAlchemy models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class TodoInDB(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    task = Column(String)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User")

# Pydantic models
class TodoBase(BaseModel):
    task: str
    completed: bool = False

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    task: Optional[str] = None
    completed: Optional[bool] = None

class TodoResponse(TodoBase):
    id: int

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Database setup
engine = create_engine("sqlite:///todos.db")
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
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
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = (db.query(User)
               .filter(User.username == user.username)
               .first())
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400,
                            detail="Invalid username or password")
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/todos", response_model=List[TodoResponse])
def get_todos(db: Session = Depends(get_db),
              current_user: str = Depends(get_current_user)):
    user = (db.query(User)
            .filter(User.username == current_user)
            .first())
    todos = db.query(TodoInDB).filter(TodoInDB.owner_id == user.id).all()
    return todos


@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo_by_id(todo_id: int, db: Session = Depends(get_db),
                   current_user: str = Depends(get_current_user)):
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
    user = (db.query(User)
            .filter(User.username == current_user).first())
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
    user = db.query(User).filter(User.username == current_user).first()
    db_todo = db.query(TodoInDB).filter(TodoInDB.id == todo_id,
                                        TodoInDB.owner_id == user.id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(db_todo)
    db.commit()
    return {"message": "Todo deleted successfully"}

@app.patch("/todos/{todo_id}/complete", response_model=TodoResponse)
def mark_todo_as_complete(todo_id: int, db: Session = Depends(get_db),
                          current_user: str = Depends(get_current_user)):
    user = db.query(User).filter(User.username == current_user).first()
    db_todo = (db.query(TodoInDB)
               .filter(TodoInDB.id == todo_id,TodoInDB.owner_id == user.id)
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
