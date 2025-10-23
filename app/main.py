from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from app.routers import health

load_dotenv()

app = FastAPI()
origins = os.getenv("ORIGINS","http://localhost:3000").split(',')

app.add_middleware(
  CORSMiddleware,
  allow_origins = origins,
  allow_credentials = True,
  allow_methods = ["*"],
  allow_headers = ["*"],
)


app.include_router(health.router, tags=["Health routes"])