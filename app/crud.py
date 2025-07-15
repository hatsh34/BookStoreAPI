
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from . import models

# --- Author CRUD Functions ---
async def create_author(db: AsyncIOMotorDatabase, author: models.AuthorCreate):
    author_dict = author.model_dump()  # Converts the Pydantic model to a dictionary to store in MongoDB.
    result = await db.authors.insert_one(author_dict)
    return await db.authors.find_one({"_id": result.inserted_id})  # Returns the newly created document by finding its insertedID 

async def get_author_by_email(db: AsyncIOMotorDatabase, email: str):
    return await db.authors.find_one({"email": email})

async def get_author(db: AsyncIOMotorDatabase, author_id: str):
    try:
        obj_id = ObjectId(author_id)
        return await db.authors.find_one({"_id": obj_id})
    except Exception:
        return None

async def list_authors(db: AsyncIOMotorDatabase):
    # .find() returns a cursor, which we must iterate over asynchronously
    return await db.authors.find().to_list(length=100)

async def delete_author(db: AsyncIOMotorDatabase, author_id: str):
    try:
        obj_id = ObjectId(author_id)
        # Delete the author
        delete_result = await db.authors.delete_one({"_id": obj_id})
        if delete_result.deleted_count > 0:
            # Also delete all books by this author
            await db.books.delete_many({"author_id": author_id})
            return True
        return False
    except Exception:
        return False

# --- Book CRUD Functions ---

async def create_book(db: AsyncIOMotorDatabase, author_id: str, book: models.BookCreate):
    book_dict = book.model_dump()
    book_dict["author_id"] = author_id
    result = await db.books.insert_one(book_dict)
    return await db.books.find_one({"_id": result.inserted_id})

async def get_book(db: AsyncIOMotorDatabase, book_id: str):
    try:
        obj_id = ObjectId(book_id)
        return await db.books.find_one({"_id": obj_id})
    except Exception:
        return None

async def list_books_by_author(db: AsyncIOMotorDatabase, author_id: str):
    return await db.books.find({"author_id": author_id}).to_list(length=100)


async def list_all_books(db: AsyncIOMotorDatabase):
    """Lists all books in the database."""
    return await db.books.find().to_list(length=100)
