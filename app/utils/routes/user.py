from sqlmodel import select

from app.models import (
    GroupTrainingStudioUser,
    RefreshToken,
    User,
    UserTrip,
    UserYogaCourse,
)


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
        for model, attr in (
            (RefreshToken, RefreshToken.user_id),
            (UserTrip, UserTrip.user_id),
            (UserYogaCourse, UserYogaCourse.user_id),
            (GroupTrainingStudioUser, GroupTrainingStudioUser.user_id),
        ):
            rows = (await session.exec(select(model).where(attr == user.id))).all()
            for row in rows:
                await session.delete(row)
        await session.delete(user)
        await session.commit()
