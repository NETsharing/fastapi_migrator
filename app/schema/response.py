from pydantic import BaseModel


class BaseSchema(BaseModel):
    """
    A base validation schema of the application.
    """

    class Config:
        anystr_strip_whitespace = True


class ErrorResponse(BaseSchema):

    code: int
    message: str
