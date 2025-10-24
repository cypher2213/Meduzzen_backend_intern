from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health
from app.core.config import get_settings
import uvicorn

app = FastAPI()
settings = get_settings()
origins = settings.origins

app.add_middleware(
  CORSMiddleware,
  allow_origins = origins,
  allow_credentials = True,
  allow_methods = ["*"],
  allow_headers = ["*"],
)


app.include_router(health.router, tags=["Health routes"])

if __name__ == "__main__":
    uvicorn.run(
      "app.main:app",
      host=settings.host,
      port=settings.port,
      reload=True,
    )