from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import uuid
from datetime import datetime, timedelta

from app.schemas import (
    AgentRegistrationRequest, AgentRegistrationResponse, AgentStatus,
    ActionLogRequest, ActionLogResponse,
    EnforcementDecisionRequest, EnforcementDecisionResponse,
    PolicyUploadRequest, PolicyUploadResponse,
    ComplianceReportRequest, ComplianceReportResponse, ComplianceMetrics,
    ErrorResponse
)
from app.policy_loader import policy_loader
from app.violation_checker import violation_checker
from app.enforcer import enforcer
from app.logger import gaas_logger
from config.settings import get_settings

# Initialize FastAPI app
app = FastAPI(
    title="Governance-as-a-Service (GaaS) Backend",
    description="A comprehensive governance system for AI agents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get settings
def get_app_settings():
    return get_settings()

# In-memory storage for registered agents (in production, use a database)
registered_agents: Dict[str, Dict[str, Any]] = {}

@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
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

@app.post("/register_agent", response_model=AgentRegistrationResponse)
async def register_agent(request: AgentRegistrationRequest, settings = Depends(get_app_settings)):
    """Register a new agent in the GaaS system."""
    try:
        # Check if agent already exists
        if request.agent_id in registered_agents:
            raise HTTPException(
                status_code=400,
                detail=f"Agent with ID {request.agent_id} already exists"
            )

        # Validate agent data
        if not request.name.strip():
            raise HTTPException(
                status_code=400,
                detail="Agent name cannot be empty"
            )

        if not request.capabilities:
            raise HTTPException(
                status_code=400,
                detail="Agent must have at least one capability"
            )

        # Register the agent
        registration_timestamp = datetime.now()
        agent_data = {
            "agent_id": request.agent_id,
            "name": request.name,
            "capabilities": request.capabilities,
            "agent_type": request.agent_type,
            "contact_info": request.contact_info,
            "status": AgentStatus.ACTIVE,
            "registration_timestamp": registration_timestamp
        }

        registered_agents[request.agent_id] = agent_data

        # Log the registration
        gaas_logger.log_agent_registration(
            request.agent_id, 
            agent_data, 
            True, 
            "Agent registered successfully"
        )

        return AgentRegistrationResponse(
            success=True,
            agent_id=request.agent_id,
            status=AgentStatus.ACTIVE,
            registration_timestamp=registration_timestamp,
            message="Agent registered successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        gaas_logger.log_agent_registration(
            request.agent_id, 
            request.dict(), 
            False, 
            str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during agent registration: {str(e)}"
        )

@app.post("/submit_action_log", response_model=ActionLogResponse)
async def submit_action_log(request: ActionLogRequest):
    """Accept and process action logs from agents."""
    try:
        # Verify agent is registered
        if request.agent_id not in registered_agents:
            raise HTTPException(
                status_code=404,
                detail=f"Agent {request.agent_id} is not registered"
            )

        # Check if agent is active
        agent = registered_agents[request.agent_id]
        if agent["status"] != AgentStatus.ACTIVE:
            raise HTTPException(
                status_code=403,
                detail=f"Agent {request.agent_id} is not active"
            )

        # Check for policy violations
        violations = violation_checker.check_action_compliance(
            request.agent_id,
            request.action_type,
            request.action_description,
            request.context
        )

        # Generate log ID
        log_id = gaas_logger.generate_log_id()

        # Log the action
        gaas_logger.log_action_submission(
            request.agent_id,
            request.dict(),
            log_id,
            violations
        )

        violation_messages = [f"{v.violation_type}: {v.description}" for v in violations]

        return ActionLogResponse(
            success=True,
            log_id=log_id,
            message="Action log submitted successfully",
            violations_detected=violation_messages
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during action log submission: {str(e)}"
        )

@app.get("/enforcement_decision", response_model=EnforcementDecisionResponse)
async def get_enforcement_decision(
    agent_id: str,
    proposed_action: str,
    context: str = "{}"  # JSON string of context
):
    """Provide enforcement decisions to agents."""
    try:
        # Verify agent is registered
        if agent_id not in registered_agents:
            raise HTTPException(
                status_code=404,
                detail=f"Agent {agent_id} is not registered"
            )

        # Parse context
        import json
        try:
            context_dict = json.loads(context) if context else {}
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON format for context parameter"
            )

        # Make enforcement decision
        decision_response = enforcer.make_enforcement_decision(
            agent_id,
            proposed_action,
            context_dict
        )

        # Log the enforcement decision
        gaas_logger.log_enforcement_decision(
            agent_id,
            decision_response.decision.value,
            decision_response.violations,
            decision_response.reasoning
        )

        return decision_response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during enforcement decision: {str(e)}"
        )

