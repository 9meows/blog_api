from fastapi import FastAPI


from app.routers import auth, users, posts, comments

app = FastAPI(title="Blog API")


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)


@app.get("/hp")
async def get_health() -> dict:
    return {"message": "ok"}

