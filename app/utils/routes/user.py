from sqlmodel import select
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.schemas import UserPatchModel


from app.models import User


class UserService:
    @staticmethod
    async def list_users(session, limit: int, offset: int) -> list[User]:
        result = await session.exec(select(User).offset(offset).limit(limit))
        return result.all()

    @staticmethod
    async def get_by_id(session, user_id: int) -> User | None:
        return await session.get(User, user_id)

    @staticmethod
    async def delete_user(session, user: User) -> None:
        await session.delete(user)
        await session.commit()

    @staticmethod
    async def update_user(session, user: User, data: UserPatchModel) -> User:
        user_update = data.model_dump(exclude_unset=True)
        user.sqlmodel_update(user_update)
        session.add(user)
        try:
            await session.commit()
            await session.refresh(user)
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already in use"
            )
        return user
