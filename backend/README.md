# Governance-as-a-Service (GaaS) Backend

A comprehensive FastAPI-based backend system that provides governance services to AI agents through RESTful APIs.

## Features

- **Agent Registration**: Register and manage AI agents in the system
- **Action Logging**: Accept and process action logs from agents
- **Policy Management**: Upload and manage governance policies
- **Enforcement Decisions**: Provide real-time enforcement decisions
- **Compliance Reporting**: Generate detailed compliance reports
- **Violation Detection**: Automatic policy violation checking

## Project Structure

```
backend/
├── app/                     # Main application code
│   ├── main.py             # FastAPI application with all endpoints
│   ├── schemas.py          # Pydantic data models
│   ├── policy_loader.py    # Policy management module
│   ├── violation_checker.py # Violation detection module
│   ├── enforcer.py         # Enforcement logic module
│   └── logger.py           # System logging module
├── config/                 # Configuration files
│   ├── settings.py         # Application settings
│   └── .env               # Environment variables
├── tests/                  # Unit tests
│   ├── test_main.py       # API endpoint tests
│   ├── test_modules.py    # Core module tests
│   └── conftest.py        # Test configuration
└── requirements.txt        # Python dependencies
```

## API Endpoints

### 1. Agent Registration
- **POST** `/register_agent`
- Register new agents in the system
- **Request**: Agent details (ID, name, capabilities, type)
- **Response**: Registration confirmation with status

### 2. Action Log Submission
- **POST** `/submit_action_log`
- Accept action logs from agents
- **Request**: Action details (agent ID, type, description, context)
- **Response**: Log ID and violation detection results

### 3. Enforcement Decision
- **GET** `/enforcement_decision`
- Provide enforcement decisions to agents
- **Parameters**: agent_id, proposed_action, context
- **Response**: Decision (allow/warn/block/suspend) with reasoning

### 4. Policy Upload
- **POST** `/upload_policy`
- Upload or update governance policies
- **Request**: Policy details (ID, name, type, content, version)
- **Response**: Upload confirmation with validation results

### 5. Compliance Report
- **GET** `/compliance_report`
- Generate compliance reports
- **Parameters**: date range, agent_id (optional), report type
- **Response**: Detailed compliance metrics and violations

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration
Copy and configure the environment file:
```bash
cp config/.env.example config/.env
```

Edit `config/.env` with your specific settings:
```env
APP_NAME=Governance-as-a-Service Backend
DEBUG=True
HOST=0.0.0.0
PORT=8000
SECRET_KEY=your-secret-key-here
LOG_LEVEL=INFO
POLICY_STORAGE_PATH=./policies
```

### 3. Create Required Directories
```bash
mkdir -p policies logs
```

### 4. Run the Application

#### Development Mode
```bash
# From the backend directory
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Production Mode
```bash
# From the backend directory
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. Verify Installation
Open your browser and navigate to:
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Running Tests

### Run All Tests
```bash
# From the backend directory
python -m pytest tests/ -v
```

### Run Specific Test Files
```bash
python -m pytest tests/test_main.py -v
python -m pytest tests/test_modules.py -v
```

### Run Tests with Coverage
```bash
pip install pytest-cov
python -m pytest tests/ --cov=app --cov-report=html
```

## Usage Examples

### 1. Register an Agent
```bash
curl -X POST "http://localhost:8000/register_agent" \
     -H "Content-Type: application/json" \
     -d '{
       "agent_id": "agent_001",
       "name": "Data Processing Agent",
       "capabilities": ["data_processing", "analysis"],
       "agent_type": "analytical",
       "contact_info": "admin@example.com"
     }'
```

### 2. Submit Action Log
```bash
curl -X POST "http://localhost:8000/submit_action_log" \
     -H "Content-Type: application/json" \
     -d '{
       "agent_id": "agent_001",
       "action_type": "data_access",
       "action_description": "Reading user database",
       "timestamp": "2024-01-01T10:00:00",
       "context": {"database": "users", "table": "profiles"}
     }'
```

### 3. Get Enforcement Decision
```bash
curl -X GET "http://localhost:8000/enforcement_decision?agent_id=agent_001&proposed_action=delete%20user%20data&context=%7B%7D"
```

### 4. Upload Policy
```bash
curl -X POST "http://localhost:8000/upload_policy" \
     -H "Content-Type: application/json" \
     -d '{
       "policy_id": "access_policy_001",
       "policy_name": "Data Access Policy",
       "policy_type": "access_control",
       "policy_content": {
         "rules": [
           {
             "type": "time_restriction",
             "allowed_hours": [9, 10, 11, 12, 13, 14, 15, 16, 17]
           }
         ]
       },
       "version": "1.0.0",
       "effective_date": "2024-01-01T00:00:00"
     }'
```

### 5. Generate Compliance Report
```bash
curl -X GET "http://localhost:8000/compliance_report?start_date=2024-01-01T00:00:00&end_date=2024-01-31T23:59:59&include_violations=true"
```

## Configuration

### Environment Variables
- `APP_NAME`: Application name
- `DEBUG`: Enable debug mode (True/False)
- `HOST`: Server host address
- `PORT`: Server port number
- `SECRET_KEY`: Secret key for security
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `POLICY_STORAGE_PATH`: Directory for policy storage
- `MAX_POLICY_SIZE_MB`: Maximum policy file size

### Policy Configuration
Policies are stored as JSON files in the configured policy storage directory. Each policy must include:
- `policy_id`: Unique identifier
- `policy_name`: Human-readable name
- `policy_type`: Type of policy (access_control, data_governance, compliance, security)
- `policy_content`: Policy rules and conditions
- `version`: Policy version
- `effective_date`: When policy becomes active
- `expiry_date`: When policy expires (optional)

## Architecture

### Core Components

1. **FastAPI Application** (`main.py`)
   - RESTful API endpoints
   - Request/response handling
   - Error management

2. **Policy Loader** (`policy_loader.py`)
   - Policy storage and retrieval
   - Policy validation
   - Cache management

3. **Violation Checker** (`violation_checker.py`)
   - Policy compliance checking
   - Rule evaluation
   - Violation detection

4. **Enforcer** (`enforcer.py`)
   - Enforcement decision logic
   - Action classification
   - Constraint generation

5. **Logger** (`logger.py`)
   - System event logging
   - Action log management
   - Compliance metrics

### Data Flow
1. Agent registers with the system
2. Agent submits action logs
3. System checks for policy violations
4. Enforcement decisions are made based on violations
5. Compliance reports are generated from logged data

## Security Considerations

- Use strong secret keys in production
- Configure CORS appropriately for your environment
- Implement authentication/authorization as needed
- Regularly update dependencies
- Monitor logs for security events

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're running from the correct directory
   - Check Python path configuration

2. **Port Already in Use**
   - Change the port in configuration
   - Kill existing processes using the port

3. **Permission Errors**
   - Check file/directory permissions
   - Ensure policy storage directory is writable

4. **Policy Validation Errors**
   - Verify policy JSON structure
   - Check required fields are present

### Logs
Check application logs for detailed error information:
- Default log file: `gaas_backend.log`
- Configure log level in environment variables

## Contributing

1. Follow Python PEP 8 style guidelines
2. Add tests for new functionality
3. Update documentation for API changes
4. Ensure all tests pass before submitting

## License

This project is part of the Governance-as-a-Service system implementation.
