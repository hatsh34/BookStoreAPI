from fastapi import FastAPI
from .routers import authors, books

app = FastAPI(
    title="Bookstore API",
    summary="A structured API to manage authors and their books.",
)

# Include the routers from the routers package
app.include_router(authors.router)
app.include_router(books.router)

@app.get("/", tags=["Root"])
def read_root():
    """
    Welcome endpoint. Provides a link to the API documentation.
    """
    return {"message": "Welcome to the Bookstore API! Visit /docs for the API documentation."}