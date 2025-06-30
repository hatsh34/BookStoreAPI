from pydantic import ConfigDict, BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator
from typing import Annotated, List


PyObjectId = Annotated[str, BeforeValidator(str)]

#Author Models 

class AuthorBase(BaseModel):
    name: str = Field(..., description="The name of the author.")
    email: EmailStr = Field(..., description="The email of the author.")

class AuthorCreate(AuthorBase):
    pass

class AuthorInDB(AuthorBase):
    id: PyObjectId = Field(alias="_id", description="The unique ID of the author.")
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

#Book Models 

class BookBase(BaseModel):
    title: str = Field(..., description="The title of the book.")
    isbn: str = Field(..., description="The International Standard Book Number.")

class BookCreate(BookBase):
    pass

class BookInDB(BookBase):
    id: PyObjectId = Field(alias="_id", description="The unique ID of the book.")
    author_id: str = Field(description="The ID of the author.")
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

class BookWithAuthor(BookBase):
    id: PyObjectId = Field(alias="_id", description="The unique ID of the book.")
    author: AuthorInDB = Field(..., description="The author of the book.")
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
