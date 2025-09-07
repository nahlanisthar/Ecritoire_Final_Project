from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.auth import router as auth_router
from controllers.samples import router as samples_router
from controllers.generation import router as generation_router
import uvicorn

app = FastAPI(
    title="Écritoire API",
    description="AI-powered personalized writing assistant that learns your style",
    version="2.1.0"
)

# Enabling CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(samples_router)
app.include_router(generation_router)

@app.get("/")
async def root():
    return {
        "message": "Écritoire API v2.1 - Your Personal Writing AI is running! ✍️",
        "features": [
            "User authentication",
            "Upload writing samples",
            "Build personal style profile",
            "Generate content in your voice",
            "Learn from your feedback"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ecritoire-personal-ai",
        "version": "2.1.0",
        "features_active": ["authentication", "style_learning", "content_generation", "feedback_learning"]
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)