import pytest
from datetime import datetime
from pydantic import ValidationError
from sqlmodel import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from app.models import YogaCourse, Trip, Video


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

    assert course.price == 5.0


async def test_yoga_course_negative_price():
    invalid_data = {
        "name": "Valid Name",
        "description": "Test",
        "price": -10.5,
        "level": "Beginner",
    }
    with pytest.raises(ValidationError) as exc_info:
        YogaCourse.model_validate(invalid_data)

    assert "Input should be greater than 0" in str(exc_info.value)


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


async def test_video_valid_data(db_session):
    course = YogaCourse(name="Hatha Basic", level="Beginner")
    db_session.add(course)
    await db_session.commit()

    video = Video(
        title="Intro to Yoga", s3_key="videos/unique_key.mp4", yoga_course_id=course.id
    )
    db_session.add(video)
    await db_session.commit()
    await db_session.refresh(video)

    assert video.id is not None
    assert video.course.name == "Hatha Basic"


async def test_video_unique_title_per_course(db_session):
    course = YogaCourse(name="Hatha Flow", level="Intermediate")
    db_session.add(course)
    await db_session.commit()

    video1 = Video(title="Intro", s3_key="key1.mp4", yoga_course_id=course.id)
    db_session.add(video1)
    await db_session.commit()

    video2 = Video(title="Intro", s3_key="key2.mp4", yoga_course_id=course.id)
    db_session.add(video2)

    with pytest.raises(IntegrityError):
        await db_session.commit()


async def test_video_yoga_course_relationship(db_session):
    course = YogaCourse(name="Advanced Vinyasa", level="Advanced")
    db_session.add(course)
    await db_session.commit()

    video1 = Video(title="Warm up", s3_key="s3://1", yoga_course_id=course.id)
    video2 = Video(title="Main Flow", s3_key="s3://2", yoga_course_id=course.id)
    db_session.add_all([video1, video2])
    await db_session.commit()

    statement = (
        select(Video).where(Video.id == video1.id).options(selectinload(Video.course))
    )
    video_db = (await db_session.exec(statement)).one()
    assert video_db.course.name == "Advanced Vinyasa"

    statement = (
        select(YogaCourse)
        .where(YogaCourse.id == course.id)
        .options(selectinload(YogaCourse.videos))
    )
    course_db = (await db_session.exec(statement)).one()

    assert len(course_db.videos) == 2
    assert any(v.title == "Main Flow" for v in course_db.videos)
    assert isinstance(course_db.videos[0], Video)
