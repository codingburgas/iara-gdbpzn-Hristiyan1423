from fastapi import FastAPI
from app import models
from app.routers import ships, permits

app = FastAPI(title="IARA System")

app.include_router(ships.router)
app.include_router(permits.router)


@app.get("/")
def root():
    return {"message": "IARA System API is running"}