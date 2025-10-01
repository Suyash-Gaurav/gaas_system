# GaaS System User Guide

## Overview

This user guide provides step-by-step instructions for using the Governance-as-a-Service (GaaS) system. Whether you're an administrator setting up policies, a developer integrating agents, or an analyst reviewing compliance reports, this guide will help you effectively use the GaaS system.

## Getting Started

### Prerequisites

Before using the GaaS system, ensure you have:

1. **System Installation**: Follow the [Installation Guide](installation_guide.md)
2. **Backend Running**: The GaaS backend server must be running
3. **Network Access**: Ensure network connectivity to the GaaS API
4. **Required Permissions**: Appropriate access rights for your use case

### Quick Start Checklist

- [ ] GaaS backend server is running (`http://localhost:8000`)
- [ ] API documentation is accessible (`http://localhost:8000/docs`)
- [ ] Health check passes (`http://localhost:8000/health`)
- [ ] You have the necessary client libraries or tools

## User Roles and Workflows

### 1. System Administrator

**Responsibilities:**
- System configuration and maintenance
- Policy management and updates
- User access control
- System monitoring and troubleshooting

**Primary Workflows:**
- [Policy Management](#policy-management)
- [System Monitoring](#system-monitoring)
- [Compliance Reporting](#compliance-reporting)

### 2. Agent Developer

**Responsibilities:**
- Agent registration and configuration
- API integration
- Action logging implementation
- Enforcement decision handling

**Primary Workflows:**
- [Agent Registration](#agent-registration)
- [API Integration](#api-integration)
- [Action Submission](#action-submission)

### 3. Compliance Analyst

**Responsibilities:**
- Compliance monitoring
- Report generation and analysis
- Policy effectiveness assessment
- Risk analysis

**Primary Workflows:**
- [Compliance Reporting](#compliance-reporting)
- [Performance Analysis](#performance-analysis)
- [Risk Assessment](#risk-assessment)

## Core Workflows

### Agent Registration

#### Step 1: Prepare Agent Information

Gather the following information about your agent:

```json
{
  "agent_id": "unique_identifier",
  "name": "Human-readable name",
  "capabilities": ["list", "of", "capabilities"],
  "agent_type": "agent_category",
  "contact_info": "contact@example.com"
}
```

**Agent Types:**
- `compliant`: Always follows policies
- `non_compliant`: May violate policies
- `mixed_behavior`: Variable compliance
- `adaptive_learning`: Learns from enforcement decisions

#### Step 2: Register the Agent

**Using cURL:**
```bash
curl -X POST "http://localhost:8000/register_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my_agent_001",
    "name": "My Data Analysis Agent",
    "capabilities": ["data_analysis", "reporting"],
    "agent_type": "compliant",
    "contact_info": "admin@mycompany.com"
  }'
```

**Using Python:**
```python
import requests

agent_data = {
    "agent_id": "my_agent_001",
    "name": "My Data Analysis Agent",
    "capabilities": ["data_analysis", "reporting"],
    "agent_type": "compliant",
    "contact_info": "admin@mycompany.com"
}

response = requests.post(
    "http://localhost:8000/register_agent",
    json=agent_data
)

if response.status_code == 200:
    result = response.json()
    print(f"Agent registered: {result['agent_id']}")
    print(f"Status: {result['status']}")
else:
    print(f"Registration failed: {response.text}")
```

#### Step 3: Verify Registration

Check the registration was successful:

```bash
curl "http://localhost:8000/health"
```

Look for your agent in the `registered_agents` count.

### Action Submission

#### Step 1: Prepare Action Data

Before submitting an action, prepare the action information:

```json
{
  "agent_id": "my_agent_001",
  "action_type": "data_access",
  "action_description": "Query customer database for monthly report",
  "timestamp": "2025-06-22T19:30:00.000Z",
  "context": {
    "priority": "normal",
    "user_initiated": true,
    "department": "analytics"
  },
  "resource_accessed": "customer_database"
}
```

**Action Types:**
- `data_access`: Data retrieval operations
- `system_modification`: System changes
- `user_interaction`: User interface actions
- `external_api_call`: External service calls

#### Step 2: Submit Action Log

**Using cURL:**
```bash
curl -X POST "http://localhost:8000/submit_action_log" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my_agent_001",
    "action_type": "data_access",
    "action_description": "Query customer database for monthly report",
    "timestamp": "2025-06-22T19:30:00.000Z",
    "context": {
      "priority": "normal",
      "user_initiated": true
    },
    "resource_accessed": "customer_database"
  }'
```

**Using Python:**
```python
from datetime import datetime
import requests

action_data = {
    "agent_id": "my_agent_001",
    "action_type": "data_access",
    "action_description": "Query customer database for monthly report",
    "timestamp": datetime.now().isoformat(),
    "context": {
        "priority": "normal",
        "user_initiated": True
    },
    "resource_accessed": "customer_database"
}

response = requests.post(
    "http://localhost:8000/submit_action_log",
    json=action_data
)

result = response.json()
print(f"Log ID: {result['log_id']}")
print(f"Violations: {result['violations_detected']}")
```

#### Step 3: Handle Response

Process the response to understand compliance status:

```python
if result['success']:
    if result['violations_detected']:
        print("⚠️  Violations detected:")
        for violation in result['violations_detected']:
            print(f"  - {violation}")
    else:
        print("✅ Action compliant")
else:
    print("❌ Action submission failed")
```

### Enforcement Decision Requests

#### Step 1: Request Enforcement Decision

Before performing an action, request an enforcement decision:

**Using cURL:**
```bash
curl -G "http://localhost:8000/enforcement_decision" \
  --data-urlencode "agent_id=my_agent_001" \
  --data-urlencode "proposed_action=Access sensitive customer data" \
  --data-urlencode 'context={"priority":"high","user_initiated":false}'
```

**Using Python:**
```python
import json
import requests

params = {
    "agent_id": "my_agent_001",
    "proposed_action": "Access sensitive customer data",
    "context": json.dumps({
        "priority": "high",
        "user_initiated": False
    })
}

response = requests.get(
    "http://localhost:8000/enforcement_decision",
    params=params
)

decision = response.json()
print(f"Decision: {decision['decision']}")
print(f"Reasoning: {decision['reasoning']}")
```

#### Step 2: Handle Enforcement Decision

Process the enforcement decision appropriately:

```python
decision_result = decision['decision']

if decision_result == 'allow':
    print("✅ Action allowed - proceed")
    # Execute the action
elif decision_result == 'warn':
    print("⚠️  Action allowed with warning")
    # Log warning and proceed with caution
elif decision_result == 'block':
    print("❌ Action blocked - do not proceed")
    # Handle blocked action
elif decision_result == 'suspend':
    print("🚫 Agent suspended - stop all operations")
    # Handle agent suspension
```

#### Step 3: Review Violations

If violations are detected, review them:

```python
if decision['violations']:
    print("Policy violations detected:")
    for violation in decision['violations']:
        print(f"  Policy: {violation['policy_id']}")
        print(f"  Type: {violation['violation_type']}")
        print(f"  Severity: {violation['severity']}")
        print(f"  Description: {violation['description']}")
```

### Policy Management

#### Step 1: Prepare Policy Data

Create a policy definition:

```json
{
  "policy_id": "DATA_ACCESS_001",
  "policy_name": "Customer Data Access Policy",
  "policy_type": "data_governance",
  "policy_content": {
    "rules": [
      {
        "condition": "resource_type == 'customer_data'",
        "action": "require_authorization",
        "level": "supervisor"
      }
    ],
    "exceptions": ["emergency_access"],
    "audit_required": true
  },
  "version": "1.0.0",
  "effective_date": "2025-06-22T00:00:00.000Z",
  "expiry_date": "2026-06-22T00:00:00.000Z"
}
```

**Policy Types:**
- `access_control`: Access permissions and restrictions
- `data_governance`: Data handling policies
- `compliance`: Regulatory compliance rules
- `security`: Security protocols

#### Step 2: Upload Policy

**Using cURL:**
```bash
curl -X POST "http://localhost:8000/upload_policy" \
  -H "Content-Type: application/json" \
  -d @policy.json
```

**Using Python:**
```python
policy_data = {
    "policy_id": "DATA_ACCESS_001",
    "policy_name": "Customer Data Access Policy",
    "policy_type": "data_governance",
    "policy_content": {
        "rules": [
            {
                "condition": "resource_type == 'customer_data'",
                "action": "require_authorization",
                "level": "supervisor"
            }
        ],
        "exceptions": ["emergency_access"],
        "audit_required": True
    },
    "version": "1.0.0",
    "effective_date": "2025-06-22T00:00:00.000Z"
}

response = requests.post(
    "http://localhost:8000/upload_policy",
    json=policy_data
)

result = response.json()
if result['success']:
    print(f"✅ Policy uploaded: {result['policy_id']} v{result['version']}")
else:
    print("❌ Policy upload failed:")
    for error in result['validation_errors']:
        print(f"  - {error}")
```

#### Step 3: Verify Policy Upload

Check that the policy is active:

```bash
curl "http://localhost:8000/health"
```

The `active_policies` count should include your new policy.

### Compliance Reporting

#### Step 1: Generate Compliance Report

Request a compliance report for a specific time period:

**Using cURL:**
```bash
curl -G "http://localhost:8000/compliance_report" \
  --data-urlencode "start_date=2025-06-01T00:00:00Z" \
  --data-urlencode "end_date=2025-06-22T23:59:59Z" \
  --data-urlencode "include_violations=true"
```

**Using Python:**
```python
from datetime import datetime, timedelta

# Generate report for last 30 days
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

params = {
    "start_date": start_date.isoformat() + "Z",
    "end_date": end_date.isoformat() + "Z",
    "include_violations": "true"
}

response = requests.get(
    "http://localhost:8000/compliance_report",
    params=params
)

report = response.json()
print(f"Report ID: {report['report_id']}")
print(f"Period: {report['period_start']} to {report['period_end']}")
```

#### Step 2: Analyze Report Metrics

Review the compliance metrics:

```python
metrics = report['metrics']

print(f"Total Actions: {metrics['total_actions']}")
print(f"Compliant Actions: {metrics['compliant_actions']}")
print(f"Violations: {metrics['violations']}")
print(f"Compliance Rate: {metrics['compliance_rate']:.2%}")

print("\nMost Common Violations:")
for violation_type in metrics['most_common_violations']:
    print(f"  - {violation_type}")
```

#### Step 3: Review Recommendations

Act on system recommendations:

```python
if report['recommendations']:
    print("\n📋 System Recommendations:")
    for recommendation in report['recommendations']:
        print(f"  • {recommendation}")
```

### Performance Analysis

#### Step 1: Run Simulation

First, generate performance data using the client simulation:

```bash
cd client
python run_simulation.py
```

This creates simulation data in the `simulation_results` directory.

#### Step 2: Run Performance Analysis

Analyze the simulation results:

```bash
cd evaluation
python run_evaluation.py
```

#### Step 3: Review Analysis Results

The analysis generates:

- **Plots**: 12 visualization types in the `plots/` directory
- **Reports**: Detailed analysis reports in the `reports/` directory
- **Metrics**: Performance statistics and recommendations

**Key Visualizations:**
1. Response Time Distribution
2. Response Time Over Time
3. Compliance Rate by Agent Type
4. Enforcement Decision Breakdown
5. Actions Per Minute Over Time
6. Violation Count Distribution
7. Agent Performance Scatter Plot
8. Response Time by Endpoint
9. Compliance Rate Trends
10. System Load Analysis
11. Response Time Percentiles
12. System Activity Summary

## Best Practices

### Agent Development

1. **Always Register First**: Register agents before any other operations
2. **Handle Errors Gracefully**: Implement proper error handling for all API calls
3. **Respect Enforcement Decisions**: Follow the guidance provided by enforcement decisions
4. **Provide Rich Context**: Include detailed context information in action submissions
5. **Monitor Compliance**: Regularly check compliance status and address violations

### Policy Management

1. **Version Control**: Always version your policies and track changes
2. **Test Policies**: Test policy changes in a development environment first
3. **Clear Documentation**: Document policy rules and their business rationale
4. **Regular Reviews**: Periodically review and update policies
5. **Gradual Rollout**: Implement policy changes gradually to minimize disruption

### System Administration

1. **Monitor Performance**: Regularly check system health and performance metrics
2. **Backup Policies**: Maintain backups of all policy configurations
3. **Log Analysis**: Regularly review system logs for issues and patterns
4. **Capacity Planning**: Monitor system load and plan for scaling needs
5. **Security Updates**: Keep the system updated with security patches

### Compliance Management

1. **Regular Reporting**: Generate compliance reports on a regular schedule
2. **Trend Analysis**: Monitor compliance trends over time
3. **Proactive Remediation**: Address compliance issues before they become problems
4. **Documentation**: Maintain detailed records of compliance activities
5. **Stakeholder Communication**: Keep stakeholders informed of compliance status

## Troubleshooting

### Common Issues

#### Agent Registration Fails

**Problem**: Agent registration returns 400 error

**Solutions:**
1. Check agent_id uniqueness
2. Verify all required fields are provided
3. Ensure agent_id meets length requirements (3-50 characters)
4. Validate capabilities list is not empty

#### Action Submission Fails

**Problem**: Action log submission returns 404 or 403 error

**Solutions:**
1. Verify agent is registered
2. Check agent status is 'active'
3. Validate timestamp format (ISO 8601)
4. Ensure action_type is valid enum value

#### Enforcement Decision Errors

**Problem**: Enforcement decision request fails

**Solutions:**
1. Verify agent is registered and active
2. Check context parameter is valid JSON
3. Ensure proposed_action is not empty
4. Validate URL encoding for special characters

#### Policy Upload Issues

**Problem**: Policy upload fails validation

**Solutions:**
1. Check policy_name is not empty
2. Verify policy_content is not empty
3. Validate effective_date is not too far in future
4. Ensure expiry_date is after effective_date

### Debug Mode

Enable debug logging for troubleshooting:

```bash
export GAAS_DEBUG=true
```

Or modify the `.env` file:

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

### Getting Help

1. **Check Logs**: Review system logs for error details
2. **API Documentation**: Consult the interactive API docs at `/docs`
3. **Health Check**: Verify system status at `/health`
4. **Troubleshooting Guide**: Review the [Troubleshooting Guide](troubleshooting.md)

## Advanced Usage

### Batch Operations

#### Bulk Agent Registration

```python
agents = [
    {"agent_id": f"agent_{i:03d}", "name": f"Agent {i}", 
     "capabilities": ["data_analysis"], "agent_type": "compliant"}
    for i in range(1, 11)
]

for agent in agents:
    response = requests.post("http://localhost:8000/register_agent", json=agent)
    print(f"Registered: {agent['agent_id']}")
```

#### Batch Action Submission

```python
actions = [
    {"agent_id": f"agent_{i:03d}", "action_type": "data_access",
     "action_description": f"Action {i}", "timestamp": datetime.now().isoformat()}
    for i in range(1, 11)
]

for action in actions:
    response = requests.post("http://localhost:8000/submit_action_log", json=action)
    result = response.json()
    print(f"Action {action['agent_id']}: {result['success']}")
```

### Custom Integration

#### Webhook Integration

```python
import requests
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook/gaas', methods=['POST'])
def handle_gaas_webhook():
    data = request.json
    
    # Process GaaS event
    if data['event_type'] == 'violation_detected':
        handle_violation(data)
    elif data['event_type'] == 'agent_suspended':
        handle_suspension(data)
    
    return {'status': 'processed'}

def handle_violation(data):
    # Custom violation handling logic
    print(f"Violation detected for agent {data['agent_id']}")
    
def handle_suspension(data):
    # Custom suspension handling logic
    print(f"Agent {data['agent_id']} suspended")
```

#### Custom Metrics Collection

```python
class CustomMetricsCollector:
    def __init__(self, gaas_url):
        self.gaas_url = gaas_url
        self.metrics = []
    
    def collect_metrics(self):
        # Collect custom business metrics
        response = requests.get(f"{self.gaas_url}/compliance_report",
                              params={"start_date": "2025-06-01T00:00:00Z",
                                     "end_date": "2025-06-22T23:59:59Z"})
        
        report = response.json()
        
        # Calculate custom metrics
        custom_metrics = {
            'business_impact_score': self.calculate_business_impact(report),
            'risk_score': self.calculate_risk_score(report),
            'efficiency_score': self.calculate_efficiency_score(report)
        }
        
        return custom_metrics
```

## Integration Examples

### Python Client Library

```python
class GaaSClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def register_agent(self, agent_data):
        response = self.session.post(f"{self.base_url}/register_agent", 
                                   json=agent_data)
        return response.json()
    
    def submit_action(self, action_data):
        response = self.session.post(f"{self.base_url}/submit_action_log",
                                   json=action_data)
        return response.json()
    
    def get_enforcement_decision(self, agent_id, proposed_action, context=None):
        params = {
            "agent_id": agent_id,
            "proposed_action": proposed_action,
            "context": json.dumps(context or {})
        }
        response = self.session.get(f"{self.base_url}/enforcement_decision",
                                  params=params)
        return response.json()

# Usage
client = GaaSClient()
result = client.register_agent({
    "agent_id": "my_agent",
    "name": "My Agent",
    "capabilities": ["data_analysis"],
    "agent_type": "compliant"
})
```

### JavaScript Integration

```javascript
class GaaSClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async registerAgent(agentData) {
        const response = await fetch(`${this.baseUrl}/register_agent`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(agentData)
        });
        return response.json();
    }
    
    async submitAction(actionData) {
        const response = await fetch(`${this.baseUrl}/submit_action_log`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(actionData)
        });
        return response.json();
    }
    
    async getEnforcementDecision(agentId, proposedAction, context = {}) {
        const params = new URLSearchParams({
            agent_id: agentId,
            proposed_action: proposedAction,
            context: JSON.stringify(context)
        });
        
        const response = await fetch(`${this.baseUrl}/enforcement_decision?${params}`);
        return response.json();
    }
}

// Usage
const client = new GaaSClient();
const result = await client.registerAgent({
    agent_id: 'js_agent',
    name: 'JavaScript Agent',
    capabilities: ['web_interaction'],
    agent_type: 'mixed_behavior'
});
```

---

This user guide provides comprehensive instructions for effectively using the GaaS system across different user roles and use cases. For additional technical details, refer to the [API Documentation](api_documentation.md) and [System Architecture](architecture.md) documents.