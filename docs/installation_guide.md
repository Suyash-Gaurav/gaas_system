# GaaS System Installation Guide

## Overview

This guide provides step-by-step instructions for installing and setting up the Governance-as-a-Service (GaaS) system. The system consists of three main components: Backend API, Client Simulation, and Evaluation Framework.

## System Requirements

### Hardware Requirements
- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Internet connection for package installation

### Software Requirements
- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **Git**: For cloning the repository (optional)

## Installation Methods

### Method 1: Complete System Installation (Recommended)

This method installs all components of the GaaS system.

#### Step 1: Clone or Download the System

```bash
# If using Git
git clone <repository-url>
cd gaas_system

# Or download and extract the system files
```

#### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv gaas_env

# Activate virtual environment
# On Linux/macOS:
source gaas_env/bin/activate

# On Windows:
gaas_env\Scripts\activate
```

#### Step 3: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
cd ..
```

**Backend Dependencies:**
- fastapi==0.109.2
- uvicorn[standard]==0.34.3
- pydantic==2.11.0
- pydantic-settings==2.1.0
- python-dotenv==1.0.1
- pytest==8.4.0
- pytest-asyncio==0.21.1
- httpx==0.25.2
- python-multipart==0.0.6

#### Step 4: Install Client Dependencies

```bash
cd client
pip install -r requirements.txt
cd ..
```

**Client Dependencies:**
- requests>=2.31.0
- pydantic>=2.0.0
- python-dateutil>=2.8.2

#### Step 5: Install Evaluation Dependencies

```bash
cd evaluation
pip install -r requirements.txt
cd ..
```

**Evaluation Dependencies:**
- pandas>=2.0.0
- matplotlib>=3.7.0
- seaborn>=0.12.0
- numpy>=1.24.0

### Method 2: Component-Specific Installation

Install only the components you need.

#### Backend Only

```bash
cd backend
python -m venv backend_env
source backend_env/bin/activate  # Linux/macOS
# backend_env\Scripts\activate  # Windows
pip install -r requirements.txt
```

#### Client Simulation Only

```bash
cd client
python -m venv client_env
source client_env/bin/activate  # Linux/macOS
# client_env\Scripts\activate  # Windows
pip install -r requirements.txt
```

#### Evaluation Framework Only

```bash
cd evaluation
python -m venv eval_env
source eval_env/bin/activate  # Linux/macOS
# eval_env\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Configuration Setup

### Backend Configuration

#### Step 1: Environment Variables

Create a `.env` file in the `backend` directory:

```bash
cd backend
touch .env  # Linux/macOS
# type nul > .env  # Windows
```

Add the following configuration:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=gaas_backend.log

# Policy Configuration
POLICY_DIR=./policies
DEFAULT_POLICY_VERSION=1.0.0

# Database Configuration (if using external database)
# DATABASE_URL=sqlite:///./gaas.db
```

#### Step 2: Policy Directory Setup

```bash
# Ensure policy directory exists
mkdir -p backend/policies
```

### Client Configuration

Create configuration file in the `client` directory:

```bash
cd client
```

The client uses the `config.py` file for configuration. Default settings should work for local development.

### Evaluation Configuration

The evaluation framework uses default settings that work with the standard directory structure.

## Running the System

### Starting the Backend Server

#### Method 1: Using the Start Script

```bash
cd backend
python start_server.py
```

#### Method 2: Using Uvicorn Directly

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Method 3: Using Python Module

```bash
cd backend
python -m app.main
```

**Verify Backend is Running:**
- Open browser to `http://localhost:8000`
- Check API documentation at `http://localhost:8000/docs`
- Health check at `http://localhost:8000/health`

### Running Client Simulation

```bash
cd client
python run_simulation.py
```

**Simulation Options:**
- Default: Runs with 15 agents for 100 simulation steps
- Custom: Modify `run_simulation.py` for different configurations

### Running Evaluation

```bash
cd evaluation
python run_evaluation.py
```

This will:
- Load simulation data from the client results
- Generate performance analysis
- Create visualization plots
- Save reports to the `reports` directory

## Verification Steps

### 1. Backend Verification

```bash
# Test API endpoints
curl http://localhost:8000/
curl http://localhost:8000/health

# Expected response for root endpoint:
# {
#   "message": "Governance-as-a-Service (GaaS) Backend",
#   "version": "1.0.0",
#   "endpoints": [...]
# }
```

### 2. Client Verification

```bash
cd client
python -c "from client_interface import GaaSClient; print('Client import successful')"
```

### 3. Evaluation Verification

