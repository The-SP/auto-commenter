from app.logger import init_logger
from app.routes import router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = init_logger(__name__)


app = FastAPI(title="Reddit Auto Commenter API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
