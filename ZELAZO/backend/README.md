# Product Distribution System - Backend

Backend API for a comprehensive product distribution, sales management, and analytics platform built with FastAPI and Python.

## Quick Start Guide

**Launch backend in Docker/Podman with ngrok in 3 steps:**

1. **Get ngrok token** from https://dashboard.ngrok.com/get-started/your-authtoken

2. **Add token to `.env` file:**
   ```bash
   # Create .env from example
   cp .env.example .env

   # Add your ngrok token
   NGROK_AUTHTOKEN=your_token_here
   ```

3. **Run the startup script:**
   ```bash
   # Windows PowerShell
   .\start-podman-ngrok.ps1

   # Linux/Mac/Git Bash
   ./start-podman-ngrok.sh
   ```

**That's it!** You'll get a public HTTPS URL like `https://abc123.ngrok-free.app`

Access your API:
- Public API: `https://abc123.ngrok-free.app/docs`
- Local API: `http://localhost:8000/docs`
- ngrok Dashboard: `http://localhost:4040`

**Restart with new migrations/requirements:**
```bash
# Windows PowerShell
.\start-podman-ngrok.ps1 -Down
.\start-podman-ngrok.ps1 -Build

# Linux/Mac/Git Bash
./start-podman-ngrok.sh --down
./start-podman-ngrok.sh --build
```

This will rebuild containers with new dependencies and automatically run all database migrations.

---

## Features

- FastAPI-based REST API with automatic OpenAPI documentation
- PostgreSQL database with SQLAlchemy ORM
- Async/await support for high performance
- Docker containerization for easy deployment
- CORS middleware for frontend integration
- Health check endpoints
- Environment-based configuration
- Secure authentication ready

## Project Structure

```
backend/
├── app/
│   ├── api/              # API routes and endpoints
│   │   ├── health.py     # Health check endpoints
│   │   └── __init__.py
│   ├── core/             # Core application configuration
│   │   ├── config.py     # Settings and environment variables
│   │   └── __init__.py
│   ├── models/           # Database models
│   ├── services/         # Business logic and services
│   ├── utils/            # Utility functions and helpers
│   ├── main.py           # FastAPI application entry point
│   └── __init__.py
├── tests/                # Test files
├── .env.example          # Example environment variables
├── .gitignore
├── docker-compose.yml    # Podman/Docker Compose configuration
├── Dockerfile            # Container definition
├── requirements.txt      # Python dependencies
├── start-local.ps1       # PowerShell local development script
├── start-local.sh        # Bash local development script
├── start-podman.ps1      # PowerShell Podman/Docker script
└── start-podman.sh       # Bash Podman/Docker script
```

## Quick Start

### Prerequisites

**For Local Development:**
- Python 3.12+

**For Container Deployment:**
- Podman or Docker with Compose plugin

### Option 1: Local Development (Recommended for Development)

Run the application directly on your machine with hot reload enabled.

**Windows (PowerShell):**
```powershell
.\start-local.ps1
```

**Linux/Mac/Git Bash:**
```bash
./start-local.sh
```

This will:
- Create and activate a virtual environment
- Automatically install/update all dependencies
- Create `.env` from `.env.example` (if needed)
- Start the API server with hot reload at http://localhost:8000

### Option 2: Podman/Docker (Recommended for Production-like Testing)

Run the application in containers with PostgreSQL database.

**Windows (PowerShell):**
```powershell
# Start containers
.\start-podman.ps1

# Start with rebuild
.\start-podman.ps1 -Build

# View logs
.\start-podman.ps1 -Logs

# Stop containers
.\start-podman.ps1 -Down
```

**Linux/Mac/Git Bash:**
```bash
# Start containers
./start-podman.sh

# Start with rebuild
./start-podman.sh --build

# View logs
./start-podman.sh --logs

# Stop containers
./start-podman.sh --down
```

The scripts automatically detect and use either Podman or Docker. This will:
- Create `.env` from `.env.example` (if needed)
- Build container images
- Start PostgreSQL and the API server
- Make the API available at http://localhost:8000

### Option 3: Public URL with ngrok (Expose API Publicly)

Want to share your API or test with external services? Use ngrok to get a public HTTPS URL.

**Prerequisites:**
1. Install ngrok: https://ngrok.com/download
2. Get your token: https://dashboard.ngrok.com/get-started/your-authtoken
3. Add token to `.env`: `NGROK_AUTHTOKEN=your_token_here`

**Local Development with ngrok:**
```powershell
# Windows
.\start-with-ngrok.ps1

# Linux/Mac/Git Bash
./start-with-ngrok.sh
```

**Podman/Docker with ngrok:**
```powershell
# Windows
.\start-podman-ngrok.ps1

# Linux/Mac/Git Bash
./start-podman-ngrok.sh
```

