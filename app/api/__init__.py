from fastapi import APIRouter
from fastapi import FastAPI
from .api_manager import router as manager_router
from .api_sd import router as sd_router
from .api_auth import router as auth_router

app = FastAPI()


@app.get("/")
def health_check_view():
    return {"status": "ok"}


api_router = APIRouter()
# router注入
api_router.include_router(sd_router, prefix="/sd", tags=["sd"])
api_router.include_router(manager_router, prefix="/manager", tags=["manager"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

app.include_router(api_router, prefix="/api")
