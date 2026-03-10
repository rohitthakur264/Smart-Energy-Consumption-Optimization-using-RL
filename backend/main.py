"""
Smart Energy RL Platform — FastAPI Backend
Serves the RL simulation engine and trained models via REST API.
"""
import os
import matplotlib
matplotlib.use('Agg') # Prevent font cache and GUI issues
import sys

# Add project root to path for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

app = FastAPI(
    title="Smart Energy RL Optimization API",
    description="IEEE Transactions Level Building Energy Management System — REST API",
    version="2.0.0",
)

print("Starting Smart Energy API...")

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from backend.routes.simulation import router as simulation_router
app.include_router(simulation_router)

@app.get("/api-info")
def root():
    return {
        "name": "Smart Energy RL Optimization API",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": ["/api/simulate", "/api/evaluate", "/api/compare", "/api/status"],
    }

@app.get("/health")
def health_check():
    """Lightweight health check for Render."""
    return {"status": "ok"}

# Serve React frontend assets
dist_assets = os.path.join(PROJECT_ROOT, "frontend", "dist", "assets")
if os.path.exists(dist_assets):
    app.mount("/assets", StaticFiles(directory=dist_assets), name="assets")

# Catch-all to serve index.html for React Router
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    dist_dir = os.path.join(PROJECT_ROOT, "frontend", "dist")
    
    # If frontend build is missing (e.g. Vercel deployment), redirect root to API docs
    if not os.path.exists(dist_dir) or not os.path.exists(os.path.join(dist_dir, "index.html")):
        if full_path == "" or full_path == "/":
            return RedirectResponse(url="/docs")
        return {"error": "Frontend build not found. API is running. Visit /docs for documentation."}

    file_path = os.path.join(dist_dir, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    index_path = os.path.join(dist_dir, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
        
    return {"error": "File not found"}
