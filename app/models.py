from pydantic import ConfigDict, BaseModel, Field, EmailStr, computed_field, model_validator
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

from typing import List, Optional # Make sure Optional is imported
"""In MongoDB, each document has an _id field, which is an ObjectId. 
But JSON (used in APIs) does not understand ObjectIds, so you convert them to string"""
"""'Annotated' lets us add metadata. 'BeforeValidator(str)' tells Pydantic to
 run the `str()` function on the value before trying to validate it."""
PyObjectId = Annotated[str, BeforeValidator(str)]

# --- A nested model for the author's name ---
class AuthorName(BaseModel):
    first: str = Field(..., description="Author's first name")
    middle: Optional[str] = Field(None, description="Author's middle name, if any")
    last: str = Field(..., description="Author's last name")
 
 
class AuthorBase(BaseModel):
    # These are the fields we want our final model to have.
    first_name: str = Field(..., description="The author's first name.")
    middle_name: Optional[str] = Field(None, description="The author's middle name. This field is optional.")
    last_name: str = Field(..., description="The author's last name.")
    email: EmailStr = Field(..., description="The email of the author.")

    # This is the magic! A model_validator runs before any other validation.
    # It allows us to modify the incoming data (from the database) on the fly.
    @model_validator(mode='before')
    @classmethod
    def handle_old_data(cls, data: any) -> any:
        # We only run this logic if the data is a dictionary (like from Mongo)
        # and it has the old 'name' field but NOT the new 'first_name' field.
        if isinstance(data, dict) and 'name' in data and 'first_name' not in data:
            # This is old data. 
            full_name = data.get('name', '')
            parts = full_name.split()
            
            # logic to split the name.
            if len(parts) > 0:
                data['first_name'] = parts[0]
                if len(parts) > 2:
                    data['middle_name'] = " ".join(parts[1:-1])
                    data['last_name'] = parts[-1]
                elif len(parts) == 2:
                    data['last_name'] = parts[1]
                else:
                    # If there's only one part, use it as first and last name.
                    data['last_name'] = parts[0]
            else:
                # If name is empty, provide defaults to pass validation.
                data['first_name'] = "N/A"
                data['last_name'] = "N/A"

        return data

class AuthorCreate(BaseModel):
    # For creating NEW authors, we want to enforce the new structure.
    # We don't include the validator here.
    first_name: str = Field(..., description="The author's first name.")
    middle_name: Optional[str] = Field(None, description="The author's middle name. This field is optional.")
    last_name: str = Field(..., description="The author's last name.")
    email: EmailStr = Field(..., description="The email of the author.")


# --- MODIFIED: AuthorInDB now inherits from the smarter AuthorBase ---
class AuthorInDB(AuthorBase):
    id: PyObjectId = Field(alias="_id", description="The unique ID of the author.")
    
    @computed_field
    @property
    def name(self) -> AuthorName:
        return AuthorName(
            first=self.first_name,
            middle=self.middle_name,
            last=self.last_name
        )
        
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

# --- Book Models (No changes needed here) ---
class BookBase(BaseModel):
    title: str = Field(..., description="The title of the book.")
    isbn: str = Field(..., description="The International Standard Book Number.")

class BookCreate(BookBase):
    author_id: str = Field(...)

class BookInDB(BookBase):
    id: PyObjectId = Field(alias="_id")
    author_id: str = Field(description="The ID of the author.")
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

class BookWithAuthor(BookBase):
    id: PyObjectId = Field(alias="_id")
    author: AuthorInDB = Field(..., description="The author of the book.")
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
