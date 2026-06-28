import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
os.environ["PADDLE_PDX_DISABLE_MKLDNN_MODEL_BL"] = "True"
os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "False"

from app.api.routes.blind_assist_routes import (
    router as blind_assist_router
)
from app.api.routes.currency_routes import (
    router as currency_router
)
from app.api.routes.face_routes import (
    router as face_router
)
from app.api.routes.object_detection_routes import (
    router as object_detection_router
)
from app.api.routes.ocr_routes import (
    router as ocr_router
)
from app.core.container import (
    container
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        container.initialize()
    except Exception as exc:
        print(f"FATAL: Container initialization failed: {exc}")
        raise

    yield

    print("Application shutdown")


app = FastAPI(
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {
        "status": "running",
        "service": "SEE BEYOND Backend"
    }
@app.get("/health")
async def health():
    return {
        "healthy": True
    }
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    face_router,
    prefix="/api/face",
    tags=["Face Recognition"]
)

app.include_router(
    object_detection_router,
    prefix="/api/object",
    tags=["Object Detection"]
)

app.include_router(
    blind_assist_router,
    prefix="/api/blind-assist",
    tags=["Blind Assist"]
)

app.include_router(
    ocr_router,
    prefix="/api/ocr",
    tags=["OCR"]
)

app.include_router(
    currency_router,
    prefix="/api/currency",
    tags=["Currency Detection"]
)
