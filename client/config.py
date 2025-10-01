"""
Configuration management for the GaaS client simulation.
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class ClientSimulationConfig:
    """Configuration for the client simulation system."""
    
    # Backend connection settings
    backend_host: str = "localhost"
    backend_port: int = 8000
    backend_protocol: str = "http"
    connection_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Simulation settings
    simulation_duration_minutes: int = 30
    step_interval_seconds: float = 2.0
    num_agents: int = 15
    max_concurrent_agents: int = 5
    log_interval_steps: int = 10
    
    # Agent distribution settings
    compliant_agent_ratio: float = 0.25
    non_compliant_agent_ratio: float = 0.17
    mixed_behavior_agent_ratio: float = 0.50
    adaptive_agent_ratio: float = 0.08
    
    # Output settings
    output_directory: str = "./simulation_results"
    save_detailed_logs: bool = True
    save_agent_metrics: bool = True
    save_response_times: bool = True
    
    # Logging settings
    log_level: str = "INFO"
    console_logging: bool = True
    file_logging: bool = True
    log_file: str = "client_simulation.log"
    
    @property
    def backend_url(self) -> str:
        """Get the complete backend URL."""
        return f"{self.backend_protocol}://{self.backend_host}:{self.backend_port}"
    
    @classmethod
    def from_environment(cls) -> 'ClientSimulationConfig':
        """Create configuration from environment variables."""
        return cls(
            backend_host=os.getenv("GAAS_BACKEND_HOST", "localhost"),
            backend_port=int(os.getenv("GAAS_BACKEND_PORT", "8000")),
            backend_protocol=os.getenv("GAAS_BACKEND_PROTOCOL", "http"),
            connection_timeout=int(os.getenv("GAAS_CONNECTION_TIMEOUT", "30")),
            max_retries=int(os.getenv("GAAS_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("GAAS_RETRY_DELAY", "1.0")),
            
            simulation_duration_minutes=int(os.getenv("GAAS_SIMULATION_DURATION", "30")),
            step_interval_seconds=float(os.getenv("GAAS_STEP_INTERVAL", "2.0")),
            num_agents=int(os.getenv("GAAS_NUM_AGENTS", "15")),
            max_concurrent_agents=int(os.getenv("GAAS_MAX_CONCURRENT", "5")),
            log_interval_steps=int(os.getenv("GAAS_LOG_INTERVAL", "10")),
            
            output_directory=os.getenv("GAAS_OUTPUT_DIR", "./simulation_results"),
            save_detailed_logs=os.getenv("GAAS_SAVE_DETAILED_LOGS", "true").lower() == "true",
            save_agent_metrics=os.getenv("GAAS_SAVE_AGENT_METRICS", "true").lower() == "true",
            save_response_times=os.getenv("GAAS_SAVE_RESPONSE_TIMES", "true").lower() == "true",
            
            log_level=os.getenv("GAAS_LOG_LEVEL", "INFO"),
            console_logging=os.getenv("GAAS_CONSOLE_LOGGING", "true").lower() == "true",
            file_logging=os.getenv("GAAS_FILE_LOGGING", "true").lower() == "true",
            log_file=os.getenv("GAAS_LOG_FILE", "client_simulation.log")
        )
    
    def validate(self) -> bool:
        """Validate configuration parameters."""
        if self.simulation_duration_minutes <= 0:
            raise ValueError("Simulation duration must be positive")
        
        if self.step_interval_seconds <= 0:
            raise ValueError("Step interval must be positive")
        
        if self.num_agents <= 0:
            raise ValueError("Number of agents must be positive")
        
        if self.max_concurrent_agents <= 0:
            raise ValueError("Max concurrent agents must be positive")
        
        if not (0 < self.compliant_agent_ratio <= 1):
            raise ValueError("Compliant agent ratio must be between 0 and 1")
        
        if not (0 <= self.non_compliant_agent_ratio <= 1):
            raise ValueError("Non-compliant agent ratio must be between 0 and 1")
        
        if not (0 <= self.mixed_behavior_agent_ratio <= 1):
            raise ValueError("Mixed behavior agent ratio must be between 0 and 1")
        
        if not (0 <= self.adaptive_agent_ratio <= 1):
            raise ValueError("Adaptive agent ratio must be between 0 and 1")
        
        total_ratio = (self.compliant_agent_ratio + self.non_compliant_agent_ratio + 
                      self.mixed_behavior_agent_ratio + self.adaptive_agent_ratio)
        if abs(total_ratio - 1.0) > 0.01:
            raise ValueError(f"Agent ratios must sum to 1.0, got {total_ratio}")
        
        return True