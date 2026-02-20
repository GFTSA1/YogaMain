from sqlmodel import SQLModel, Field


class YogaCourseModel(SQLModel):
    name: str = Field(min_length=3)
    description: str
    price: float = Field(default=0.0, ge=0)
    level: str
