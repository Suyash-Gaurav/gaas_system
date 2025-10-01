import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from config.settings import get_settings

settings = get_settings()

class GaaSLogger:
    def __init__(self):
        self.setup_logging()
        self.action_logs: Dict[str, Dict[str, Any]] = {}
        self.log_counter = 0

    def setup_logging(self):
        """Setup logging configuration."""
        log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

        # Create logs directory if it doesn't exist
        log_path = Path(settings.log_file).parent
        log_path.mkdir(exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(settings.log_file),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger('GaaS-Backend')

    def log_agent_registration(self, agent_id: str, registration_data: Dict[str, Any], 
                             success: bool, message: str):
        """Log agent registration events."""
        log_entry = {
            'event_type': 'agent_registration',
            'agent_id': agent_id,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'registration_data': registration_data
        }

        if success:
            self.logger.info(f"Agent registered successfully: {agent_id}")
        else:
            self.logger.error(f"Agent registration failed: {agent_id} - {message}")

        self._store_log_entry(log_entry)

    def log_action_submission(self, agent_id: str, action_data: Dict[str, Any], 
                            log_id: str, violations: list):
        """Log action submission events."""
        log_entry = {
            'event_type': 'action_submission',
            'agent_id': agent_id,
            'log_id': log_id,
            'action_data': action_data,
            'violations_detected': len(violations),
            'violations': [str(v) for v in violations],
            'timestamp': datetime.now().isoformat()
        }

        if violations:
            self.logger.warning(f"Action submitted with violations: {agent_id} - {len(violations)} violations")
        else:
            self.logger.info(f"Action submitted successfully: {agent_id}")

        self._store_log_entry(log_entry)

        # Store in action logs for compliance reporting
        self.action_logs[log_id] = {
            'agent_id': agent_id,
            'action_data': action_data,
            'violations': violations,
            'timestamp': datetime.now(),
            'log_id': log_id
        }

    def log_enforcement_decision(self, agent_id: str, decision: str, violations: list, 
                               reasoning: str):
        """Log enforcement decisions."""
        log_entry = {
            'event_type': 'enforcement_decision',
            'agent_id': agent_id,
            'decision': decision,
            'violations_count': len(violations),
            'reasoning': reasoning,
            'timestamp': datetime.now().isoformat()
        }

        self.logger.info(f"Enforcement decision made: {agent_id} - {decision}")
        self._store_log_entry(log_entry)

    def log_policy_upload(self, policy_id: str, policy_data: Dict[str, Any], 
                         success: bool, validation_errors: list):
        """Log policy upload events."""
        log_entry = {
            'event_type': 'policy_upload',
            'policy_id': policy_id,
            'success': success,
            'validation_errors': validation_errors,
            'policy_version': policy_data.get('version'),
            'timestamp': datetime.now().isoformat()
        }

        if success:
            self.logger.info(f"Policy uploaded successfully: {policy_id}")
        else:
            self.logger.error(f"Policy upload failed: {policy_id} - {validation_errors}")

        self._store_log_entry(log_entry)

    def log_compliance_report_generation(self, report_id: str, agent_id: Optional[str], 
                                       period_start: datetime, period_end: datetime):
        """Log compliance report generation."""
        log_entry = {
            'event_type': 'compliance_report',
            'report_id': report_id,
            'agent_id': agent_id,
            'period_start': period_start.isoformat(),
            'period_end': period_end.isoformat(),
            'timestamp': datetime.now().isoformat()
        }

        self.logger.info(f"Compliance report generated: {report_id}")
        self._store_log_entry(log_entry)

    def log_system_event(self, event_type: str, message: str, level: str = 'info', 
                        additional_data: Optional[Dict[str, Any]] = None):
        """Log general system events."""
        log_entry = {
            'event_type': event_type,
            'message': message,
            'level': level,
            'additional_data': additional_data or {},
            'timestamp': datetime.now().isoformat()
        }

        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(f"{event_type}: {message}")

        self._store_log_entry(log_entry)

    def _store_log_entry(self, log_entry: Dict[str, Any]):
        """Store log entry for potential retrieval."""
        # This could be extended to store in a database
        # For now, we just ensure it's logged to file
        pass

    def generate_log_id(self) -> str:
        """Generate a unique log ID."""
        self.log_counter += 1
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"LOG_{timestamp}_{self.log_counter:06d}"

    def get_action_logs_for_period(self, start_date: datetime, end_date: datetime, 
                                  agent_id: Optional[str] = None) -> list:
        """Get action logs for a specific period."""
        filtered_logs = []

        for log_id, log_data in self.action_logs.items():
            log_timestamp = log_data['timestamp']

            # Check if log is within the specified period
            if start_date <= log_timestamp <= end_date:
                # Check if agent filter applies
                if agent_id is None or log_data['agent_id'] == agent_id:
                    filtered_logs.append(log_data)

        return filtered_logs

    def get_violation_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get violation statistics for a period."""
        logs = self.get_action_logs_for_period(start_date, end_date)

        total_actions = len(logs)
        total_violations = sum(len(log['violations']) for log in logs)
        compliant_actions = sum(1 for log in logs if not log['violations'])

        violation_types = {}
        for log in logs:
            for violation in log['violations']:
                violation_type = getattr(violation, 'violation_type', 'unknown')
                violation_types[violation_type] = violation_types.get(violation_type, 0) + 1

        return {
            'total_actions': total_actions,
            'total_violations': total_violations,
            'compliant_actions': compliant_actions,
            'compliance_rate': compliant_actions / total_actions if total_actions > 0 else 1.0,
            'violation_types': violation_types
        }

# Global logger instance
gaas_logger = GaaSLogger()
