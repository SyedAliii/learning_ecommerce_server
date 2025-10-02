from pydantic import BaseModel

class GenericResponse(BaseModel):
    status_code: int
    msg: str