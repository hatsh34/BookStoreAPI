import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, ANY
from bson import ObjectId

from app.main import app
from app.database import get_database


@pytest.fixture
def mock_db():
    """Provides a mock database object for tests."""
    return AsyncMock()   
    # AsyncMock comes from Python's unittest.mock library and is a special type of mock object designed for async functions. 
    # It knows how to be awaited, which is essential for your application.

@pytest.fixture(autouse=True)  #tells pytest to run this fixture automatically before every single test in this file.
def override_db(mock_db):
    """
    This fixture automatically replaces the `get_database` dependency 
    with the mock_db for every test in this file.
    """ 
    app.dependency_overrides[get_database] = lambda: mock_db
    yield
    app.dependency_overrides.clear()


# --- Tests for creating books for an author ---

@pytest.mark.asyncio
async def test_create_book_for_author_success():
    """Tests successful creation of a book for a given author."""
    #data and conditions for the test
    fake_author_id = str(ObjectId())
    # The payload must match the BookCreate model exactly.
    test_payload = {
        "title": "A Great Test Book",
        "isbn": "978-3-16-148410-0",
        "author_id": fake_author_id # This field is required 
    }

    mock_author = {
        "_id": ObjectId(fake_author_id),
        "first_name": "John", "last_name": "Smith", "email": "john@example.com"
    }
    mock_book = {
        "_id": ObjectId(), "title": test_payload["title"], "isbn": test_payload["isbn"], "author_id": fake_author_id
    }
    #Performing actions to test
    with patch("app.routers.books.crud.get_author", new_callable=AsyncMock, return_value=mock_author) as mock_get_author, \
         patch("app.routers.books.crud.create_book", new_callable=AsyncMock, return_value=mock_book) as mock_create_book:

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # --- FIXED ENDPOINT ---
            # The correct endpoint includes the author_id in the path.
            response = await client.post(f"/books/by-author/{fake_author_id}", json=test_payload)
            
    #ASSERT: Check that the outcome is what you expected.
    assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.json()}"
    data = response.json()
    assert data["title"] == test_payload["title"]
    assert "author" in data
    assert data["author"]["email"] == mock_author["email"]
    
    mock_get_author.assert_awaited_once_with(ANY, fake_author_id)
    mock_create_book.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_book_for_missing_author():
    """Tests that creating a book fails if the author does not exist."""
    fake_author_id = str(ObjectId())
    test_payload = {"title": "Ghost Book", "isbn": "111-2223334445", "author_id": fake_author_id}

    with patch("app.routers.books.crud.get_author", new_callable=AsyncMock, return_value=None) as mock_get_author:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # --- FIXED ENDPOINT ---
            response = await client.post(f"/books/by-author/{fake_author_id}", json=test_payload)

    assert response.status_code == 404, f"Expected 404, got {response.status_code}. Response: {response.json()}"
    assert "author with id" in response.json()["detail"].lower()
    mock_get_author.assert_awaited_once_with(ANY, fake_author_id)


# --- Tests for retrieving books ---

@pytest.mark.asyncio
async def test_get_books_by_author():
    """Tests successfully retrieving all books by a specific author."""
    fake_author_id = str(ObjectId())
    mock_author = {"_id": ObjectId(fake_author_id), "first_name": "Jane", "last_name": "Austen", "email": "jane@example.com"}
    mock_books = [{"_id": ObjectId(), "title": "Pride", "isbn": "123-abc", "author_id": fake_author_id}]

    with patch("app.routers.books.crud.get_author", new_callable=AsyncMock, return_value=mock_author), \
         patch("app.routers.books.crud.list_books_by_author", new_callable=AsyncMock, return_value=mock_books) as mock_list_books:

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # --- FIXED ENDPOINT ---
            # The correct endpoint is /books/by-author/{author_id}
            response = await client.get(f"/books/by-author/{fake_author_id}")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.json()}"
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == mock_books[0]["title"]
    assert data[0]["author"]["email"] == mock_author["email"] 
    mock_list_books.assert_awaited_once_with(ANY, fake_author_id)


@pytest.mark.asyncio
async def test_get_single_book_success():
    """Tests successfully retrieving a single book by its ID."""
    fake_book_id = str(ObjectId())
    fake_author_id = str(ObjectId())
    
    mock_book_from_db = {"_id": ObjectId(fake_book_id), "title": "A Testable Book", "isbn": "123-4567890123", "author_id": fake_author_id}
    mock_author_from_db = {"_id": ObjectId(fake_author_id), "first_name": "Testy", "last_name": "McTestFace", "email": "testy@example.com"}

    with patch("app.routers.books.crud.get_book", new_callable=AsyncMock, return_value=mock_book_from_db) as mock_get_book, \
         patch("app.routers.books.crud.get_author", new_callable=AsyncMock, return_value=mock_author_from_db) as mock_get_author:
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # This now tests the newly created GET /books/{book_id} endpoint
            response = await client.get(f"/books/{fake_book_id}")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.json()}"
    data = response.json()
    assert data["title"] == mock_book_from_db["title"]
    assert data["_id"] == fake_book_id
    assert data["author"]["email"] == mock_author_from_db["email"]
    mock_get_book.assert_awaited_once_with(ANY, fake_book_id)
    mock_get_author.assert_awaited_once_with(ANY, fake_author_id)


@pytest.mark.asyncio
async def test_get_single_book_not_found():
    """Tests that retrieving a non-existent book returns a 404 error."""
    fake_book_id = str(ObjectId())

    with patch("app.routers.books.crud.get_book", new_callable=AsyncMock, return_value=None) as mock_get_book:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # This now tests the newly created GET /books/{book_id} endpoint
            response = await client.get(f"/books/{fake_book_id}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    mock_get_book.assert_awaited_once_with(ANY, fake_book_id)