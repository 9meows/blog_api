import pytest

@pytest.mark.asyncio
async def test_register_success(client):
    register_reponse = await client.post("/api/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "qwerty"
    })
    assert register_reponse.status_code == 200
    assert register_reponse.json()["username"] == "testuser"
    
    
@pytest.mark.asyncio
async def test_register_failed(client):
    await client.post("/api/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "qwerty"
    })
    register_reponse = await client.post("/api/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "qwerty"
    })
    assert register_reponse.status_code == 400
    assert register_reponse.json()["detail"] == "Пользователь с таким username уже существует"
    

@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "qwerty"
    })
    
    loging_response = await client.post("/api/login", data={"username": "testuser", "password": "qwerty1"})
    
    assert loging_response.status_code == 401
    