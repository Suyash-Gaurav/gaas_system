"""
Client interface module for interacting with the GaaS FastAPI backend.
This module provides methods to communicate with all backend endpoints.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ClientConfig:
    """Configuration for the GaaS client."""
    base_url: str = "http://localhost:8000"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0

class GaaSClient:
    """Client interface for interacting with the GaaS backend."""
    
    def __init__(self, config: ClientConfig = None):
        """Initialize the GaaS client with configuration."""
        self.config = config or ClientConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'GaaS-Client/1.0.0'
        })
        
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Tuple[Dict, float]:
        """
        Make HTTP request with retry logic and performance tracking.
        
        Returns:
            Tuple of (response_data, response_time_seconds)
        """
        url = f"{self.config.base_url}{endpoint}"
        start_time = time.time()
        
        for attempt in range(self.config.max_retries):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, params=params, timeout=self.config.timeout)
                elif method.upper() == 'POST':
                    response = self.session.post(url, json=data, timeout=self.config.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    return response.json(), response_time
                else:
                    logger.warning(f"HTTP {response.status_code} for {method} {endpoint}: {response.text}")
                    if attempt == self.config.max_retries - 1:
                        response.raise_for_status()
                        
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.config.max_retries - 1:
                    raise
                time.sleep(self.config.retry_delay * (attempt + 1))
        
        # Should not reach here
        raise Exception("Max retries exceeded")
    
    def register_agent(self, agent_id: str, name: str, capabilities: List[str], 
                      agent_type: str, contact_info: str = None) -> Tuple[Dict, float]:
        """
        Register an agent with the GaaS backend.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
            capabilities: List of capabilities the agent possesses
            agent_type: Type or category of the agent
            contact_info: Optional contact information
            
        Returns:
            Tuple of (response_data, response_time_seconds)
        """
        data = {
            "agent_id": agent_id,
            "name": name,
            "capabilities": capabilities,
            "agent_type": agent_type,
            "contact_info": contact_info
        }
        
        logger.info(f"Registering agent: {agent_id}")
        return self._make_request('POST', '/register_agent', data=data)
    
    def send_action_log(self, agent_id: str, action_type: str, action_description: str,
                       timestamp: datetime, context: Dict[str, Any] = None,
                       resource_accessed: str = None) -> Tuple[Dict, float]:
        """
        Submit an action log to the GaaS backend.
        
        Args:
            agent_id: ID of the agent performing the action
            action_type: Type of action (data_access, system_modification, etc.)
            action_description: Detailed description of the action
            timestamp: When the action occurred
            context: Additional context about the action
            resource_accessed: Resource that was accessed
            
        Returns:
            Tuple of (response_data, response_time_seconds)
        """
        data = {
            "agent_id": agent_id,
            "action_type": action_type,
            "action_description": action_description,
            "timestamp": timestamp.isoformat(),
            "context": context or {},
            "resource_accessed": resource_accessed
        }
        
        logger.debug(f"Submitting action log for agent: {agent_id}")
        return self._make_request('POST', '/submit_action_log', data=data)
    
    def get_enforcement_decision(self, agent_id: str, proposed_action: str,
                               context: Dict[str, Any] = None) -> Tuple[Dict, float]:
        """
        Get an enforcement decision from the GaaS backend.
        
        Args:
            agent_id: ID of the agent requesting decision
            proposed_action: Action the agent wants to perform
            context: Context for the decision
            
        Returns:
            Tuple of (response_data, response_time_seconds)
        """
        params = {
            "agent_id": agent_id,
            "proposed_action": proposed_action,
            "context": json.dumps(context or {})
        }
        
        logger.debug(f"Getting enforcement decision for agent: {agent_id}")
        return self._make_request('GET', '/enforcement_decision', params=params)
    
    def upload_policy(self, policy_id: str, policy_name: str, policy_type: str,
                     policy_content: Dict[str, Any], version: str,
                     effective_date: datetime, expiry_date: datetime = None) -> Tuple[Dict, float]:
        """
        Upload a policy to the GaaS backend.
        
        Args:
            policy_id: Unique identifier for the policy
            policy_name: Human-readable name for the policy
            policy_type: Type of policy (access_control, data_governance, etc.)
            policy_content: The actual policy rules and conditions
            version: Version of the policy
            effective_date: When the policy becomes effective
            expiry_date: When the policy expires (optional)
            
        Returns:
            Tuple of (response_data, response_time_seconds)
        """
        data = {
            "policy_id": policy_id,
            "policy_name": policy_name,
            "policy_type": policy_type,
            "policy_content": policy_content,
            "version": version,
            "effective_date": effective_date.isoformat(),
            "expiry_date": expiry_date.isoformat() if expiry_date else None
        }
        
        logger.info(f"Uploading policy: {policy_id}")
        return self._make_request('POST', '/upload_policy', data=data)
    
    def get_compliance_report(self, start_date: datetime, end_date: datetime,
                            agent_id: str = None, report_type: str = "summary",
                            include_violations: bool = True) -> Tuple[Dict, float]:
        """
        Get a compliance report from the GaaS backend.
        
        Args:
            start_date: Start date for the report period
            end_date: End date for the report period
            agent_id: Specific agent to report on (optional)
            report_type: Type of compliance report
            include_violations: Whether to include violation details
            
        Returns:
            Tuple of (response_data, response_time_seconds)
        """
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "report_type": report_type,
            "include_violations": include_violations
        }
        
        if agent_id:
            params["agent_id"] = agent_id
        
        logger.info(f"Getting compliance report for period: {start_date} to {end_date}")
        return self._make_request('GET', '/compliance_report', params=params)
    
    def health_check(self) -> Tuple[Dict, float]:
        """
        Check the health of the GaaS backend.
        
        Returns:
            Tuple of (response_data, response_time_seconds)
        """
        return self._make_request('GET', '/health')
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()