```bash
cd evaluation
python -c "from performance_analyzer import GaaSPerformanceAnalyzer; print('Evaluation import successful')"
```

## Docker Installation (Alternative)

### Using Docker Compose

If you prefer containerized deployment:

```bash
# Build and start all services
docker-compose up --build

# Start in background
docker-compose up -d --build

# Stop services
docker-compose down
```

### Backend Docker Only

```bash
cd backend
docker build -t gaas-backend .
docker run -p 8000:8000 gaas-backend
```

## Troubleshooting

### Common Installation Issues

#### 1. Python Version Issues

```bash
# Check Python version
python --version

# If Python 3.8+ not available, install it:
# Ubuntu/Debian:
sudo apt update
sudo apt install python3.8 python3.8-venv python3.8-dev

# macOS (using Homebrew):
brew install python@3.8

# Windows: Download from python.org
```

#### 2. Virtual Environment Issues

```bash
# If venv module not available
pip install virtualenv
virtualenv gaas_env

# Activate the environment
source gaas_env/bin/activate  # Linux/macOS
gaas_env\Scripts\activate     # Windows
```

#### 3. Package Installation Issues

```bash
# Upgrade pip first
pip install --upgrade pip

# Install packages with verbose output
pip install -r requirements.txt -v

# If specific package fails, install individually
pip install fastapi==0.109.2
```

#### 4. Port Already in Use

```bash
# Check what's using port 8000
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# Use different port
uvicorn app.main:app --port 8001
```

#### 5. Permission Issues

```bash
# Linux/macOS: Fix permissions
chmod +x start_server.py
sudo chown -R $USER:$USER gaas_system/

# Windows: Run as Administrator if needed
```

### Dependency Conflicts

If you encounter dependency conflicts:

```bash
# Create fresh virtual environment
deactivate
rm -rf gaas_env
python -m venv gaas_env
source gaas_env/bin/activate

# Install components one by one
cd backend && pip install -r requirements.txt
cd ../client && pip install -r requirements.txt
cd ../evaluation && pip install -r requirements.txt
```

### Performance Issues

#### Memory Usage

```bash
# Monitor memory usage
top -p $(pgrep -f "python.*main")  # Linux
Activity Monitor  # macOS
Task Manager  # Windows
```

#### Slow Response Times

1. Check system resources
2. Reduce simulation parameters
3. Enable debug logging to identify bottlenecks

### Logging and Debugging

#### Enable Debug Mode

```bash
# Set environment variable
export GAAS_DEBUG=true

# Or modify .env file
echo "DEBUG=true" >> backend/.env
```

#### Check Log Files

```bash
# Backend logs
tail -f backend/gaas_backend.log

# Client logs
tail -f client/client_simulation.log

# Evaluation logs
tail -f evaluation/evaluation.log
```

## Development Setup

For development work:

```bash
# Install development dependencies
pip install pytest pytest-asyncio black flake8 mypy

# Run tests
cd backend && python -m pytest tests/
cd ../client && python -m pytest  # if tests exist
cd ../evaluation && python -m pytest  # if tests exist

# Code formatting
black backend/app/
black client/
black evaluation/
```

## Production Deployment

### Security Considerations

1. **Environment Variables**: Use secure environment variable management
2. **CORS Configuration**: Restrict CORS origins in production
3. **Authentication**: Implement proper authentication mechanisms
4. **HTTPS**: Use HTTPS in production deployments
5. **Database**: Use production-grade database instead of in-memory storage

### Performance Optimization

1. **Database**: Configure proper database with connection pooling
2. **Caching**: Implement Redis or similar for caching
3. **Load Balancing**: Use nginx or similar for load balancing
4. **Monitoring**: Set up proper monitoring and alerting

### Example Production Configuration

```env
# Production .env file
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=WARNING

# Database
DATABASE_URL=postgresql://user:pass@localhost/gaas_db

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=https://yourdomain.com

# Performance
WORKERS=4
MAX_CONNECTIONS=100
```

## Next Steps

After successful installation:

1. Review the [API Documentation](api_documentation.md)
2. Follow the [User Guide](user_guide.md)
3. Explore the [System Architecture](architecture.md)
4. Try the [Multi-Agent Simulation](simulation_guide.md)

## Support

If you encounter issues not covered in this guide:

1. Check the [Troubleshooting Guide](troubleshooting.md)
2. Review system logs for error messages
3. Verify all dependencies are correctly installed
4. Ensure proper Python version and virtual environment setup

---

**Installation Complete!** 🎉

Your GaaS system should now be ready for use. Start with the backend server, then run client simulations to see the system in action.