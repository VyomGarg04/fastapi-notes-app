from pydantic import BaseModel, Field
class Note(BaseModel):
    title: str
    content : str
    important :bool = False
    category:str | None = None
    tags: list[str] = Field(default_factory=list)