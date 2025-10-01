"""
Multi-agent simulation system with diverse agent behaviors.
This module defines different types of agents with varying compliance patterns.
"""

import random
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging

from client_interface import GaaSClient, ClientConfig

logger = logging.getLogger(__name__)

@dataclass
class AgentMetrics:
    """Metrics tracking for individual agents."""
    total_actions: int = 0
    compliant_actions: int = 0
    violations: int = 0
    blocked_actions: int = 0
    warnings_received: int = 0
    response_times: List[float] = None
    
    def __post_init__(self):
        if self.response_times is None:
            self.response_times = []
    
    @property
    def compliance_rate(self) -> float:
        """Calculate compliance rate."""
        if self.total_actions == 0:
            return 1.0
        return self.compliant_actions / self.total_actions
    
    @property
    def average_response_time(self) -> float:
        """Calculate average response time."""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)

class BaseAgent(ABC):
    """Abstract base class for all agent types."""
    
    def __init__(self, agent_id: str, name: str, agent_type: str, 
                 capabilities: List[str], client: GaaSClient):
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.client = client
        self.metrics = AgentMetrics()
        self.registered = False
        self.active = True
        
    def register(self) -> bool:
        """Register the agent with the GaaS backend."""
        try:
            response, response_time = self.client.register_agent(
                agent_id=self.agent_id,
                name=self.name,
                capabilities=self.capabilities,
                agent_type=self.agent_type,
                contact_info=f"agent-{self.agent_id}@simulation.local"
            )
            
            self.metrics.response_times.append(response_time)
            
            if response.get('success', False):
                self.registered = True
                logger.info(f"Agent {self.agent_id} registered successfully")
                return True
            else:
                logger.error(f"Failed to register agent {self.agent_id}: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error registering agent {self.agent_id}: {str(e)}")
            return False
    
    def submit_action(self, action_type: str, action_description: str,
                     context: Dict[str, Any] = None, resource_accessed: str = None) -> Dict:
        """Submit an action log to the backend."""
        if not self.registered or not self.active:
            return {"success": False, "reason": "Agent not registered or inactive"}
        
        try:
            response, response_time = self.client.send_action_log(
                agent_id=self.agent_id,
                action_type=action_type,
                action_description=action_description,
                timestamp=datetime.now(),
                context=context or {},
                resource_accessed=resource_accessed
            )
            
            self.metrics.response_times.append(response_time)
            self.metrics.total_actions += 1
            
            violations = response.get('violations_detected', [])
            if violations:
                self.metrics.violations += len(violations)
                logger.debug(f"Agent {self.agent_id} action had violations: {violations}")
            else:
                self.metrics.compliant_actions += 1
            
            return response
            
        except Exception as e:
            logger.error(f"Error submitting action for agent {self.agent_id}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_enforcement_decision(self, proposed_action: str, 
                               context: Dict[str, Any] = None) -> Dict:
        """Get an enforcement decision from the backend."""
        if not self.registered or not self.active:
            return {"decision": "block", "reason": "Agent not registered or inactive"}
        
        try:
            response, response_time = self.client.get_enforcement_decision(
                agent_id=self.agent_id,
                proposed_action=proposed_action,
                context=context or {}
            )
            
            self.metrics.response_times.append(response_time)
            
            decision = response.get('decision', 'block')
            if decision == 'block':
                self.metrics.blocked_actions += 1
            elif decision == 'warn':
                self.metrics.warnings_received += 1
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting enforcement decision for agent {self.agent_id}: {str(e)}")
            return {"decision": "block", "error": str(e)}
    
    @abstractmethod
    def generate_action(self) -> Dict[str, Any]:
        """Generate an action based on agent behavior pattern."""
        pass
    
    @abstractmethod
    def decide_action_execution(self, enforcement_decision: Dict) -> bool:
        """Decide whether to execute an action based on enforcement decision."""
        pass
    
    def simulate_step(self) -> Dict[str, Any]:
        """Execute one simulation step for this agent."""
        if not self.active:
            return {"status": "inactive"}
        
        # Generate a potential action
        action_data = self.generate_action()
        
        # Get enforcement decision
        enforcement_decision = self.get_enforcement_decision(
            proposed_action=action_data['description'],
            context=action_data.get('context', {})
        )
        
        # Decide whether to proceed
        should_execute = self.decide_action_execution(enforcement_decision)
        
        result = {
            "agent_id": self.agent_id,
            "action_generated": action_data,
            "enforcement_decision": enforcement_decision,
            "action_executed": should_execute
        }
        
        # Execute action if decided to proceed
        if should_execute:
            action_result = self.submit_action(
                action_type=action_data['type'],
                action_description=action_data['description'],
                context=action_data.get('context', {}),
                resource_accessed=action_data.get('resource')
            )
            result["action_result"] = action_result
        
        return result

