from fastapi import FastAPI

app = FastAPI(title="IARA System")


@app.get("/")
def root():
    return {"message": "IARA System API is running"}
