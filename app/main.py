from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes.users import router as users_router
from app.database import sessionmanager
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()

app = FastAPI(lifespan=lifespan, title=settings.project_name, docs_url="/api/docs")

@app.get("/")
async def root():
    return {"message": "Hello World"}


# Routers
app.include_router(users_router)

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)