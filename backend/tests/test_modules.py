import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from backend.app.policy_loader import PolicyLoader
from backend.app.violation_checker import ViolationChecker
from backend.app.enforcer import Enforcer
from backend.app.logger import GaaSLogger
from backend.app.schemas import ActionType, ViolationSeverity, EnforcementAction

class TestPolicyLoader:
    def setup_method(self):
        self.policy_loader = PolicyLoader()

    def test_save_and_load_policy(self):
        """Test saving and loading a policy."""
        policy_data = {
            "policy_id": "test_policy",
            "policy_name": "Test Policy",
            "policy_type": "access_control",
            "policy_content": {"rules": []},
            "version": "1.0.0",
            "effective_date": datetime.now().isoformat()
        }

        # Save policy
        success = self.policy_loader.save_policy(policy_data)
        assert success is True

        # Load policy
        loaded_policy = self.policy_loader.load_policy("test_policy")
        assert loaded_policy is not None
        assert loaded_policy["policy_id"] == "test_policy"

    def test_validate_policy_structure(self):
        """Test policy structure validation."""
        valid_policy = {
            "policy_id": "valid",
            "policy_name": "Valid Policy",
            "policy_type": "access_control",
            "policy_content": {},
            "version": "1.0.0"
        }

        invalid_policy = {
            "policy_id": "invalid"
            # Missing required fields
        }

        assert self.policy_loader._validate_policy_structure(valid_policy) is True
        assert self.policy_loader._validate_policy_structure(invalid_policy) is False

class TestViolationChecker:
    def setup_method(self):
        self.violation_checker = ViolationChecker()

    @patch('backend.app.violation_checker.policy_loader')
    def test_check_action_compliance_no_violations(self, mock_policy_loader):
        """Test action compliance check with no violations."""
        mock_policy_loader.get_all_policies.return_value = {}

        violations = self.violation_checker.check_action_compliance(
            "test_agent",
            ActionType.DATA_ACCESS,
            "read data",
            {}
        )

        assert len(violations) == 0

    @patch('backend.app.violation_checker.policy_loader')
    def test_check_action_compliance_with_violations(self, mock_policy_loader):
        """Test action compliance check with violations."""
        mock_policy = {
            "policy_001": {
                "policy_id": "policy_001",
                "policy_content": {
                    "agent_scope": ["*"],
                    "action_types": ["*"],
                    "rules": [
                        {
                            "type": "forbidden_action",
                            "patterns": ["delete"],
                            "violation_type": "forbidden_action",
                            "severity": "high",
                            "description": "Delete operations are forbidden"
                        }
                    ]
                }
            }
        }

        mock_policy_loader.get_all_policies.return_value = mock_policy
        mock_policy_loader.is_policy_active.return_value = True

        violations = self.violation_checker.check_action_compliance(
            "test_agent",
            ActionType.SYSTEM_MODIFICATION,
            "delete user data",
            {}
        )

        assert len(violations) > 0
        assert violations[0].severity == ViolationSeverity.HIGH

class TestEnforcer:
    def setup_method(self):
        self.enforcer = Enforcer()

    @patch('backend.app.enforcer.violation_checker')
    def test_make_enforcement_decision_allow(self, mock_violation_checker):
        """Test enforcement decision with no violations (allow)."""
        mock_violation_checker.check_action_compliance.return_value = []

        decision = self.enforcer.make_enforcement_decision(
            "test_agent",
            "read data",
            {}
        )

        assert decision.decision == EnforcementAction.ALLOW
        assert "No policy violations" in decision.reasoning

    @patch('backend.app.enforcer.violation_checker')
    def test_make_enforcement_decision_block(self, mock_violation_checker):
        """Test enforcement decision with high severity violations (block)."""
        from backend.app.schemas import ViolationDetail

        mock_violations = [
            ViolationDetail(
                policy_id="test_policy",
                violation_type="high_risk_action",
                severity=ViolationSeverity.HIGH,
                description="High risk action detected"
            )
        ]

        mock_violation_checker.check_action_compliance.return_value = mock_violations

        decision = self.enforcer.make_enforcement_decision(
            "test_agent",
            "risky action",
            {}
        )

        assert decision.decision == EnforcementAction.BLOCK
        assert len(decision.violations) == 1

class TestGaaSLogger:
    def setup_method(self):
        self.logger = GaaSLogger()

    def test_generate_log_id(self):
        """Test log ID generation."""
        log_id1 = self.logger.generate_log_id()
        log_id2 = self.logger.generate_log_id()

        assert log_id1 != log_id2
        assert log_id1.startswith("LOG_")
        assert log_id2.startswith("LOG_")

    def test_log_agent_registration(self):
        """Test agent registration logging."""
        # This should not raise any exceptions
        self.logger.log_agent_registration(
            "test_agent",
            {"name": "Test Agent"},
            True,
            "Success"
        )

    def test_get_violation_statistics(self):
        """Test violation statistics calculation."""
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()

        stats = self.logger.get_violation_statistics(start_date, end_date)

        assert "total_actions" in stats
        assert "total_violations" in stats
        assert "compliant_actions" in stats
        assert "compliance_rate" in stats
        assert "violation_types" in stats
