import pytest
from pydantic import ValidationError

from app.models import YogaCourse, Trip


async def test_yoga_course_valid_data(db_session):
    course = YogaCourse(
        name="Hatha Basic", description="Good for all", price=100.0, level="Beginner"
    )
    db_session.add(course)
    await db_session.commit()
    await db_session.refresh(course)

    assert course.id is not None
    assert isinstance(course.id, (int, str))
    assert course.name == "Hatha Basic"


async def test_yoga_course_default_price(db_session):
    course = YogaCourse(
        name="Free Yoga", description="No price provided", level="Beginner"
    )
    db_session.add(course)
    await db_session.commit()
    await db_session.refresh(course)

    assert course.price == 0.0


def test_yoga_course_negative_price():
    invalid_data = {
        "name": "Valid Name",
        "description": "Test",
        "price": -10.5,
        "level": "Beginner",
    }
    with pytest.raises(ValidationError) as exc_info:
        YogaCourse.model_validate(invalid_data)

    assert "Input should be greater than or equal to 0" in str(exc_info.value)


def test_yoga_course_name_too_short():
    invalid_data = {"name": "Yo", "description": "Short name test", "level": "Beginner"}

    with pytest.raises(ValidationError) as exc_info:
        YogaCourse.model_validate(invalid_data)

    assert "String should have at least 3 characters" in str(exc_info.value)
