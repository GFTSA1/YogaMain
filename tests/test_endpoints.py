from fastapi import status


async def test_create_course(client):

    response = await client.post(
        "/courses",
        json={
            "name": "Test name",
            "description": "Dynamic movements",
            "price": 25.0,
            "level": "Intermediate",
        },
    )

    data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in data


async def test_create_wrong_data(client):
    response = await client.post(
        "/courses",
        json={
            "name": "Yo",
            "description": "Too short name and negative price",
            "price": -10.0,
            "level": "Beginner",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


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

    await client.post(
        "/courses",
        json={
            "name": "Initial Course",
            "description": "Test description",
            "price": 15.0,
            "level": "Intermediate",
        },
    )

    response = await client.get("/courses")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(data, list)
    assert len(data) > 1
    assert data[0]["name"] == "Initial Course"


async def test_get_course(client):
    response = await client.post(
        "/courses",
        json={
            "name": "Test",
            "description": "Test description",
            "price": 10,
            "level": "Beginner",
        },
    )
    course_id = response.json()["id"]

    response = await client.get(f"/courses/{course_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Test"


async def test_get_course_not_found(client):
    response = await client.post(
        "/courses",
        json={
            "name": "Test",
            "description": "Test description",
            "price": 10,
            "level": "Beginner",
        },
    )

    course_id = response.json()["id"]

    response = await client.get(f"/courses/{course_id + 1}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_update_course(client):
    response = await client.post(
        "/courses",
        json={
            "name": "Old Name",
            "description": "Test description",
            "price": 10,
            "level": "Beginner",
        },
    )
    course_id = response.json()["id"]

    update_response = await client.patch(
        f"/courses/{course_id}",
        json={
            "name": "New Name",
            "description": "Test description new",
            "price": 20,
            "level": "Intermediate",
        },
    )
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.json()["name"] == "New Name"
    assert update_response.json()["description"] == "Test description new"


async def test_update_wrong_data(client):
    response = await client.post(
        "/courses",
        json={
            "name": "Old Name",
            "description": "Test description",
            "price": 10,
            "level": "Beginner",
        },
    )
    course_id = response.json()["id"]

    update_response = await client.patch(
        f"/courses/{course_id}",
        json={
            "name": "N",
            "description": "Test description new",
            "price": -20,
            "level": "Intermediate",
        },
    )

    get_response = await client.get(f"/courses/{course_id}")
    current_data = get_response.json()

    assert update_response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert current_data["name"] == "Old Name"
    assert current_data["price"] == 10.0


async def test_update_wrong_course_id(client):
    response = await client.post(
        "/courses",
        json={
            "name": "Old Name",
            "description": "Test description",
            "price": 10,
            "level": "Beginner",
        },
    )
    course_id = response.json()["id"]
    wrong_id = course_id + 1

    update_response = await client.patch(
        f"/courses/{wrong_id}",
        json={
            "name": "New Name",
            "description": "Test description new",
            "price": 20,
            "level": "Intermediate",
        },
    )

    assert update_response.status_code == status.HTTP_404_NOT_FOUND
    assert update_response.json()["detail"] == "Course not found"


async def test_delete_course(client):
    response = await client.post(
        "/courses",
        json={
            "name": "To Delete",
            "description": "Test description",
            "price": 10,
            "level": "Beginner",
        },
    )
    course_id = response.json()["id"]

    del_response = await client.delete(f"/courses/{course_id}")
    assert del_response.status_code == status.HTTP_204_NO_CONTENT

    check_response = await client.get(f"/courses/{course_id}")
    assert check_response.status_code == status.HTTP_404_NOT_FOUND


async def test_create_trip(client):
    response = await client.post(
        "/trips",
        json={
            "name": "Test Name",
            "description": "Test Description",
            "location": "Test Location",
            "start_date": "2026-06-15T10:00:00Z",
            "end_date": "2026-06-20T10:00:00Z",
        },
    )

    data = response.json()

    assert "id" in data
    assert response.status_code == status.HTTP_201_CREATED
    assert data["id"] is not None
    assert data["name"] == "Test Name"
    assert data["location"] == "Test Location"


async def test_create_trip_wrong_data(client):
    response = await client.post(
        "/trips",
        json={
            "name": "Test Name",
            "description": "Test Description",
            "location": "Test Location",
            "start_date": "2026-06-15T10:00:00Z",
            "end_date": "2026-06-15T10:00:00Z",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_get_all_trips(client):
    await client.post(
        "/trips",
        json={
            "name": "Test Name",
            "description": "Test Description",
            "location": "Test Location",
            "start_date": "2026-06-15T10:00:00Z",
            "end_date": "2026-06-20T10:00:00Z",
        },
    )

    await client.post(
        "/trips",
        json={
            "name": "Test Name",
            "description": "Test Description",
            "location": "Test Location",
            "start_date": "2026-07-15T10:00:00Z",
            "end_date": "2026-07-18T10:00:00Z",
        },
    )

    response = await client.get("/trips")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["name"] == "Test Name"


async def test_get_trip(client):
    response = await client.post(
        "/trips",
        json={
            "name": "Test Name",
            "description": "Test Description",
            "location": "Test Location",
            "start_date": "2026-06-15T10:00:00Z",
            "end_date": "2026-06-16T10:00:00Z",
        },
    )
    trips_id = response.json()["id"]

    response = await client.get(f"/trips/{trips_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Test Name"


async def test_get_trip_not_found(client):
    response = await client.post(
        "/trips",
        json={
            "name": "Test Name",
            "description": "Test Description",
            "location": "Test Location",
            "start_date": "2026-06-15T10:00:00Z",
            "end_date": "2026-06-17T10:00:00Z",
        },
    )

    trips_id = response.json()["id"]

    response = await client.get(f"/trips/{trips_id + 1}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_patch_trip(client):
    response = await client.post(
        "/trips",
        json={
            "name": "Test Name",
            "description": "Test Description",
            "location": "Test Location",
            "start_date": "2026-06-15T10:00:00Z",
            "end_date": "2026-06-17T10:00:00Z",
        },
    )
    trips_id = response.json()["id"]

    update_response = await client.patch(
        f"/trips/{trips_id}",
        json={"name": "New Name"},
    )
    assert update_response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), dict)
    assert update_response.json()["name"] == "New Name"


async def test_trip_patch_wrong_data(client):
    response = await client.post(
        "/trips",
        json={
            "name": "Test Name",
            "description": "Test description",
            "location": "Test location",
            "start_date": "2026-06-15T10:00:00Z",
            "end_date": "2026-06-18T10:00:00Z",
        },
    )
    trips_id = response.json()["id"]

    update_response = await client.patch(
        f"/trips/{trips_id}",
        json={
            "name": "Test Name",
            "description": "Test description",
            "location": "Test location",
            "start_date": "2026-06-15T10:00:00Z",
            "end_date": "2026-06-14T10:00:00Z",
        },
    )

    get_response = await client.get(f"/trips/{trips_id}")
    current_data = get_response.json()

    assert update_response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert current_data["name"] == "Test Name"


async def test_patch_wrong_trip_id(client):
    response = await client.post(
        "/trips",
        json={
            "name": "Test Name",
            "description": "Test Description",
            "location": "Test Location",
            "start_date": "2026-06-15T10:00:00Z",
            "end_date": "2026-06-16T10:00:00Z",
        },
    )
    trip_id = response.json()["id"]
    wrong_id = trip_id + 1

    update_response = await client.patch(
        f"/trips/{wrong_id}",
        json={
            "name": "Test Name",
            "description": "Test Description",
            "location": "Test Location",
            "start_date": "2026-06-15T10:00:00Z",
            "end_date": "2026-06-16T10:00:00Z",
        },
    )

    assert update_response.status_code == status.HTTP_404_NOT_FOUND
    assert update_response.json()["detail"] == "Trip not found"


async def test_delete_trip(client):
    response = await client.post(
        "/trips",
        json={
            "name": "Test Name",
            "description": "Test Description",
            "location": "Test Location",
            "start_date": "2026-06-15T10:00:00Z",
            "end_date": "2026-06-16T10:00:00Z",
        },
    )
    trip_id = response.json()["id"]

    del_response = await client.delete(f"/trips/{trip_id}")
    assert del_response.status_code == status.HTTP_204_NO_CONTENT

    check_response = await client.get(f"/trips/{trip_id}")
    assert check_response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_trip_wrong_id(client):
    response = await client.post(
        "/trips",
        json={
            "name": "Test Name",
            "description": "Test Description",
            "location": "Test Location",
            "start_date": "2026-06-15T10:00:00Z",
            "end_date": "2026-06-16T10:00:00Z",
        },
    )
    trip_id = response.json()["id"]
    del_response = await client.delete(f"/trips/{trip_id + 1}")
    assert del_response.status_code == status.HTTP_404_NOT_FOUND
