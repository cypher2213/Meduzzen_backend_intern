import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.base_exception import BaseServiceError
from app.core.config import settings
from app.core.error_middleware import error_middleware
from app.routers.route_collection import router as api_routes

app = FastAPI()


@app.exception_handler(BaseServiceError)
async def base_service_error_handler(request, exc: BaseServiceError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.middleware("http")(error_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_routes)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.app.HOST,
        port=settings.app.PORT,
        reload=True,
    )
