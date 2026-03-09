---
title: Smart Energy RL Optimization
emoji: ⚡
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 7860
---

# Smart Energy RL Consumption Optimization

This is the backend API for the Smart Energy RL Optimization project.
It implements a patent-grade Reinforcement Learning environment for building hvac optimization.

## How to use
This Space hosts the FastAPI backend. You should connect your Vercel frontend to this URL.

### API Endpoints
- `/api/simulate`: Run hourly energy simulations
- `/api/status`: Check system health and loaded models
- `/api/upload-dataset`: Upload custom building CSVs