class CompliantAgent(BaseAgent):
    """Agent that always follows governance policies and enforcement decisions."""
    
    def __init__(self, agent_id: str, name: str, client: GaaSClient):
        super().__init__(
            agent_id=agent_id,
            name=name,
            agent_type="compliant",
            capabilities=["data_analysis", "reporting", "basic_operations"],
            client=client
        )
        self.compliant_actions = [
            "Generate standard report",
            "Read public documentation",
            "Perform routine data analysis",
            "Update personal profile",
            "Submit status report"
        ]
    
    def generate_action(self) -> Dict[str, Any]:
        """Generate compliant actions."""
        action_desc = random.choice(self.compliant_actions)
        return {
            "type": "data_access",
            "description": action_desc,
            "context": {
                "priority": "normal",
                "user_initiated": True,
                "compliance_checked": True
            },
            "resource": f"public_resource_{random.randint(1, 10)}"
        }
    
    def decide_action_execution(self, enforcement_decision: Dict) -> bool:
        """Always respect enforcement decisions."""
        decision = enforcement_decision.get('decision', 'block')
        return decision in ['allow', 'warn']

class NonCompliantAgent(BaseAgent):
    """Agent that frequently violates policies and ignores enforcement decisions."""
    
    def __init__(self, agent_id: str, name: str, client: GaaSClient):
        super().__init__(
            agent_id=agent_id,
            name=name,
            agent_type="non_compliant",
            capabilities=["system_access", "data_modification", "advanced_operations"],
            client=client
        )
        self.risky_actions = [
            "Access sensitive database",
            "Modify system configuration",
            "Export confidential data",
            "Bypass security controls",
            "Execute privileged commands"
        ]
    
    def generate_action(self) -> Dict[str, Any]:
        """Generate potentially non-compliant actions."""
        action_desc = random.choice(self.risky_actions)
        action_type = random.choice(["data_access", "system_modification", "external_api_call"])
        
        return {
            "type": action_type,
            "description": action_desc,
            "context": {
                "priority": "high",
                "user_initiated": False,
                "compliance_checked": False,
                "risk_level": "high"
            },
            "resource": f"sensitive_resource_{random.randint(1, 5)}"
        }
    
    def decide_action_execution(self, enforcement_decision: Dict) -> bool:
        """Often ignores enforcement decisions (70% chance to proceed regardless)."""
        if random.random() < 0.7:
            return True  # Proceed regardless of decision
        
        decision = enforcement_decision.get('decision', 'block')
        return decision in ['allow', 'warn']

class MixedBehaviorAgent(BaseAgent):
    """Agent with mixed compliance behavior - sometimes compliant, sometimes not."""
    
    def __init__(self, agent_id: str, name: str, client: GaaSClient):
        super().__init__(
            agent_id=agent_id,
            name=name,
            agent_type="mixed_behavior",
            capabilities=["data_processing", "user_interaction", "system_integration"],
            client=client
        )
        self.compliance_probability = random.uniform(0.3, 0.8)  # Random compliance rate
        
        self.compliant_actions = [
            "Process user request",
            "Generate analytics report",
            "Update dashboard",
            "Send notification"
        ]
        
        self.questionable_actions = [
            "Access user personal data",
            "Modify business rules",
            "Cache sensitive information",
            "Log detailed user activity"
        ]
    
    def generate_action(self) -> Dict[str, Any]:
        """Generate actions based on current compliance mood."""
        if random.random() < self.compliance_probability:
            # Generate compliant action
            action_desc = random.choice(self.compliant_actions)
            action_type = "user_interaction"
            risk_level = "low"
            resource = f"standard_resource_{random.randint(1, 20)}"
        else:
            # Generate questionable action
            action_desc = random.choice(self.questionable_actions)
            action_type = random.choice(["data_access", "system_modification"])
            risk_level = "medium"
            resource = f"restricted_resource_{random.randint(1, 10)}"
        
        return {
            "type": action_type,
            "description": action_desc,
            "context": {
                "priority": random.choice(["low", "normal", "high"]),
                "user_initiated": random.choice([True, False]),
                "risk_level": risk_level
            },
            "resource": resource
        }
    
    def decide_action_execution(self, enforcement_decision: Dict) -> bool:
        """Respect enforcement decisions most of the time."""
        decision = enforcement_decision.get('decision', 'block')
        
        if decision == 'allow':
            return True
        elif decision == 'warn':
            return random.random() < 0.8  # Usually proceed with warnings
        elif decision == 'block':
            return random.random() < 0.2  # Sometimes ignore blocks
        else:
            return False