@app.post("/upload_policy", response_model=PolicyUploadResponse)
async def upload_policy(request: PolicyUploadRequest):
    """Allow policy uploads and updates."""
    try:
        # Validate policy data
        validation_errors = []

        if not request.policy_name.strip():
            validation_errors.append("Policy name cannot be empty")

        if not request.policy_content:
            validation_errors.append("Policy content cannot be empty")

        if request.effective_date > datetime.now() + timedelta(days=365):
            validation_errors.append("Effective date cannot be more than 1 year in the future")

        if request.expiry_date and request.expiry_date <= request.effective_date:
            validation_errors.append("Expiry date must be after effective date")

        # Prepare policy data for storage
        policy_data = {
            "policy_id": request.policy_id,
            "policy_name": request.policy_name,
            "policy_type": request.policy_type.value,
            "policy_content": request.policy_content,
            "version": request.version,
            "effective_date": request.effective_date.isoformat(),
            "expiry_date": request.expiry_date.isoformat() if request.expiry_date else None,
            "upload_timestamp": datetime.now().isoformat()
        }

        # Save policy
        success = policy_loader.save_policy(policy_data)

        if not success:
            validation_errors.append("Failed to save policy to storage")

        # Log policy upload
        gaas_logger.log_policy_upload(
            request.policy_id,
            policy_data,
            success and not validation_errors,
            validation_errors
        )

        return PolicyUploadResponse(
            success=success and not validation_errors,
            policy_id=request.policy_id,
            version=request.version,
            upload_timestamp=datetime.now(),
            message="Policy uploaded successfully" if success and not validation_errors else "Policy upload failed",
            validation_errors=validation_errors
        )

    except Exception as e:
        gaas_logger.log_policy_upload(
            request.policy_id,
            request.dict(),
            False,
            [str(e)]
        )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during policy upload: {str(e)}"
        )

@app.get("/compliance_report", response_model=ComplianceReportResponse)
async def get_compliance_report(
    start_date: str,
    end_date: str,
    agent_id: str = None,
    report_type: str = "summary",
    include_violations: bool = True
):
    """Generate compliance reports."""
    try:
        # Parse dates
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
            )

        if start_dt >= end_dt:
            raise HTTPException(
                status_code=400,
                detail="Start date must be before end date"
            )

        # Verify agent exists if specified
        if agent_id and agent_id not in registered_agents:
            raise HTTPException(
                status_code=404,
                detail=f"Agent {agent_id} is not registered"
            )

        # Generate report ID
        report_id = f"RPT_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"

        # Get violation statistics
        violation_stats = gaas_logger.get_violation_statistics(start_dt, end_dt)

        # Create compliance metrics
        metrics = ComplianceMetrics(
            total_actions=violation_stats['total_actions'],
            compliant_actions=violation_stats['compliant_actions'],
            violations=violation_stats['total_violations'],
            compliance_rate=violation_stats['compliance_rate'],
            most_common_violations=list(violation_stats['violation_types'].keys())[:5]
        )

        # Get detailed violations if requested
        detailed_violations = []
        if include_violations:
            action_logs = gaas_logger.get_action_logs_for_period(start_dt, end_dt, agent_id)
            for log in action_logs:
                detailed_violations.extend(log['violations'])

        # Generate recommendations
        recommendations = []
        if metrics.compliance_rate < 0.9:
            recommendations.append("Consider reviewing and updating policies")
        if metrics.violations > 10:
            recommendations.append("Implement additional agent training")
        if violation_stats['violation_types']:
            most_common = max(violation_stats['violation_types'], key=violation_stats['violation_types'].get)
            recommendations.append(f"Focus on addressing {most_common} violations")

        # Log report generation
        gaas_logger.log_compliance_report_generation(report_id, agent_id, start_dt, end_dt)

        return ComplianceReportResponse(
            report_id=report_id,
            agent_id=agent_id,
            period_start=start_dt,
            period_end=end_dt,
            generated_at=datetime.now(),
            metrics=metrics,
            detailed_violations=detailed_violations,
            recommendations=recommendations
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during compliance report generation: {str(e)}"
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "registered_agents": len(registered_agents),
        "active_policies": len(policy_loader.get_all_policies())
    }

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(app, host=settings.host, port=settings.port, reload=settings.debug)
