# Docker Setup Guide

This guide will help you run the Code KT Generator application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed (usually comes with Docker Desktop)

## Quick Start

### 1. Build and Start the Containers

```bash
docker compose up --build
```

> **Note**: Modern Docker uses `docker compose` (without hyphen). If you have an older version, use `docker-compose` instead.

This command will:
- Build the backend (Python/FastAPI) container
- Build the frontend (Next.js) container
- Start both services
- Set up networking between them

### 2. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 3. Stop the Containers

Press `Ctrl+C` in the terminal, or run:

```bash
docker compose down
```

## Common Commands

### Start in detached mode (background)
```bash
docker compose up -d
```

### View logs
```bash
# All services
docker compose logs -f

# Just backend
docker compose logs -f backend

# Just frontend
docker compose logs -f frontend
```

### Rebuild after code changes
```bash
docker compose up --build
```

### Stop and remove containers, networks, and volumes
```bash
docker compose down -v
```

### Access container shell
```bash
# Backend
docker exec -it kt-generator-backend sh

# Frontend
docker exec -it kt-generator-frontend sh
```

## Environment Variables

The `.env` file in the root directory is automatically loaded by Docker Compose. Make sure it contains:

```
ANTHROPIC_API_KEY=your-api-key-here
```

## Data Persistence

The following data is persisted using Docker volumes:
- **backend-data**: SQLite database files
- **backend-chroma**: ChromaDB vector embeddings

This means your data will persist even when containers are stopped or restarted.

## Troubleshooting

### Port already in use
If you get an error about ports 3000 or 8000 being in use, either:
1. Stop the other application using that port
2. Modify the ports in `docker-compose.yml`:
   ```yaml
   ports:
     - "3001:3000"  # Use port 3001 on host instead
   ```

### Database locked error
If you see database locked errors, restart the containers:
```bash
docker compose restart backend
```

### Frontend not connecting to backend
Make sure both containers are on the same network. Check with:
```bash
docker network inspect kt-generator_kt-network
```

## Development Mode

The current setup runs in development mode with hot-reload enabled:
- Backend auto-reloads when Python files change
- Frontend auto-reloads when JS/JSX files change

## Production Deployment

For production, you should:
1. Update the frontend Dockerfile to build the Next.js app
2. Use `NODE_ENV=production`
3. Remove volume mounts for code
4. Use a reverse proxy like Nginx
5. Set up proper secrets management

## Notes

- The backend runs on `uvicorn` with auto-reload
- The frontend runs with `npm run dev`
- Both containers share a Docker network for communication
- Source code is mounted as volumes for development
