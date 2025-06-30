from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
from typing import List

from .. import crud, models
from ..database import get_database

router = APIRouter(
    prefix="/authors",
    tags=["Authors"],
)

@router.post("/", response_model=models.AuthorInDB, status_code=status.HTTP_201_CREATED)
def create_author(author: models.AuthorCreate, db: Database = Depends(get_database)):
    if crud.get_author_by_email(db, email=author.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Author with email '{author.email}' already exists."
        )
    created_author = crud.create_author(db, author=author)
    if created_author:
        return created_author
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create author.")

@router.get("/", response_model=List[models.AuthorInDB])
def get_all_authors(db: Database = Depends(get_database)):
    return crud.list_authors(db)

@router.get("/{author_id}", response_model=models.AuthorInDB)
def get_single_author(author_id: str, db: Database = Depends(get_database)):
    author = crud.get_author(db, author_id)
    if author:
        return author
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with ID '{author_id}' not found.")

@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_single_author(author_id: str, db: Database = Depends(get_database)):
    if not crud.delete_author(db, author_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with ID '{author_id}' not found.")
    return