from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

# Enums for better type safety
class AgentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class ActionType(str, Enum):
    DATA_ACCESS = "data_access"
    SYSTEM_MODIFICATION = "system_modification"
    USER_INTERACTION = "user_interaction"
    EXTERNAL_API_CALL = "external_api_call"

class ViolationSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EnforcementAction(str, Enum):
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    SUSPEND = "suspend"

class PolicyType(str, Enum):
    ACCESS_CONTROL = "access_control"
    DATA_GOVERNANCE = "data_governance"
    COMPLIANCE = "compliance"
    SECURITY = "security"

# Agent Registration Schemas
class AgentRegistrationRequest(BaseModel):
    agent_id: str = Field(..., min_length=3, max_length=50, description="Unique identifier for the agent")
    name: str = Field(..., min_length=1, max_length=100, description="Human-readable name for the agent")
    capabilities: List[str] = Field(..., description="List of capabilities the agent possesses")
    agent_type: str = Field(..., description="Type or category of the agent")
    contact_info: Optional[str] = Field(None, description="Contact information for the agent owner")

class AgentRegistrationResponse(BaseModel):
    success: bool
    agent_id: str
    status: AgentStatus
    registration_timestamp: datetime
    message: str

# Action Log Schemas
class ActionLogRequest(BaseModel):
    agent_id: str = Field(..., description="ID of the agent performing the action")
    action_type: ActionType = Field(..., description="Type of action being performed")
    action_description: str = Field(..., description="Detailed description of the action")
    timestamp: datetime = Field(..., description="When the action occurred")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context about the action")
    resource_accessed: Optional[str] = Field(None, description="Resource that was accessed")

class ActionLogResponse(BaseModel):
    success: bool
    log_id: str
    message: str
    violations_detected: List[str] = Field(default_factory=list)

# Enforcement Decision Schemas
class EnforcementDecisionRequest(BaseModel):
    agent_id: str = Field(..., description="ID of the agent requesting decision")
    proposed_action: str = Field(..., description="Action the agent wants to perform")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context for the decision")

class ViolationDetail(BaseModel):
    policy_id: str
    violation_type: str
    severity: ViolationSeverity
    description: str

class EnforcementDecisionResponse(BaseModel):
    decision: EnforcementAction
    agent_id: str
    reasoning: str
    violations: List[ViolationDetail] = Field(default_factory=list)
    timestamp: datetime
    additional_constraints: Optional[Dict[str, Any]] = None

# Policy Upload Schemas
class PolicyUploadRequest(BaseModel):
    policy_id: str = Field(..., description="Unique identifier for the policy")
    policy_name: str = Field(..., description="Human-readable name for the policy")
    policy_type: PolicyType = Field(..., description="Type of policy")
    policy_content: Dict[str, Any] = Field(..., description="The actual policy rules and conditions")
    version: str = Field(..., description="Version of the policy")
    effective_date: datetime = Field(..., description="When the policy becomes effective")
    expiry_date: Optional[datetime] = Field(None, description="When the policy expires")

class PolicyUploadResponse(BaseModel):
    success: bool
    policy_id: str
    version: str
    upload_timestamp: datetime
    message: str
    validation_errors: List[str] = Field(default_factory=list)

# Compliance Report Schemas
class ComplianceReportRequest(BaseModel):
    agent_id: Optional[str] = Field(None, description="Specific agent to report on (optional)")
    start_date: datetime = Field(..., description="Start date for the report period")
    end_date: datetime = Field(..., description="End date for the report period")
    report_type: str = Field(default="summary", description="Type of compliance report")
    include_violations: bool = Field(default=True, description="Whether to include violation details")

class ComplianceMetrics(BaseModel):
    total_actions: int
    compliant_actions: int
    violations: int
    compliance_rate: float
    most_common_violations: List[str]

class ComplianceReportResponse(BaseModel):
    report_id: str
    agent_id: Optional[str]
    period_start: datetime
    period_end: datetime
    generated_at: datetime
    metrics: ComplianceMetrics
    detailed_violations: List[ViolationDetail] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

# Error Response Schema
class ErrorResponse(BaseModel):
    error: bool = True
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
