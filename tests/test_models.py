
import pytest
from app.models import AuthorInDB

def test_author_model_handles_old_data():
    """
    Tests that the backward-compatibility validator correctly
    parses the old single 'name' field into the new structure.
    """
    old_data = {
        "_id": "60d5ec49e7b4e9e4a8e1c3d4",
        "name": "George R. R. Martin",
        "email": "grrm@example.com"
    }
    
    author = AuthorInDB.model_validate(old_data)
    
    assert author.first_name == "George"
    assert author.middle_name == "R. R."
    assert author.last_name == "Martin"
    # Also test the computed 'name' dictionary
    assert author.name.first == "George"
    assert author.name.last == "Martin"

def test_author_model_handles_new_data():
    """
    Tests that the model works correctly when given data
    in the new format.
    """
    new_data = {
        "_id": "60d5ec49e7b4e9e4a8e1c3d5",
        "first_name": "J. R. R.",
        "last_name": "Tolkien",
        "email": "jrrt@example.com"
    }
    
    author = AuthorInDB.model_validate(new_data)
    
    assert author.first_name == "J. R. R."
    assert author.last_name == "Tolkien"
    assert author.middle_name is None # Check that optional field is handled
    assert author.name.first == "J. R. R."

def test_author_model_handles_two_part_name():
    """Tests the validator with a simple two-part name."""
    old_data = {
        "_id": "60d5ec49e7b4e9e4a8e1c3d6",
        "name": "Jane Austen",
        "email": "jane@example.com"
    }
    
    author = AuthorInDB.model_validate(old_data)
    
    assert author.first_name == "Jane"
    assert author.last_name == "Austen"
    assert author.middle_name is None
