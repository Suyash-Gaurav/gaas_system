from typing import Dict, List, Any, Optional
from datetime import datetime
from app.violation_checker import violation_checker
from app.schemas import (
    EnforcementAction, ViolationDetail, ViolationSeverity, 
    EnforcementDecisionResponse, ActionType
)

class Enforcer:
    def __init__(self):
        self.violation_checker = violation_checker
        self.enforcement_history: Dict[str, List[Dict[str, Any]]] = {}

    def make_enforcement_decision(self, agent_id: str, proposed_action: str, 
                                context: Dict[str, Any]) -> EnforcementDecisionResponse:
        """Make an enforcement decision based on policy violations."""

        # Determine action type from proposed action
        action_type = self._classify_action_type(proposed_action)

        # Check for violations
        violations = self.violation_checker.check_action_compliance(
            agent_id, action_type, proposed_action, context
        )

        # Determine enforcement action based on violations
        decision = self._determine_enforcement_action(violations, agent_id)

        # Generate reasoning
        reasoning = self._generate_reasoning(decision, violations)

        # Record enforcement decision
        self._record_enforcement_decision(agent_id, decision, violations, proposed_action)

        # Prepare additional constraints if needed
        additional_constraints = self._generate_constraints(decision, violations, context)

        return EnforcementDecisionResponse(
            decision=decision,
            agent_id=agent_id,
            reasoning=reasoning,
            violations=violations,
            timestamp=datetime.now(),
            additional_constraints=additional_constraints
        )

    def _classify_action_type(self, proposed_action: str) -> ActionType:
        """Classify the type of action based on the description."""
        action_lower = proposed_action.lower()

        if any(keyword in action_lower for keyword in ['read', 'access', 'view', 'get']):
            return ActionType.DATA_ACCESS
        elif any(keyword in action_lower for keyword in ['modify', 'update', 'delete', 'create', 'write']):
            return ActionType.SYSTEM_MODIFICATION
        elif any(keyword in action_lower for keyword in ['user', 'interact', 'message', 'notify']):
            return ActionType.USER_INTERACTION
        elif any(keyword in action_lower for keyword in ['api', 'external', 'call', 'request']):
            return ActionType.EXTERNAL_API_CALL
        else:
            return ActionType.DATA_ACCESS  # Default fallback

    def _determine_enforcement_action(self, violations: List[ViolationDetail], 
                                    agent_id: str) -> EnforcementAction:
        """Determine the appropriate enforcement action based on violations."""
        if not violations:
            return EnforcementAction.ALLOW

        # Check for critical violations
        critical_violations = [v for v in violations if v.severity == ViolationSeverity.CRITICAL]
        if critical_violations:
            return EnforcementAction.SUSPEND

        # Check for high severity violations
        high_violations = [v for v in violations if v.severity == ViolationSeverity.HIGH]
        if high_violations:
            return EnforcementAction.BLOCK

        # Check agent's violation history
        agent_history = self.enforcement_history.get(agent_id, [])
        recent_violations = [
            entry for entry in agent_history 
            if (datetime.now() - entry['timestamp']).days <= 7
        ]

        # If agent has recent violations, escalate enforcement
        if len(recent_violations) >= 3:
            return EnforcementAction.BLOCK
        elif len(recent_violations) >= 1:
            return EnforcementAction.WARN

        # For medium and low violations, warn by default
        return EnforcementAction.WARN

    def _generate_reasoning(self, decision: EnforcementAction, 
                          violations: List[ViolationDetail]) -> str:
        """Generate human-readable reasoning for the enforcement decision."""
        if decision == EnforcementAction.ALLOW:
            return "No policy violations detected. Action is permitted."

        violation_summary = []
        for violation in violations:
            violation_summary.append(f"{violation.severity.value} {violation.violation_type}")

        base_reason = f"Detected violations: {', '.join(violation_summary)}. "

        if decision == EnforcementAction.WARN:
            return base_reason + "Action permitted with warning."
        elif decision == EnforcementAction.BLOCK:
            return base_reason + "Action blocked due to policy violations."
        elif decision == EnforcementAction.SUSPEND:
            return base_reason + "Agent suspended due to critical violations."

        return base_reason

    def _record_enforcement_decision(self, agent_id: str, decision: EnforcementAction, 
                                   violations: List[ViolationDetail], proposed_action: str):
        """Record the enforcement decision for future reference."""
        if agent_id not in self.enforcement_history:
            self.enforcement_history[agent_id] = []

        record = {
            'timestamp': datetime.now(),
            'decision': decision.value,
            'violations_count': len(violations),
            'proposed_action': proposed_action,
            'violation_types': [v.violation_type for v in violations]
        }

        self.enforcement_history[agent_id].append(record)

        # Keep only last 100 records per agent
        if len(self.enforcement_history[agent_id]) > 100:
            self.enforcement_history[agent_id] = self.enforcement_history[agent_id][-100:]

    def _generate_constraints(self, decision: EnforcementAction, violations: List[ViolationDetail], 
                            context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate additional constraints based on the enforcement decision."""
        if decision == EnforcementAction.ALLOW:
            return None

        constraints = {}

        if decision == EnforcementAction.WARN:
            constraints['monitoring_required'] = True
            constraints['report_required'] = True

        elif decision == EnforcementAction.BLOCK:
            constraints['action_blocked'] = True
            constraints['retry_allowed'] = False
            constraints['escalation_required'] = True

        elif decision == EnforcementAction.SUSPEND:
            constraints['agent_suspended'] = True
            constraints['manual_review_required'] = True
            constraints['suspension_duration_hours'] = 24

        # Add violation-specific constraints
        for violation in violations:
            if violation.severity == ViolationSeverity.CRITICAL:
                constraints['immediate_notification'] = True
            elif violation.severity == ViolationSeverity.HIGH:
                constraints['supervisor_notification'] = True

        return constraints if constraints else None

    def get_agent_enforcement_history(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get enforcement history for a specific agent."""
        return self.enforcement_history.get(agent_id, [])

    def get_enforcement_statistics(self) -> Dict[str, Any]:
        """Get overall enforcement statistics."""
        total_decisions = sum(len(history) for history in self.enforcement_history.values())

        if total_decisions == 0:
            return {
                'total_decisions': 0,
                'decisions_by_type': {},
                'agents_with_violations': 0
            }

        decisions_by_type = {}
        for history in self.enforcement_history.values():
            for record in history:
                decision = record['decision']
                decisions_by_type[decision] = decisions_by_type.get(decision, 0) + 1

        return {
            'total_decisions': total_decisions,
            'decisions_by_type': decisions_by_type,
            'agents_with_violations': len(self.enforcement_history)
        }

# Global enforcer instance
enforcer = Enforcer()
