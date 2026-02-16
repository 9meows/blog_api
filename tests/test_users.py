import pytest


@pytest.mark.asyncio
async def test_get_users_list(auth_client):
    all_users = await auth_client.get("/api/users/")
    
    assert all_users.status_code == 200
    assert type(all_users.json()) is list
    
@pytest.mark.asyncio
async def test_get_user_by_username(auth_client):
    user = await auth_client.get("/api/users/testuser")

    assert user.status_code == 200
    assert user.json()["username"]  == "testuser" 
    
@pytest.mark.asyncio
async def test_get_user_posts(auth_client):
    post_created = await auth_client.post("/api/posts/", json={
    "title":"BOO ISPUGALSYA? DONT BE AFRAID:)",
    "content": "a" * 100,
    "status": "published",
    "tags": []})
    
    get_reponse = await auth_client.get("/api/users/testuser/posts")
    assert get_reponse.status_code == 200
    assert type(get_reponse.json()) is list