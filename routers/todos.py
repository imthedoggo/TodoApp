from fastapi import FastAPI, APIRouter, Depends, HTTPException, Path
from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from models import Todos
from database import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description:str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()


@router.get("/todo/{id}", status_code=status.HTTP_200_OK)
async def read_task(db: db_dependency, id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='todo not found!')


@router.post("/todo}", status_code=status.HTTP_201_CREATED)
async def create_task(db: db_dependency, request: TodoRequest):
    todo_model = Todos(**request.dict())

    db.add(todo_model)
    db.commit()


@router.put("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_task(db: db_dependency,
                      request: TodoRequest,
                      id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='todo not found!')
    todo_model.title = request.title
    todo_model.description = request.description
    todo_model.priority = request.priority
    todo_model.complete = request.complete

    db.add(todo_model)
    db.commit()


@router.delete("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(db: db_dependency, id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='todo not found!')

    db.query(Todos).filter(Todos.id == id).first().delete()
    db.commit()
