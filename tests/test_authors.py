import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, ANY
from bson import ObjectId

from app.main import app
from app.database import get_database


@pytest.fixture
def mock_db():
    return AsyncMock() 

@pytest.fixture(autouse=True)
def override_db(mock_db):
    app.dependency_overrides[get_database] = lambda: mock_db
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_book_for_author_success():
    fake_author_id = str(ObjectId())
    # --- FIXED PAYLOAD ---
    # The payload must match the BookCreate model.
    test_payload = {
        "title": "Test Book",
        "isbn": "978-1-23-456789-0",
        "author_id": fake_author_id # This field is required by the model
    }

    mock_author = {
        "_id": ObjectId(fake_author_id),
        "first_name": "John",
        "last_name": "Smith",
        "email": "john@example.com"
    }

    mock_book = {
        "_id": ObjectId(),
        "title": test_payload["title"],
        "isbn": test_payload["isbn"],
        "author_id": fake_author_id
    }

    with patch("app.routers.books.crud.get_author", new_callable=AsyncMock, return_value=mock_author) as mock_get_author, \
         patch("app.routers.books.crud.create_book", new_callable=AsyncMock, return_value=mock_book) as mock_create_book:

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # The endpoint is /books/by-author/{author_id}
            response = await client.post(f"/books/by-author/{fake_author_id}", json=test_payload)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == test_payload["title"]
    assert data["author"]["email"] == mock_author["email"]

    mock_get_author.assert_awaited_once_with(ANY, fake_author_id)
    mock_create_book.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_book_for_missing_author():
    fake_author_id = str(ObjectId())
    # --- FIXED PAYLOAD ---
    test_payload = {
        "title": "Ghost Book",
        "isbn": "978-0-98-765432-1",
        "author_id": fake_author_id
    }

    with patch("app.routers.books.crud.get_author", new_callable=AsyncMock, return_value=None) as mock_get_author:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(f"/books/by-author/{fake_author_id}", json=test_payload)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
    # --- FIXED ASSERTION ---
    mock_get_author.assert_awaited_once_with(ANY, fake_author_id)


@pytest.mark.asyncio
async def test_get_books_by_author():
    fake_author_id = str(ObjectId())
    mock_author = {
        "_id": ObjectId(fake_author_id),
        "first_name": "Jane",
        "last_name": "Austen",
        "email": "jane@example.com"
    }

    mock_books = [
        {
            "_id": ObjectId(),
            "title": "Pride",
            "isbn": "12345",
            "author_id": fake_author_id
        }
    ]

    # --- FIXED PATCH ---
    # The function is named list_books_by_author in crud.py
    with patch("app.routers.books.crud.get_author", new_callable=AsyncMock, return_value=mock_author) as mock_get_author, \
         patch("app.routers.books.crud.list_books_by_author", new_callable=AsyncMock, return_value=mock_books) as mock_get_books:

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/books/by-author/{fake_author_id}")

    assert response.status_code == 200
    data = response.json()
    assert data[0]["title"] == mock_books[0]["title"]
    assert data[0]["author"]["email"] == mock_author["email"]

    mock_get_author.assert_awaited_once_with(ANY, fake_author_id)
    mock_get_books.assert_awaited_once_with(ANY, fake_author_id)


@pytest.mark.asyncio
async def test_get_books_by_author_not_found():
    fake_author_id = str(ObjectId())

    with patch("app.routers.books.crud.get_author", new_callable=AsyncMock, return_value=None) as mock_get_author:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/books/by-author/{fake_author_id}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
    # --- FIXED ASSERTION ---
    mock_get_author.assert_awaited_once_with(ANY, fake_author_id)