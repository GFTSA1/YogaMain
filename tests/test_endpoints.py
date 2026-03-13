from http.client import responses

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

    data = response.json()

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


async def test_get_studios(client):
    await client.post(
        "/studios",
        json={"city": "Kyiv", "capacity": 30, "address": "Khreshchatyk 1, Kyiv 01001"},
    )

    await client.post(
        "/studios",
        json={"city": "Lviv", "capacity": 50, "address": "Rynok Square 1, Lviv 79000"},
    )

    response = await client.get("/studios")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2

async def test_create_studio(client):
    response = await client.post(
        "/studios",
        json={"city": "Lviv", "capacity": 50, "address": "Rynok Square 1, Lviv 79000"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["city"] == "Lviv"

async def test_studio_creation_wrong_data(client):
    response = await client.post(
        "/studios",
        json={"city": "Lviv", "address": "Rynok Square 1, Lviv 79000"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_get_single_studio(client):
    response = await client.post(
        "/studios",
        json={"city": "Kyiv", "capacity": 30, "address": "Khreshchatyk 1, Kyiv 01001"},
    )
    studio_id = response.json()["id"]
    response = await client.get(f"/studios/{studio_id}")

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), dict)
    assert response.json()["city"] == "Kyiv"


async def test_patch_studio(client):
    response = await client.post(
        "/studios",
        json={"city": "Kyiv", "capacity": 30, "address": "Khreshchatyk 1, Kyiv 01001"},
    )

    studio_id = response.json()["id"]
    response = await client.patch(
        f"/studios/{studio_id}",
        json={'city': 'New York'}
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), dict)
    assert response.json()["city"] == "New York"


async def test_patch_studio_wrong_data(client):
    response = await client.post(
        "/studios",
        json={"city": "Kyiv", "capacity": 30, "address": "Khreshchatyk 1, Kyiv 01001"}
    )

    studio_id = response.json()["id"]
    response = await client.patch(
        f"/studios/{studio_id}",
        json={'street': 'Gaga 11'}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    response = await client.get(
        f"/studios/{studio_id}",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["city"] == "Kyiv"
    assert response.json().get("street") == None

async def test_patch_studio_wrong_data_id(client):
    response = await client.post(
        "/studios",
        json={"city": "Kyiv", "capacity": 30, "address": "Khreshchatyk 1, Kyiv 01001"}
    )

    studio_id = response.json()["id"]
    response = await client.patch(
        f"/studios/{studio_id+1}",
        json={'city': 'Jojo'}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    response = await client.get(
        f"/studios/{studio_id}",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["city"] == "Kyiv"

async def test_delete_studio(client):
    response = await client.post(
        "/studios",
        json={"city": "Kyiv", "capacity": 30, "address": "Khreshchatyk 1, Kyiv 01001"}
    )

    studio_id = response.json()["id"]
    response = await client.delete(f"/studios/{studio_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = await client.get(f"/studios/{studio_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

async def delete_studio_wrong_id(client):
    response = await client.post(
        "/studios",
        json={"city": "Kyiv", "capacity": 30, "address": "Khreshchatyk 1, Kyiv 01001"}
    )

    studio_id = response.json()["id"]
    response = await client.delete(f"/studios/{studio_id+1}")

    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = await client.get(f"/studios/{studio_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["city"] == "Kyiv"