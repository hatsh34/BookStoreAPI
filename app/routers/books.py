from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List

from .. import crud, models
from ..database import get_database

router = APIRouter(
    prefix="/books",
    tags=["Books"],
)

@router.post("/by-author/{author_id}", response_model=models.BookWithAuthor, status_code=status.HTTP_201_CREATED)
async def create_book_for_author(author_id: str, book: models.BookCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    # First, check if the author exists
    author = await crud.get_author(db, author_id)
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with ID '{author_id}' not found.")

    # Now, create the book
    created_book = await crud.create_book(db, author_id, book)
    if created_book:
        # Combine the created book data with the author data for the response
        return models.BookWithAuthor.model_validate({**created_book, "author": author})
    
    raise HTTPException(status_code=500, detail="Failed to create book.")

# --- FIXED ENDPOINT ---
@router.get("/", response_model=List[models.BookWithAuthor])
async def get_all_books(db: AsyncIOMotorDatabase = Depends(get_database)):
    all_books_data = []
    # Use the new crud function to get all books
    books_cursor = await crud.list_all_books(db)
    for book in books_cursor:
        author = await crud.get_author(db, book["author_id"])
        if author:
            # Combine book and author data for the response model
            all_books_data.append(models.BookWithAuthor.model_validate({**book, "author": author}))
    return all_books_data

# --- NEW ENDPOINT ---
@router.get("/{book_id}", response_model=models.BookWithAuthor)
async def get_single_book(book_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Retrieves a single book by its ID."""
    book = await crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID '{book_id}' not found.")
    
    author = await crud.get_author(db, book["author_id"])
    if not author:
        # This is a data integrity issue, but we should handle it gracefully.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author for book with ID '{book['author_id']}' not found.")

    return models.BookWithAuthor.model_validate({**book, "author": author})

@router.get("/by-author/{author_id}", response_model=List[models.BookWithAuthor])
async def get_books_by_author_id(author_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    author = await crud.get_author(db, author_id)
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with ID '{author_id}' not found.")

    books = await crud.list_books_by_author(db, author_id)
    # Combine each book with the author's data for the response
    return [models.BookWithAuthor.model_validate({**book, "author": author}) for book in books]