**What you get:**
```
========================================
✓ ngrok tunnel established!
========================================

Public URL:  https://abc123.ngrok-free.app
Local URL:   http://localhost:8000
API Docs:    https://abc123.ngrok-free.app/docs
ngrok Web:   http://localhost:4040

========================================
```

**Features:**
- ✅ Automatic HTTPS encryption
- ✅ Public URL that works anywhere
- ✅ Request inspection at http://localhost:4040
- ✅ Great for webhook testing, mobile app development, or sharing demos

**Note:** The URL changes each time you restart (use ngrok paid plan for permanent URLs).

See [NGROK_SETUP.md](NGROK_SETUP.md) for detailed configuration options.

## Environment Configuration

Copy `.env.example` to `.env` and update the values:

```env
# Application
APP_NAME="Product Distribution System"
ENVIRONMENT=development
DEBUG=True

# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/product_distribution

# Security
SECRET_KEY=your-secret-key-here-change-in-production
```

## API Documentation

Once the server is running, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Available Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint

## Manual Podman/Docker Commands

If you prefer to use Podman or Docker directly:

```bash
# Using Podman
podman compose up -d          # Start containers
podman compose logs -f        # View logs
podman compose down           # Stop containers
podman compose up --build     # Rebuild and start
podman compose down -v        # Stop and remove volumes

# Using Docker (same commands)
docker compose up -d          # Start containers
docker compose logs -f        # View logs
docker compose down           # Stop containers
docker compose up --build     # Rebuild and start
docker compose down -v        # Stop and remove volumes
```

Note: The `docker-compose.yml` file is fully compatible with both Podman and Docker.

## Development

### Installing Dependencies

Dependencies are automatically installed when using the startup scripts. For manual installation:

```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# Install/update dependencies
pip install -r requirements.txt --upgrade
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
# Format code with black
black .

# Lint code with ruff
ruff check .
```

## Technology Stack

- **Framework**: FastAPI 0.115.5
- **Server**: Uvicorn with ASGI
- **Database**: PostgreSQL with SQLAlchemy (async)
- **Authentication**: JWT with python-jose
- **Data Processing**: Pandas, NumPy
- **Testing**: Pytest
- **Code Quality**: Black, Ruff

## Quick Reference

### All Startup Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `start-local` | Local development (localhost only) | `./start-local.sh` or `.\start-local.ps1` |
| `start-with-ngrok` | Local dev with public URL | `./start-with-ngrok.sh` or `.\start-with-ngrok.ps1` |
| `start-podman` | Containers (localhost only) | `./start-podman.sh` or `.\start-podman.ps1` |
| `start-podman-ngrok` | Containers with public URL | `./start-podman-ngrok.sh` or `.\start-podman-ngrok.ps1` |

### Common Commands

```bash
# Database migrations (automatic in all scripts)
alembic upgrade head              # Apply all migrations
alembic revision --autogenerate   # Create new migration
alembic downgrade -1              # Rollback last migration

# View ngrok URL manually
curl http://localhost:4040/api/tunnels   # Get tunnel info
# Or open: http://localhost:4040          # Web dashboard

# Container management
podman compose logs -f            # View logs (or docker)
podman compose ps                 # List containers
podman compose down -v            # Stop and remove all data

# Database connection (DBeaver/pgAdmin)
Host: localhost
Port: 5432
Database: product_distribution
Username: user
Password: password
```

### Important Files

- **[.env.example](.env.example)** - Environment configuration template
- **[DATABASE.md](DATABASE.md)** - Database management guide
- **[NGROK_SETUP.md](NGROK_SETUP.md)** - Public URL setup guide
- **[docker-compose.yml](docker-compose.yml)** - Standard container setup
- **[docker-compose-ngrok.yml](docker-compose-ngrok.yml)** - Container setup with ngrok

## Next Steps

1. Configure your `.env` file with proper credentials
2. **Optional:** Add ngrok token for public URL access
3. Add your database models in `app/models/`
4. Create API endpoints in `app/api/`
5. Implement business logic in `app/services/`
6. Write tests in `tests/`

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running (`./start-podman.sh` or local PostgreSQL)
- Check DATABASE_URL in `.env` matches your setup
- Verify credentials are correct

### ngrok Issues
- Make sure NGROK_AUTHTOKEN is set in `.env`
- Check ngrok is installed: `ngrok version`
- Visit http://localhost:4040 for tunnel status
- Free plan URLs change on each restart

### Migration Issues
- Check database is accessible
- Verify `alembic/versions/` has migration files
- Run manually: `alembic upgrade head`
- Reset if needed: `alembic downgrade base && alembic upgrade head`

## License

Proprietary - All rights reserved
