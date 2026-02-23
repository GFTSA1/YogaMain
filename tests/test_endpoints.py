import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.models import YogaCourse


async def test_create_course(client):
    mock = {
        "name": "Test name",
        "description": "Dynamic movements",
        "price": 25.0,
        "level": "Intermediate",
    }

    response = await client.post("/courses", json=mock)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == mock["name"]
    assert "id" in data


async def test_get_all_courses(client):
    await client.post(
        "/courses",
        json={
            "name": "Initial Course",
            "description": "Test description",
            "price": 10.0,
            "level": "Beginner",
        },
    )

    response = await client.get("/courses")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == "Initial Course"
