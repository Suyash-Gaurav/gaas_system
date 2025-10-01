from typing import Dict, List, Any, Optional
from datetime import datetime
from app.policy_loader import policy_loader
from app.schemas import ViolationDetail, ViolationSeverity, ActionType

class ViolationChecker:
    def __init__(self):
        self.policy_loader = policy_loader

    def check_action_compliance(self, agent_id: str, action_type: ActionType, 
                              action_description: str, context: Dict[str, Any]) -> List[ViolationDetail]:
        """Check if an action complies with all applicable policies."""
        violations = []

        # Get all active policies
        all_policies = self.policy_loader.get_all_policies()

        for policy_id, policy in all_policies.items():
            if not self.policy_loader.is_policy_active(policy_id):
                continue

            # Check if policy applies to this agent/action
            if self._policy_applies_to_action(policy, agent_id, action_type, context):
                violation = self._check_policy_violation(policy, agent_id, action_type, 
                                                       action_description, context)
                if violation:
                    violations.append(violation)

        return violations

    def _policy_applies_to_action(self, policy: Dict[str, Any], agent_id: str, 
                                 action_type: ActionType, context: Dict[str, Any]) -> bool:
        """Determine if a policy applies to the given action."""
        policy_content = policy.get('policy_content', {})

        # Check agent scope
        agent_scope = policy_content.get('agent_scope', [])
        if agent_scope and agent_id not in agent_scope and '*' not in agent_scope:
            return False

        # Check action type scope
        action_scope = policy_content.get('action_types', [])
        if action_scope and action_type.value not in action_scope and '*' not in action_scope:
            return False

        # Check context conditions
        conditions = policy_content.get('conditions', {})
        if conditions and not self._evaluate_conditions(conditions, context):
            return False

        return True

    def _check_policy_violation(self, policy: Dict[str, Any], agent_id: str, 
                               action_type: ActionType, action_description: str, 
                               context: Dict[str, Any]) -> Optional[ViolationDetail]:
        """Check if an action violates a specific policy."""
        policy_content = policy.get('policy_content', {})
        rules = policy_content.get('rules', [])

        for rule in rules:
            if self._rule_violated(rule, agent_id, action_type, action_description, context):
                return ViolationDetail(
                    policy_id=policy['policy_id'],
                    violation_type=rule.get('violation_type', 'policy_violation'),
                    severity=ViolationSeverity(rule.get('severity', 'medium')),
                    description=rule.get('description', f"Violation of policy {policy['policy_id']}")
                )

        return None

    def _rule_violated(self, rule: Dict[str, Any], agent_id: str, action_type: ActionType, 
                      action_description: str, context: Dict[str, Any]) -> bool:
        """Check if a specific rule is violated."""
        rule_type = rule.get('type')

        if rule_type == 'forbidden_action':
            forbidden_patterns = rule.get('patterns', [])
            return any(pattern in action_description.lower() for pattern in forbidden_patterns)

        elif rule_type == 'time_restriction':
            return self._check_time_restriction(rule, context)

        elif rule_type == 'resource_limit':
            return self._check_resource_limit(rule, context)

        elif rule_type == 'approval_required':
            return not context.get('approved', False)

        # Default: no violation detected
        return False

    def _check_time_restriction(self, rule: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check time-based restrictions."""
        allowed_hours = rule.get('allowed_hours', [])
        if not allowed_hours:
            return False

        current_hour = datetime.now().hour
        return current_hour not in allowed_hours

    def _check_resource_limit(self, rule: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check resource usage limits."""
        max_resources = rule.get('max_resources', {})
        current_usage = context.get('resource_usage', {})

        for resource, limit in max_resources.items():
            if current_usage.get(resource, 0) > limit:
                return True

        return False

    def _evaluate_conditions(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate policy conditions against context."""
        for key, expected_value in conditions.items():
            if context.get(key) != expected_value:
                return False
        return True

# Global violation checker instance
violation_checker = ViolationChecker()
