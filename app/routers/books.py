from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
from typing import List

from .. import crud, models
from ..database import get_database

router = APIRouter(
    prefix="/books",
    tags=["Books"],
)

@router.post("/by-author/{author_id}", response_model=models.BookWithAuthor, status_code=status.HTTP_201_CREATED)
def create_book_for_author(author_id: str, book: models.BookCreate, db: Database = Depends(get_database)):
    author = crud.get_author(db, author_id)
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with ID '{author_id}' not found.")

    created_book = crud.create_book(db, author_id, book)
    if created_book:
        return models.BookWithAuthor.model_validate({**created_book, "author": author})
    raise HTTPException(status_code=500, detail="Failed to create book.")

@router.get("/", response_model=List[models.BookWithAuthor])
def get_all_books(db: Database = Depends(get_database)):
    all_books_data = []
    books = crud.list_all_books(db)
    for book in books:
        author = crud.get_author(db, book["author_id"])
        if author:
            all_books_data.append(models.BookWithAuthor.model_validate({**book, "author": author}))
    return all_books_data

@router.get("/by-author/{author_id}", response_model=List[models.BookWithAuthor])
def get_books_by_author_id(author_id: str, db: Database = Depends(get_database)):
    author = crud.get_author(db, author_id)
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with ID '{author_id}' not found.")

    books = crud.get_books_by_author(db, author_id)
    return [models.BookWithAuthor.model_validate({**book, "author": author}) for book in books]
