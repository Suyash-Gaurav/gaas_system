# GaaS API Documentation

## Overview

The Governance-as-a-Service (GaaS) API provides a comprehensive RESTful interface for managing AI agent governance, policy enforcement, and compliance monitoring. The API is built using FastAPI and provides automatic OpenAPI documentation.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. In production deployments, implement appropriate authentication mechanisms based on your security requirements.

## API Endpoints

### 1. Root Endpoint

**GET /**

Returns basic API information and available endpoints.

**Response:**
```json
{
  "message": "Governance-as-a-Service (GaaS) Backend",
  "version": "1.0.0",
  "endpoints": [
    "/register_agent",
    "/submit_action_log", 
    "/enforcement_decision",
    "/upload_policy",
    "/compliance_report"
  ]
}
```

### 2. Agent Registration

**POST /register_agent**

Register a new agent in the GaaS system.

**Request Body:**
```json
{
  "agent_id": "string (3-50 characters)",
  "name": "string (1-100 characters)",
  "capabilities": ["string"],
  "agent_type": "string",
  "contact_info": "string (optional)"
}
```

**Request Example:**
```json
{
  "agent_id": "agent_001",
  "name": "Data Analysis Agent",
  "capabilities": ["data_analysis", "reporting", "basic_operations"],
  "agent_type": "compliant",
  "contact_info": "admin@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "agent_id": "agent_001",
  "status": "active",
  "registration_timestamp": "2025-06-22T19:30:00.000Z",
  "message": "Agent registered successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Agent already exists or validation errors
- `500 Internal Server Error`: Server-side processing error

### 3. Action Log Submission

**POST /submit_action_log**

Submit an action log from an agent for compliance checking.

**Request Body:**
```json
{
  "agent_id": "string",
  "action_type": "data_access | system_modification | user_interaction | external_api_call",
  "action_description": "string",
  "timestamp": "ISO 8601 datetime",
  "context": {},
  "resource_accessed": "string (optional)"
}
```

**Request Example:**
```json
{
  "agent_id": "agent_001",
  "action_type": "data_access",
  "action_description": "Query customer database for analytics report",
  "timestamp": "2025-06-22T19:30:00.000Z",
  "context": {
    "priority": "normal",
    "user_initiated": true,
    "department": "analytics"
  },
  "resource_accessed": "customer_db"
}
```

**Response:**
```json
{
  "success": true,
  "log_id": "LOG_20250622193000_abc123",
  "message": "Action log submitted successfully",
  "violations_detected": [
    "POLICY_001: Unauthorized data access detected"
  ]
}
```

**Error Responses:**
- `404 Not Found`: Agent not registered
- `403 Forbidden`: Agent not active
- `500 Internal Server Error`: Server-side processing error

### 4. Enforcement Decision

**GET /enforcement_decision**

Get an enforcement decision for a proposed agent action.

**Query Parameters:**
- `agent_id` (required): ID of the requesting agent
- `proposed_action` (required): Description of the proposed action
- `context` (optional): JSON string containing action context

**Request Example:**
```
GET /enforcement_decision?agent_id=agent_001&proposed_action=Access%20sensitive%20database&context={"priority":"high","user_initiated":false}
```

**Response:**
```json
{
  "decision": "block",
  "agent_id": "agent_001",
  "reasoning": "Action violates data access policy - insufficient permissions for sensitive database",
  "violations": [
    {
      "policy_id": "POLICY_DATA_001",
      "violation_type": "unauthorized_access",
      "severity": "high",
      "description": "Attempt to access sensitive database without proper authorization"
    }
  ],
  "timestamp": "2025-06-22T19:30:00.000Z",
  "additional_constraints": {
    "required_approval": "supervisor",
    "alternative_actions": ["access_public_database", "request_permission"]
  }
}
```

**Enforcement Actions:**
- `allow`: Action is permitted
- `warn`: Action is permitted with warning
- `block`: Action is not permitted
- `suspend`: Agent should be suspended

**Error Responses:**
- `404 Not Found`: Agent not registered
- `400 Bad Request`: Invalid context JSON format
- `500 Internal Server Error`: Server-side processing error

### 5. Policy Upload

**POST /upload_policy**

Upload or update a governance policy.

**Request Body:**
```json
{
  "policy_id": "string",
  "policy_name": "string",
  "policy_type": "access_control | data_governance | compliance | security",
  "policy_content": {},
  "version": "string",
  "effective_date": "ISO 8601 datetime",
  "expiry_date": "ISO 8601 datetime (optional)"
}
```

**Request Example:**
```json
{
  "policy_id": "POLICY_DATA_001",
  "policy_name": "Sensitive Data Access Policy",
  "policy_type": "data_governance",
  "policy_content": {
    "rules": [
      {
        "condition": "resource_type == 'sensitive_database'",
        "action": "require_authorization",
        "level": "supervisor"
      }
    ],
    "exceptions": ["emergency_access"],
    "audit_required": true
  },
  "version": "1.2.0",
  "effective_date": "2025-06-22T00:00:00.000Z",
  "expiry_date": "2026-06-22T00:00:00.000Z"
}
```

**Response:**
```json
{
  "success": true,
  "policy_id": "POLICY_DATA_001",
  "version": "1.2.0",
  "upload_timestamp": "2025-06-22T19:30:00.000Z",
  "message": "Policy uploaded successfully",
  "validation_errors": []
}
```

**Validation Rules:**
- Policy name cannot be empty
- Policy content cannot be empty
- Effective date cannot be more than 1 year in the future
- Expiry date must be after effective date

**Error Responses:**
- `400 Bad Request`: Validation errors
- `500 Internal Server Error`: Server-side processing error

### 6. Compliance Report

**GET /compliance_report**

Generate a compliance report for a specified time period.

**Query Parameters:**
- `start_date` (required): Start date in ISO 8601 format
- `end_date` (required): End date in ISO 8601 format
- `agent_id` (optional): Specific agent to report on
- `report_type` (optional): Type of report (default: "summary")
- `include_violations` (optional): Include violation details (default: true)

**Request Example:**
```
GET /compliance_report?start_date=2025-06-01T00:00:00Z&end_date=2025-06-22T23:59:59Z&agent_id=agent_001&include_violations=true
```

**Response:**
```json
{
  "report_id": "RPT_20250622193000_def456",
  "agent_id": "agent_001",
  "period_start": "2025-06-01T00:00:00.000Z",
  "period_end": "2025-06-22T23:59:59.000Z",
  "generated_at": "2025-06-22T19:30:00.000Z",
  "metrics": {
    "total_actions": 150,
    "compliant_actions": 128,
    "violations": 22,
    "compliance_rate": 0.853,
    "most_common_violations": [
      "unauthorized_access",
      "policy_violation",
      "resource_misuse"
    ]
  },
  "detailed_violations": [
    {
      "policy_id": "POLICY_DATA_001",
      "violation_type": "unauthorized_access",
      "severity": "high",
      "description": "Attempted access to restricted resource"
    }
  ],
  "recommendations": [
    "Consider reviewing and updating policies",
    "Focus on addressing unauthorized_access violations"
  ]
}
```

**Error Responses:**
- `400 Bad Request`: Invalid date format or date range
- `404 Not Found`: Agent not found (if agent_id specified)
- `500 Internal Server Error`: Server-side processing error

### 7. Health Check

**GET /health**

Check system health and status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-22T19:30:00.000Z",
  "registered_agents": 15,
  "active_policies": 8
}
```

## Data Models

### Agent Status Enum
- `active`: Agent is operational
- `inactive`: Agent is not operational
- `suspended`: Agent has been suspended due to violations

### Action Type Enum
- `data_access`: Data retrieval or query operations
- `system_modification`: System configuration or state changes
- `user_interaction`: User interface or communication actions
- `external_api_call`: External service or API interactions

### Violation Severity Enum
- `low`: Minor policy deviation
- `medium`: Moderate policy violation
- `high`: Serious policy violation
- `critical`: Severe policy violation requiring immediate attention

### Policy Type Enum
- `access_control`: Access permissions and restrictions
- `data_governance`: Data handling and privacy policies
- `compliance`: Regulatory compliance requirements
- `security`: Security protocols and restrictions

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": true,
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

## Rate Limiting

Currently, no rate limiting is implemented. For production deployments, consider implementing appropriate rate limiting based on your requirements.

## CORS Configuration

The API is configured to accept requests from all origins (`*`). In production, configure CORS settings appropriately for your security requirements.

## OpenAPI Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Code Examples

### Python Client Example

```python
import requests
import json
from datetime import datetime

# Base URL
base_url = "http://localhost:8000"

# Register an agent
agent_data = {
    "agent_id": "example_agent",
    "name": "Example Agent",
    "capabilities": ["data_analysis", "reporting"],
    "agent_type": "compliant",
    "contact_info": "admin@example.com"
}

response = requests.post(f"{base_url}/register_agent", json=agent_data)
print(f"Registration: {response.json()}")

# Submit an action log
action_data = {
    "agent_id": "example_agent",
    "action_type": "data_access",
    "action_description": "Generate monthly report",
    "timestamp": datetime.now().isoformat(),
    "context": {"priority": "normal"},
    "resource_accessed": "reports_db"
}

response = requests.post(f"{base_url}/submit_action_log", json=action_data)
print(f"Action Log: {response.json()}")

# Get enforcement decision
params = {
    "agent_id": "example_agent",
    "proposed_action": "Access customer database",
    "context": json.dumps({"priority": "high"})
}

response = requests.get(f"{base_url}/enforcement_decision", params=params)
print(f"Enforcement Decision: {response.json()}")
```

### JavaScript Client Example

```javascript
const baseUrl = 'http://localhost:8000';

// Register an agent
const agentData = {
  agent_id: 'js_agent',
  name: 'JavaScript Agent',
  capabilities: ['web_interaction', 'data_processing'],
  agent_type: 'mixed_behavior',
  contact_info: 'dev@example.com'
};

fetch(`${baseUrl}/register_agent`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(agentData)
})
.then(response => response.json())
.then(data => console.log('Registration:', data));

// Get compliance report
const reportParams = new URLSearchParams({
  start_date: '2025-06-01T00:00:00Z',
  end_date: '2025-06-22T23:59:59Z',
  include_violations: 'true'
});

fetch(`${baseUrl}/compliance_report?${reportParams}`)
.then(response => response.json())
.then(data => console.log('Compliance Report:', data));
```

## Best Practices

1. **Agent Registration**: Always register agents before attempting other operations
2. **Error Handling**: Implement proper error handling for all API calls
3. **Timestamp Format**: Use ISO 8601 format for all datetime fields
4. **Context Information**: Provide rich context information for better policy enforcement
5. **Regular Compliance Checks**: Generate regular compliance reports for monitoring
6. **Policy Management**: Keep policies up-to-date and properly versioned

## Troubleshooting

### Common Issues

1. **Agent Not Found (404)**: Ensure the agent is registered before submitting actions
2. **Invalid JSON (400)**: Verify JSON format and required fields
3. **Date Format Errors**: Use ISO 8601 format for all datetime fields
4. **Connection Errors**: Verify the server is running and accessible

### Debug Information

Enable debug logging by setting the environment variable:
```bash
export GAAS_DEBUG=true
```

This will provide detailed logging information for troubleshooting API issues.