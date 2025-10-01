import pytest
import json
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from backend.app.main import app
from backend.app.schemas import AgentStatus, ActionType, EnforcementAction, ViolationSeverity

client = TestClient(app)

class TestAgentRegistration:
    def test_register_agent_success(self):
        """Test successful agent registration."""
        agent_data = {
            "agent_id": "test_agent_001",
            "name": "Test Agent",
            "capabilities": ["data_processing", "analysis"],
            "agent_type": "analytical",
            "contact_info": "test@example.com"
        }

        response = client.post("/register_agent", json=agent_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["agent_id"] == "test_agent_001"
        assert data["status"] == "active"
        assert "registration_timestamp" in data

    def test_register_duplicate_agent(self):
        """Test registration of duplicate agent ID."""
        agent_data = {
            "agent_id": "duplicate_agent",
            "name": "Duplicate Agent",
            "capabilities": ["testing"],
            "agent_type": "test"
        }

        # Register first time
        response1 = client.post("/register_agent", json=agent_data)
        assert response1.status_code == 200

        # Try to register again
        response2 = client.post("/register_agent", json=agent_data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]

    def test_register_agent_invalid_data(self):
        """Test agent registration with invalid data."""
        # Empty name
        agent_data = {
            "agent_id": "invalid_agent_001",
            "name": "",
            "capabilities": ["testing"],
            "agent_type": "test"
        }

        response = client.post("/register_agent", json=agent_data)
        assert response.status_code == 400
        assert "cannot be empty" in response.json()["detail"]

        # No capabilities
        agent_data = {
            "agent_id": "invalid_agent_002",
            "name": "Invalid Agent",
            "capabilities": [],
            "agent_type": "test"
        }

        response = client.post("/register_agent", json=agent_data)
        assert response.status_code == 400
        assert "at least one capability" in response.json()["detail"]

class TestActionLogSubmission:
    def setup_method(self):
        """Setup test agent for action log tests."""
        agent_data = {
            "agent_id": "action_test_agent",
            "name": "Action Test Agent",
            "capabilities": ["data_access"],
            "agent_type": "test"
        }
        client.post("/register_agent", json=agent_data)

    def test_submit_action_log_success(self):
        """Test successful action log submission."""
        action_data = {
            "agent_id": "action_test_agent",
            "action_type": "data_access",
            "action_description": "Reading user data",
            "timestamp": datetime.now().isoformat(),
            "context": {"resource": "user_database"},
            "resource_accessed": "user_table"
        }

        response = client.post("/submit_action_log", json=action_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "log_id" in data
        assert data["message"] == "Action log submitted successfully"

    def test_submit_action_log_unregistered_agent(self):
        """Test action log submission for unregistered agent."""
        action_data = {
            "agent_id": "unregistered_agent",
            "action_type": "data_access",
            "action_description": "Attempting access",
            "timestamp": datetime.now().isoformat(),
            "context": {}
        }

        response = client.post("/submit_action_log", json=action_data)
        assert response.status_code == 404
        assert "not registered" in response.json()["detail"]

class TestEnforcementDecision:
    def setup_method(self):
        """Setup test agent for enforcement decision tests."""
        agent_data = {
            "agent_id": "enforcement_test_agent",
            "name": "Enforcement Test Agent",
            "capabilities": ["system_modification"],
            "agent_type": "test"
        }
        client.post("/register_agent", json=agent_data)

    def test_get_enforcement_decision_success(self):
        """Test successful enforcement decision retrieval."""
        params = {
            "agent_id": "enforcement_test_agent",
            "proposed_action": "read user data",
            "context": json.dumps({"approved": True})
        }

        response = client.get("/enforcement_decision", params=params)
        assert response.status_code == 200

        data = response.json()
        assert "decision" in data
        assert "reasoning" in data
        assert "timestamp" in data
        assert data["agent_id"] == "enforcement_test_agent"

    def test_get_enforcement_decision_unregistered_agent(self):
        """Test enforcement decision for unregistered agent."""
        params = {
            "agent_id": "unregistered_enforcement_agent",
            "proposed_action": "test action",
            "context": "{}"
        }

        response = client.get("/enforcement_decision", params=params)
        assert response.status_code == 404
        assert "not registered" in response.json()["detail"]

    def test_get_enforcement_decision_invalid_context(self):
        """Test enforcement decision with invalid JSON context."""
        params = {
            "agent_id": "enforcement_test_agent",
            "proposed_action": "test action",
            "context": "invalid json"
        }

        response = client.get("/enforcement_decision", params=params)
        assert response.status_code == 400
        assert "Invalid JSON format" in response.json()["detail"]

class TestPolicyUpload:
    def test_upload_policy_success(self):
        """Test successful policy upload."""
        policy_data = {
            "policy_id": "test_policy_001",
            "policy_name": "Test Access Policy",
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
            "effective_date": datetime.now().isoformat(),
            "expiry_date": (datetime.now() + timedelta(days=365)).isoformat()
        }

        response = client.post("/upload_policy", json=policy_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["policy_id"] == "test_policy_001"
        assert data["version"] == "1.0.0"

    def test_upload_policy_invalid_data(self):
        """Test policy upload with invalid data."""
        policy_data = {
            "policy_id": "invalid_policy",
            "policy_name": "",  # Empty name
            "policy_type": "access_control",
            "policy_content": {},
            "version": "1.0.0",
            "effective_date": datetime.now().isoformat()
        }

        response = client.post("/upload_policy", json=policy_data)
        assert response.status_code == 200  # Still returns 200 but with validation errors

        data = response.json()
        assert data["success"] is False
        assert len(data["validation_errors"]) > 0

class TestComplianceReport:
    def setup_method(self):
        """Setup test data for compliance report tests."""
        # Register test agent
        agent_data = {
            "agent_id": "compliance_test_agent",
            "name": "Compliance Test Agent",
            "capabilities": ["reporting"],
            "agent_type": "test"
        }
        client.post("/register_agent", json=agent_data)

        # Submit some action logs
        action_data = {
            "agent_id": "compliance_test_agent",
            "action_type": "data_access",
            "action_description": "Test action for compliance",
            "timestamp": datetime.now().isoformat(),
            "context": {}
        }
        client.post("/submit_action_log", json=action_data)

    def test_get_compliance_report_success(self):
        """Test successful compliance report generation."""
        start_date = (datetime.now() - timedelta(days=7)).isoformat()
        end_date = datetime.now().isoformat()

        params = {
            "start_date": start_date,
            "end_date": end_date,
            "report_type": "summary",
            "include_violations": True
        }

        response = client.get("/compliance_report", params=params)
        assert response.status_code == 200

        data = response.json()
        assert "report_id" in data
        assert "metrics" in data
        assert "generated_at" in data
        assert data["period_start"] is not None
        assert data["period_end"] is not None

    def test_get_compliance_report_invalid_dates(self):
        """Test compliance report with invalid date range."""
        start_date = datetime.now().isoformat()
        end_date = (datetime.now() - timedelta(days=1)).isoformat()  # End before start

        params = {
            "start_date": start_date,
            "end_date": end_date
        }

        response = client.get("/compliance_report", params=params)
        assert response.status_code == 400
        assert "Start date must be before end date" in response.json()["detail"]

    def test_get_compliance_report_invalid_date_format(self):
        """Test compliance report with invalid date format."""
        params = {
            "start_date": "invalid-date",
            "end_date": "also-invalid"
        }

        response = client.get("/compliance_report", params=params)
        assert response.status_code == 400
        assert "Invalid date format" in response.json()["detail"]

class TestHealthAndRoot:
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
        assert len(data["endpoints"]) == 5

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "registered_agents" in data
        assert "active_policies" in data

# Integration tests
class TestIntegrationWorkflow:
    def test_complete_workflow(self):
        """Test complete workflow from agent registration to compliance report."""
        # 1. Register agent
        agent_data = {
            "agent_id": "workflow_test_agent",
            "name": "Workflow Test Agent",
            "capabilities": ["full_workflow"],
            "agent_type": "integration_test"
        }

        reg_response = client.post("/register_agent", json=agent_data)
        assert reg_response.status_code == 200

        # 2. Upload a policy
        policy_data = {
            "policy_id": "workflow_test_policy",
            "policy_name": "Workflow Test Policy",
            "policy_type": "compliance",
            "policy_content": {"rules": []},
            "version": "1.0.0",
            "effective_date": datetime.now().isoformat()
        }

        policy_response = client.post("/upload_policy", json=policy_data)
        assert policy_response.status_code == 200

        # 3. Submit action log
        action_data = {
            "agent_id": "workflow_test_agent",
            "action_type": "data_access",
            "action_description": "Workflow test action",
            "timestamp": datetime.now().isoformat(),
            "context": {}
        }

        action_response = client.post("/submit_action_log", json=action_data)
        assert action_response.status_code == 200

        # 4. Get enforcement decision
        params = {
            "agent_id": "workflow_test_agent",
            "proposed_action": "workflow test decision",
            "context": "{}"
        }

        decision_response = client.get("/enforcement_decision", params=params)
        assert decision_response.status_code == 200

        # 5. Generate compliance report
        report_params = {
            "start_date": (datetime.now() - timedelta(hours=1)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "agent_id": "workflow_test_agent"
        }

        report_response = client.get("/compliance_report", params=report_params)
        assert report_response.status_code == 200

        # Verify all steps completed successfully
        assert all([
            reg_response.json()["success"],
            policy_response.json()["success"],
            action_response.json()["success"],
            "decision" in decision_response.json(),
            "report_id" in report_response.json()
        ])
