import pytest


async def create_post(auth_client):
    response = await auth_client.post("/api/posts/", json={
        "title": "Test post title here",
        "content": "a" * 100,
        "status": "published",
        "tags": []
    })
    return response.json()["slug"]

@pytest.mark.asyncio
async def test_create_comment_authorized(auth_client):
    slug_from_created_post = await create_post(auth_client=auth_client)
    
    comment_response = await auth_client.post(f"/api/posts/{slug_from_created_post}/comments", json={"text": "a"*30, "parent_id":None})
    
    assert comment_response.status_code == 201
    assert comment_response.json()["text"] == "a"*30
    


@pytest.mark.asyncio
async def test_create_comment_unauthorized(auth_client):
    slug_from_created_post = await create_post(auth_client=auth_client)

    comment_response = await auth_client.post(f"/api/posts/{slug_from_created_post}/comments",
                                              json={"text": "a"*30, "parent_id":None},
                                              headers={"Authorization": ""})
    assert comment_response.status_code == 401
    assert comment_response.json()["detail"] == "Not authenticated"

@pytest.mark.asyncio
async def test_delete_comment_by_author(auth_client):
    slug_from_created_post = await create_post(auth_client=auth_client)

    comment_response = await auth_client.post(f"/api/posts/{slug_from_created_post}/comments", json={"text": "a"*30, "parent_id":None})
    
    id_comment_from_reponse = comment_response.json()["id"]
    
    reponse_delete = await auth_client.delete(f"/api/comments/{id_comment_from_reponse}")
    
    assert reponse_delete.status_code == 204 
    

@pytest.mark.asyncio
async def test_delete_comment_unauthorized(auth_client):
    slug_from_created_post = await create_post(auth_client=auth_client)

    comment_response = await auth_client.post(f"/api/posts/{slug_from_created_post}/comments", json={"text": "a"*30, "parent_id":None})
    
    id_comment_from_reponse = comment_response.json()["id"]

    reponse_delete = await auth_client.delete(f"/api/comments/{id_comment_from_reponse}", headers = {"Authorization": ""})
    
    assert reponse_delete.status_code == 401
    assert reponse_delete.json()["detail"] == "Not authenticated"