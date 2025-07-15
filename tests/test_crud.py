import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from app import crud, models

# Mark all tests in this file as async, so pytest runs them in an event loop.
pytestmark = pytest.mark.asyncio

# --- Author CRUD Tests ---

async def test_create_author():
    """Tests that the create_author crud function works correctly."""
    mock_db = AsyncMock()
    mock_db.authors.insert_one.return_value = MagicMock(inserted_id=ObjectId())
    mock_db.authors.find_one.return_value = {"_id": ObjectId(), "email": "test@example.com"}

    author_data = models.AuthorCreate(
        first_name="Test",
        last_name="Author",
        email="test@example.com"
    )

    result = await crud.create_author(db=mock_db, author=author_data)

    mock_db.authors.insert_one.assert_awaited_once()
    mock_db.authors.find_one.assert_awaited_once()
    assert result is not None
    assert result["email"] == author_data.email

async def test_get_author_success():
    """Tests successfully retrieving an author by a valid ID."""
    mock_db = AsyncMock()
    author_id = ObjectId()
    expected_author = {"_id": author_id, "first_name": "Found", "last_name": "Me"}
    mock_db.authors.find_one.return_value = expected_author

    result = await crud.get_author(db=mock_db, author_id=str(author_id))

    mock_db.authors.find_one.assert_awaited_once_with({"_id": author_id})
    assert result == expected_author

async def test_get_author_invalid_id():
    """Tests that get_author returns None for a malformed ObjectId string."""
    mock_db = AsyncMock()
    result = await crud.get_author(db=mock_db, author_id="this-is-not-an-id")
    mock_db.authors.find_one.assert_not_called()
    assert result is None

async def test_list_authors():
    """Tests that the list_authors crud function works correctly."""
    # --- THIS IS THE FIX ---
    # Use a standard MagicMock for the db object.
    mock_db = MagicMock()
    # Create an AsyncMock to represent the cursor object.
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [{"name": "Author 1"}, {"name": "Author 2"}]
    # Configure the synchronous find() method to return our async cursor mock.
    mock_db.authors.find.return_value = mock_cursor

    result = await crud.list_authors(db=mock_db)

    # Assert the synchronous find() was called.
    mock_db.authors.find.assert_called_once_with()
    # Assert the asynchronous to_list() was awaited.
    mock_cursor.to_list.assert_awaited_once_with(length=100)
    assert len(result) == 2

async def test_delete_author_success():
    """Tests successful deletion of an author and their books."""
    mock_db = AsyncMock()
    mock_db.authors.delete_one.return_value = MagicMock(deleted_count=1)
    mock_db.books.delete_many.return_value = MagicMock()
    
    author_id = str(ObjectId())
    result = await crud.delete_author(db=mock_db, author_id=author_id)

    mock_db.authors.delete_one.assert_awaited_once()
    mock_db.books.delete_many.assert_awaited_once_with({"author_id": author_id})
    assert result is True

async def test_delete_author_not_found():
    """Tests deletion when the author is not found."""
    mock_db = AsyncMock()
    mock_db.authors.delete_one.return_value = MagicMock(deleted_count=0)
    
    author_id = str(ObjectId())
    result = await crud.delete_author(db=mock_db, author_id=author_id)

    mock_db.authors.delete_one.assert_awaited_once()
    mock_db.books.delete_many.assert_not_called()
    assert result is False

# --- Book CRUD Tests ---

async def test_create_book():
    """Tests that the create_book crud function works correctly."""
    mock_db = AsyncMock()
    mock_db.books.insert_one.return_value = MagicMock(inserted_id=ObjectId())
    mock_db.books.find_one.return_value = {"_id": ObjectId(), "title": "Test Book"}

    author_id = str(ObjectId())
    book_data = models.BookCreate(
        title="Test Book",
        isbn="123-456",
        author_id=author_id
    )

    result = await crud.create_book(db=mock_db, author_id=author_id, book=book_data)

    mock_db.books.insert_one.assert_awaited_once()
    mock_db.books.find_one.assert_awaited_once()
    assert result is not None
    assert result["title"] == book_data.title

async def test_get_book_success():
    """Tests successfully retrieving a book by a valid ID."""
    mock_db = AsyncMock()
    book_id = ObjectId()
    expected_book = {"_id": book_id, "title": "Found Book"}
    mock_db.books.find_one.return_value = expected_book

    result = await crud.get_book(db=mock_db, book_id=str(book_id))

    mock_db.books.find_one.assert_awaited_once_with({"_id": book_id})
    assert result == expected_book

async def test_get_book_invalid_id():
    """Tests that get_book returns None for a malformed ObjectId string."""
    mock_db = AsyncMock()
    result = await crud.get_book(db=mock_db, book_id="not-a-real-id")
    mock_db.books.find_one.assert_not_called()
    assert result is None

async def test_list_books_by_author():
    """Tests retrieving all books for a specific author."""
    # --- APPLY THE SAME FIX HERE ---
    mock_db = MagicMock()
    author_id = str(ObjectId())
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [{"title": "Book 1"}, {"title": "Book 2"}]
    mock_db.books.find.return_value = mock_cursor

    result = await crud.list_books_by_author(db=mock_db, author_id=author_id)

    mock_db.books.find.assert_called_once_with({"author_id": author_id})
    mock_cursor.to_list.assert_awaited_once_with(length=100)
    assert len(result) == 2
