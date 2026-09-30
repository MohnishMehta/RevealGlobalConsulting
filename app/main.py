from fastapi import FastAPI

from app.routes.imports import router as imports_router


app = FastAPI()

app.include_router(imports_router)


@app.get("/")
def read_root():
    return {"message": "Reveal Global Consulting API"}