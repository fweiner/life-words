"""Main FastAPI application."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.core.error_logger import log_error

# Create FastAPI app
app = FastAPI(
    title="Parrot Software Treatment API",
    description="Backend API for cognitive treatment applications",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions, log them, and return a clean 500."""
    try:
        body = None
        if request.method in ("POST", "PUT", "PATCH"):
            try:
                body = await request.json()
            except Exception:
                pass

        query_params = dict(request.query_params) if request.query_params else None

        log_error(
            error=exc,
            source="unhandled",
            endpoint=str(request.url.path),
            http_method=request.method,
            request_body=body,
            query_params=query_params,
            status_code=500,
        )
    except Exception:
        pass  # Handler itself must never crash

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Parrot Software Treatment API",
        "version": "1.0.0",
        "status": "online",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


# Import and include routers
from app.routers import auth, treatments, results, life_words, invites, profile, items, messaging

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
app.include_router(treatments.router, prefix="/api/treatments", tags=["treatments"])
app.include_router(results.router, prefix="/api/results", tags=["results"])
app.include_router(life_words.router, prefix="/api/life-words", tags=["life-words"])
app.include_router(invites.router, prefix="/api/life-words", tags=["invites"])
app.include_router(items.router, prefix="/api/life-words/items", tags=["items"])
app.include_router(messaging.router, prefix="/api/life-words/messaging", tags=["messaging"])

from app.routers import life_words_questions
app.include_router(life_words_questions.router, prefix="/api/life-words", tags=["life-words-questions"])

from app.routers import life_words_information
app.include_router(life_words_information.router, prefix="/api/life-words", tags=["life-words-information"])

from app.routers import speech
app.include_router(speech.router, prefix="/api/speech", tags=["speech"])

from app.routers import matching
app.include_router(matching.router, prefix="/api/matching", tags=["matching"])

from app.routers import admin
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

from app.routers import stripe
app.include_router(stripe.router, prefix="/api/stripe", tags=["stripe"])
