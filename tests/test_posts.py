import pytest


@pytest.mark.asyncio()
async def test_create_post_authorized(auth_client):
    post_responese = await auth_client.post("/api/posts/", json={
        "title":"BOO ISPUGALSYA? DONT BE AFRAID:)",
        "content": "a" * 100,
        "status": "published",
        "tags": []
    })

    assert post_responese.status_code == 201
    assert post_responese.json()["title"] == "BOO ISPUGALSYA? DONT BE AFRAID:)"
    
    

@pytest.mark.asyncio()
async def test_create_post_unauthorized(client):
    post_responese = await client.post("/api/posts/", json={
    "title":"BOO ISPUGALSYA? DONT BE AFRAID:)",
    "content": "a" * 100,
    "status": "published",
    "tags": []
    })

    assert post_responese.status_code == 401
    assert post_responese.json()["detail"] == "Not authenticated"

@pytest.mark.asyncio()
async def test_get_posts_list(client):
    posts_responese = await client.get("/api/posts/")
    
    assert posts_responese.status_code == 200
    assert type(posts_responese.json()) is list

@pytest.mark.asyncio()
async def test_get_post_by_slug(auth_client):
    created_post = await auth_client.post("/api/posts/", json={
    "title":"BOO ISPUGALSYA? DONT BE AFRAID:)",
    "content": "a" * 100,
    "status": "published",
    "tags": []
    })
    response = await auth_client.get(f"/api/posts/{created_post.json()['slug']}")
    
    assert response.status_code == 200
    assert response.json()["title"] == "BOO ISPUGALSYA? DONT BE AFRAID:)"
    assert response.json()["status"] == "published"
    
@pytest.mark.asyncio()
async def test_delete_post_by_author(auth_client):
    del_post = await auth_client.post("/api/posts/", json={
        "title":"BOO ISPUGALSYA? DONT BE AFRAID:)",
        "content": "a" * 100,
        "status": "published",
        "tags": []
    })
    response = await auth_client.delete(f'/api/posts/{del_post.json()["slug"]}')

    assert response.status_code == 204

@pytest.mark.asyncio()
async def test_delete_post_unauthorized(auth_client, client):
    created_post = await auth_client.post("/api/posts/", json={
        "title": "BOO ISPUGALSYA? DONT BE AFRAID:)",
        "content": "a" * 100,
        "status": "published",
        "tags": []
    })
    slug = created_post.json()["slug"]

    response = await auth_client.delete(
        f"/api/posts/{slug}",
        headers={"Authorization": ""}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"