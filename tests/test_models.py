import pytest
from datetime import datetime
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


async def test_yoga_course_negative_price():
    invalid_data = {
        "name": "Valid Name",
        "description": "Test",
        "price": -10.5,
        "level": "Beginner",
    }
    with pytest.raises(ValidationError) as exc_info:
        YogaCourse.model_validate(invalid_data)

    assert "Input should be greater than or equal to 0" in str(exc_info.value)


async def test_yoga_course_name_too_short():
    invalid_data = {"name": "Yo", "description": "Short name test", "level": "Beginner"}

    with pytest.raises(ValidationError) as exc_info:
        YogaCourse.model_validate(invalid_data)

    assert "String should have at least 3 characters" in str(exc_info.value)


async def test_trip_valid_data(db_session):
    trip = Trip(
        name="Test Name",
        description="Test Description",
        location="Bali",
        start_date=datetime(2026, 5, 1),
        end_date=datetime(2026, 5, 10),
    )
    db_session.add(trip)
    await db_session.commit()
    await db_session.refresh(trip)

    assert trip.id is not None
    assert trip.name == "Test Name"
    assert trip.description == "Test Description"
    assert trip.start_date == datetime(2026, 5, 1)


async def test_trip_same_day():

    invalid_data = {
        "name": "Test Name",
        "location": "Kyiv",
        "start_date": datetime(2026, 7, 1),
        "end_date": datetime(2026, 7, 1),
    }

    with pytest.raises(ValidationError):
        Trip.model_validate(invalid_data)


async def test_trip_name_too_short():
    invalid_data = {
        "name": "Yo",
        "description": "Short name test",
        "location": "Kyiv",
        "start_date": datetime(2026, 7, 1),
        "end_date": datetime(2026, 7, 4),
    }

    with pytest.raises(ValidationError) as exc_info:
        YogaCourse.model_validate(invalid_data)

    assert "String should have at least 3 characters" in str(exc_info.value)
