from fastapi import Depends
from typing import Annotated
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database import get_session

SessionDep = Annotated[AsyncSession, Depends(get_session)]
