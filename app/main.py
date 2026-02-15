from fastapi import FastAPI


from app.routers import auth

app = FastAPI(title="Blog API")


app.include_router(auth.router)

@app.get("/hp")
async def get_health() -> dict:
    return {"message": "ok"}