class AdaptiveLearningAgent(BaseAgent):
    """Agent that learns from enforcement decisions and adapts behavior over time."""
    
    def __init__(self, agent_id: str, name: str, client: GaaSClient):
        super().__init__(
            agent_id=agent_id,
            name=name,
            agent_type="adaptive_learning",
            capabilities=["machine_learning", "pattern_recognition", "adaptive_behavior"],
            client=client
        )
        self.learning_rate = 0.1
        self.action_success_rates = {}  # Track success rates for different actions
        self.recent_decisions = []  # Track recent enforcement decisions
        
    def update_learning(self, action_type: str, decision: str):
        """Update learning based on enforcement decision."""
        if action_type not in self.action_success_rates:
            self.action_success_rates[action_type] = 0.5  # Start neutral
        
        if decision == 'allow':
            self.action_success_rates[action_type] += self.learning_rate * (1 - self.action_success_rates[action_type])
        elif decision in ['block', 'suspend']:
            self.action_success_rates[action_type] -= self.learning_rate * self.action_success_rates[action_type]
        
        self.recent_decisions.append(decision)
        if len(self.recent_decisions) > 20:
            self.recent_decisions.pop(0)
    
    def generate_action(self) -> Dict[str, Any]:
        """Generate actions based on learned success rates."""
        # Choose action type based on learned success rates
        if self.action_success_rates:
            action_types = list(self.action_success_rates.keys())
            weights = [self.action_success_rates[at] for at in action_types]
            action_type = random.choices(action_types, weights=weights)[0]
        else:
            action_type = random.choice(["data_access", "user_interaction", "system_modification"])
        
        # Generate appropriate action description
        if action_type == "data_access":
            actions = ["Query database", "Read configuration", "Access logs"]
        elif action_type == "user_interaction":
            actions = ["Send message", "Update interface", "Process request"]
        else:
            actions = ["Update settings", "Restart service", "Clear cache"]
        
        action_desc = random.choice(actions)
        
        return {
            "type": action_type,
            "description": action_desc,
            "context": {
                "learning_iteration": len(self.recent_decisions),
                "confidence": self.action_success_rates.get(action_type, 0.5)
            },
            "resource": f"adaptive_resource_{random.randint(1, 15)}"
        }
    
    def decide_action_execution(self, enforcement_decision: Dict) -> bool:
        """Make decisions based on learned patterns."""
        decision = enforcement_decision.get('decision', 'block')
        
        # Update learning
        action_type = enforcement_decision.get('context', {}).get('action_type', 'unknown')
        self.update_learning(action_type, decision)
        
        # Make execution decision
        if decision == 'allow':
            return True
        elif decision == 'warn':
            # Consider recent pattern of decisions
            recent_blocks = sum(1 for d in self.recent_decisions[-5:] if d in ['block', 'suspend'])
            return recent_blocks < 2  # Be more cautious if recent blocks
        else:
            return False

def create_agent_population(client: GaaSClient, num_agents: int = 15) -> List[BaseAgent]:
    """Create a diverse population of agents for simulation."""
    agents = []
    
    # Distribution of agent types
    compliant_count = max(1, num_agents // 4)
    non_compliant_count = max(1, num_agents // 6)
    mixed_count = max(1, num_agents // 2)
    adaptive_count = num_agents - compliant_count - non_compliant_count - mixed_count
    
    # Create compliant agents
    for i in range(compliant_count):
        agent = CompliantAgent(
            agent_id=f"compliant_agent_{i+1:02d}",
            name=f"Compliant Agent {i+1}",
            client=client
        )
        agents.append(agent)
    
    # Create non-compliant agents
    for i in range(non_compliant_count):
        agent = NonCompliantAgent(
            agent_id=f"noncompliant_agent_{i+1:02d}",
            name=f"Non-Compliant Agent {i+1}",
            client=client
        )
        agents.append(agent)
    
    # Create mixed behavior agents
    for i in range(mixed_count):
        agent = MixedBehaviorAgent(
            agent_id=f"mixed_agent_{i+1:02d}",
            name=f"Mixed Behavior Agent {i+1}",
            client=client
        )
        agents.append(agent)
    
    # Create adaptive learning agents
    for i in range(adaptive_count):
        agent = AdaptiveLearningAgent(
            agent_id=f"adaptive_agent_{i+1:02d}",
            name=f"Adaptive Learning Agent {i+1}",
            client=client
        )
        agents.append(agent)
    
    logger.info(f"Created agent population: {compliant_count} compliant, {non_compliant_count} non-compliant, "
                f"{mixed_count} mixed behavior, {adaptive_count} adaptive learning")
    
    return agents