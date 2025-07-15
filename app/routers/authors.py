from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import List

from .. import crud, models
from ..database import get_database

router = APIRouter(
    prefix="/authors",
    tags=["Authors"],
)

@router.post("/", response_model=models.AuthorInDB, status_code=status.HTTP_201_CREATED)
async def create_author(author: models.AuthorCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    if await crud.get_author_by_email(db, email=author.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Author with email '{author.email}' already exists."
        )
    created_author_doc = await crud.create_author(db, author=author)
    if created_author_doc:
        # --- THIS IS THE FIX ---
        # Instead of returning the raw dictionary, we create an instance
        # of our Pydantic model. This forces the alias (_id -> id) to be applied.
        return models.AuthorInDB.model_validate(created_author_doc)
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create author.")

@router.get("/", response_model=List[models.AuthorInDB])
async def get_all_authors(db: AsyncIOMotorDatabase = Depends(get_database)):
    # This endpoint was likely correct, but it's good practice to ensure
    # every item is validated before returning.
    authors_list = await crud.list_authors(db)
    return [models.AuthorInDB.model_validate(author) for author in authors_list]

@router.get("/{author_id}", response_model=models.AuthorInDB)
async def get_single_author(author_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):  
    author = await crud.get_author(db, author_id)
    if author:
        return models.AuthorInDB.model_validate(author)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with ID '{author_id}' not found.")

@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_single_author(author_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    if not await crud.delete_author(db, author_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with ID '{author_id}' not found.")
    return