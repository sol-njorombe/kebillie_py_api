from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router

app = FastAPI(
    title="Ke Bills API",
    openapi_url="/api/v1/openapi.json"
)

# Set up CORS middleware
# Replace ["*"] with your frontend domain(s) in production, e.g., ["http://localhost:3000"]
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Welcome to Ke Bills API. Visit /docs for the API documentation."}
