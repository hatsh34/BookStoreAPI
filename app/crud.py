from pymongo.database import Database
from bson import ObjectId
from . import models

#Author CRUD Functions

def create_author(db: Database, author: models.AuthorCreate):
    author_dict = author.model_dump()
    result = db.authors.insert_one(author_dict)
    return db.authors.find_one({"_id": result.inserted_id})

def get_author_by_email(db: Database, email: str):
    return db.authors.find_one({"email": email})

def get_author(db: Database, author_id: str):
    try:
        obj_id = ObjectId(author_id)
        return db.authors.find_one({"_id": obj_id})
    except Exception:
        return None

def list_authors(db: Database):
    return list(db.authors.find())

def delete_author(db: Database, author_id: str):
    try:
        obj_id = ObjectId(author_id)
        # Delete author
        delete_result = db.authors.delete_one({"_id": obj_id})
        if delete_result.deleted_count > 0:
            # Also delete all books by this author
            db.books.delete_many({"author_id": author_id})
            return True
        return False
    except Exception:
        return False

#Book CRUD Functions

def create_book(db: Database, author_id: str, book: models.BookCreate):
    book_dict = book.model_dump()
    book_dict["author_id"] = author_id
    result = db.books.insert_one(book_dict)
    return db.books.find_one({"_id": result.inserted_id})

def list_all_books(db: Database):
    return list(db.books.find())

def get_books_by_author(db: Database, author_id: str):
    return list(db.books.find({"author_id": author_id}))
