from sqlmodel import SQLModel, Field


class PKMixin(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
