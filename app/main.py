from fastapi import FastAPI

app = FastAPI(title="Blog API")



@app.get("/hp")
async def get_health() -> dict:
    return {"message": "ok"}

