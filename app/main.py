from fastapi import FastAPI

app = FastAPI()



@app.get("/hp")
async def get_health() -> dict:
    return {"message": "ok"}

