import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Import your application's specific components
from core.database import Base, engine
from routes.pdf import pdf_router
from routes.tech_interview import tech_ws_router
# --- NEW: Import the router for serving the HTML page ---
from routes.interview_page import page_router

# --- Lifespan Manager (for startup and shutdown events) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting InterviewAI API...")
    # Initialize the database
    Base.metadata.create_all(bind=engine)
    print("InterviewAI API started successfully!")
    yield
    print("Shutting down InterviewAI API...")

# --- FastAPI App Initialization ---
app = FastAPI(
    title="InterviewAI API",
    description="AI-powered interview practice system",
    version="1.0.0",
    lifespan=lifespan
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Routers ---
# Your existing routers for the WebSocket and PDF upload
app.include_router(tech_ws_router, prefix="/ws")
app.include_router(pdf_router, prefix="/pdf")
# --- NEW: Add the router that serves the /interview/{id} page ---
app.include_router(page_router)

# --- Static File Serving ---
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", include_in_schema=False)
async def read_upload_page():
    """Serves the main index.html (the upload page)."""
    return FileResponse(os.path.join(static_dir, "index.html"))

# --- Server Execution ---
if __name__ == "__main__":
    import uvicorn
    print("--- Starting Server ---")
    print("Access the application at: http://127.0.0.1:8000")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )