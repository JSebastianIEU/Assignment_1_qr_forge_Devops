from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "QR Forge API running!"}
