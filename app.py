#!/usr/bin/env python3
"""
Smart Energy RL Platform — Main Application Entry Point
"""
import os
import uvicorn
from backend.main import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)