import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .api import users, quizzes, sectors, admin, goals, feedback
from .models.models_hierarchical import Base
from .database import engine
from .db_init import auto_populate_if_empty

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create all tables using hierarchical models
Base.metadata.create_all(bind=engine)

# Note: Auto-population now runs in entrypoint.sh after DB is ready
# This allows proper sequencing: DB ready → populate → start server
# If running locally without Docker, uncomment the line below:
# auto_populate_if_empty()

app = FastAPI(
    title="Future Work Readiness API",
    description="API for the Future of Work Readiness Platform",
    version="1.0.0"
)

# CORS - Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://localhost:3004", "http://localhost:3005", "http://localhost:3006", "http://localhost:3007", "http://localhost:3008", "http://localhost:3009", "http://localhost:3010", "http://localhost:3011", "http://localhost:3012", "http://localhost:3013", "http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(quizzes.router, prefix="/api", tags=["Quizzes"])
app.include_router(sectors.router, prefix="/api", tags=["Sectors"])
app.include_router(admin.router, prefix="/api", tags=["Admin"])
app.include_router(goals.router, prefix="/api", tags=["Goals"])
app.include_router(feedback.router, prefix="/api", tags=["Feedback"])

@app.get("/")
def root():
    return {
        "message": "Welcome to Future Work Readiness API",
        "docs": "Visit /docs for API documentation"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/welcome")
def welcome(request: Request):
    """
    Welcome endpoint that logs requests and returns a welcome message
    """
    logger.info(f"Request received: {request.method} {request.url.path}")
    return {"message": "Welcome to the Future Work Readiness API"}
