"""
Main simulation loop for multi-agent GaaS system testing.
This module orchestrates agent interactions and manages the simulation lifecycle.
"""

import time
import json
import csv
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
import logging

from client_interface import GaaSClient, ClientConfig
from agents import BaseAgent, create_agent_population

logger = logging.getLogger(__name__)

@dataclass
class SimulationConfig:
    """Configuration for the simulation."""
    duration_minutes: int = 30
    step_interval_seconds: float = 2.0
    max_concurrent_agents: int = 5
    log_interval_steps: int = 10
    backend_url: str = "http://localhost:8000"
    output_directory: str = "./simulation_results"
    
@dataclass
class SimulationMetrics:
    """Overall simulation metrics."""
    total_steps: int = 0
    total_actions: int = 0
    total_violations: int = 0
    total_blocks: int = 0
    total_warnings: int = 0
    agents_registered: int = 0
    simulation_start_time: Optional[datetime] = None
    simulation_end_time: Optional[datetime] = None
    average_response_time: float = 0.0
    
    @property
    def duration_seconds(self) -> float:
        """Calculate simulation duration in seconds."""
        if self.simulation_start_time and self.simulation_end_time:
            return (self.simulation_end_time - self.simulation_start_time).total_seconds()
        return 0.0
    
    @property
    def actions_per_minute(self) -> float:
        """Calculate actions per minute rate."""
        if self.duration_seconds > 0:
            return (self.total_actions * 60) / self.duration_seconds
        return 0.0

class PerformanceLogger:
    """Handles logging of performance data and metrics."""
    
    def __init__(self, output_directory: str):
        self.output_directory = output_directory
        self.action_logs = []
        self.response_time_logs = []
        self.agent_metrics_logs = []
        self.enforcement_decision_logs = []
        
        # Ensure output directory exists
        import os
        os.makedirs(output_directory, exist_ok=True)
    
    def log_action(self, agent_id: str, action_data: Dict, result: Dict, timestamp: datetime):
        """Log an individual action."""
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "agent_id": agent_id,
            "action_type": action_data.get("type"),
            "action_description": action_data.get("description"),
            "resource_accessed": action_data.get("resource"),
            "success": result.get("success", False),
            "violations_detected": len(result.get("violations_detected", [])),
            "violations": result.get("violations_detected", [])
        }
        self.action_logs.append(log_entry)
    
    def log_response_time(self, agent_id: str, endpoint: str, response_time: float, timestamp: datetime):
        """Log response time for API calls."""
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "agent_id": agent_id,
            "endpoint": endpoint,
            "response_time_seconds": response_time
        }
        self.response_time_logs.append(log_entry)
    
    def log_enforcement_decision(self, agent_id: str, proposed_action: str, 
                               decision: str, violations: List, timestamp: datetime):
        """Log enforcement decisions."""
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "agent_id": agent_id,
            "proposed_action": proposed_action,
            "decision": decision,
            "violation_count": len(violations),
            "violations": [v.get("violation_type", "unknown") for v in violations] if violations else []
        }
        self.enforcement_decision_logs.append(log_entry)
    
    def log_agent_metrics(self, agent: BaseAgent, timestamp: datetime):
        """Log agent-specific metrics."""
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "agent_id": agent.agent_id,
            "agent_type": agent.agent_type,
            "total_actions": agent.metrics.total_actions,
            "compliant_actions": agent.metrics.compliant_actions,
            "violations": agent.metrics.violations,
            "blocked_actions": agent.metrics.blocked_actions,
            "warnings_received": agent.metrics.warnings_received,
            "compliance_rate": agent.metrics.compliance_rate,
            "average_response_time": agent.metrics.average_response_time
        }
        self.agent_metrics_logs.append(log_entry)
    
    def save_logs_to_files(self):
        """Save all logged data to CSV files."""
        # Save action logs
        if self.action_logs:
            with open(f"{self.output_directory}/action_logs.csv", 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.action_logs[0].keys())
                writer.writeheader()
                writer.writerows(self.action_logs)
        
        # Save response time logs
        if self.response_time_logs:
            with open(f"{self.output_directory}/response_times.csv", 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.response_time_logs[0].keys())
                writer.writeheader()
                writer.writerows(self.response_time_logs)
        
        # Save enforcement decision logs
        if self.enforcement_decision_logs:
            with open(f"{self.output_directory}/enforcement_decisions.csv", 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.enforcement_decision_logs[0].keys())
                writer.writeheader()
                writer.writerows(self.enforcement_decision_logs)
        
        # Save agent metrics logs
        if self.agent_metrics_logs:
            with open(f"{self.output_directory}/agent_metrics.csv", 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.agent_metrics_logs[0].keys())
                writer.writeheader()
                writer.writerows(self.agent_metrics_logs)
        
        logger.info(f"Saved simulation logs to {self.output_directory}")

class GaaSSimulation:
    """Main simulation orchestrator for multi-agent GaaS testing."""
    
    def __init__(self, config: SimulationConfig = None):
        self.config = config or SimulationConfig()
        self.client_config = ClientConfig(base_url=self.config.backend_url)
        self.client = GaaSClient(self.client_config)
        self.agents: List[BaseAgent] = []
        self.metrics = SimulationMetrics()
        self.performance_logger = PerformanceLogger(self.config.output_directory)
        self.running = False
        self.step_count = 0
        
    def initialize_agents(self, num_agents: int = 15) -> bool:
        """Initialize and register all agents."""
        logger.info(f"Initializing {num_agents} agents...")
        
        # Create agent population
        self.agents = create_agent_population(self.client, num_agents)
        
        # Register all agents
        registration_success = 0
        for agent in self.agents:
            if agent.register():
                registration_success += 1
                time.sleep(0.1)  # Small delay between registrations
        
        self.metrics.agents_registered = registration_success
        logger.info(f"Successfully registered {registration_success}/{len(self.agents)} agents")
        
        return registration_success > 0
    
    def check_backend_health(self) -> bool:
        """Check if the backend is healthy and responsive."""
        try:
            response, response_time = self.client.health_check()
            logger.info(f"Backend health check: {response.get('status')} (response time: {response_time:.3f}s)")
            return response.get('status') == 'healthy'
        except Exception as e:
            logger.error(f"Backend health check failed: {str(e)}")
            return False
    
    def execute_agent_step(self, agent: BaseAgent) -> Dict[str, Any]:
        """Execute one simulation step for a single agent."""
        try:
            step_start_time = datetime.now()
            result = agent.simulate_step()
            
            # Log the step results
            if result.get("action_executed"):
                action_data = result.get("action_generated", {})
                action_result = result.get("action_result", {})
                
                self.performance_logger.log_action(
                    agent.agent_id, action_data, action_result, step_start_time
                )
                
                # Update simulation metrics
                self.metrics.total_actions += 1
                if action_result.get("violations_detected"):
                    self.metrics.total_violations += len(action_result["violations_detected"])
            
            # Log enforcement decision
            enforcement_decision = result.get("enforcement_decision", {})
            if enforcement_decision:
                decision = enforcement_decision.get("decision", "unknown")
                violations = enforcement_decision.get("violations", [])
                
                self.performance_logger.log_enforcement_decision(
                    agent.agent_id,
                    result.get("action_generated", {}).get("description", ""),
                    decision,
                    violations,
                    step_start_time
                )
                
                # Update metrics based on decision
                if decision == "block":
                    self.metrics.total_blocks += 1
                elif decision == "warn":
                    self.metrics.total_warnings += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing step for agent {agent.agent_id}: {str(e)}")
            return {"error": str(e), "agent_id": agent.agent_id}
    
    def execute_simulation_step(self):
        """Execute one simulation step for all active agents."""
        active_agents = [agent for agent in self.agents if agent.active and agent.registered]
        
        if not active_agents:
            logger.warning("No active agents available for simulation step")
            return
        
        # Execute agent steps concurrently
        with ThreadPoolExecutor(max_workers=self.config.max_concurrent_agents) as executor:
            future_to_agent = {
                executor.submit(self.execute_agent_step, agent): agent 
                for agent in active_agents
            }
            
            step_results = []
            for future in as_completed(future_to_agent):
                agent = future_to_agent[future]
                try:
                    result = future.result()
                    step_results.append(result)
                except Exception as e:
                    logger.error(f"Agent {agent.agent_id} step failed: {str(e)}")
        
        self.step_count += 1
        self.metrics.total_steps += 1
        
        # Log agent metrics periodically
        if self.step_count % self.config.log_interval_steps == 0:
            timestamp = datetime.now()
            for agent in active_agents:
                self.performance_logger.log_agent_metrics(agent, timestamp)
            
            logger.info(f"Completed step {self.step_count}: "
                       f"{len(step_results)} agents active, "
                       f"{self.metrics.total_actions} total actions, "
                       f"{self.metrics.total_violations} violations")
    
    def run_simulation(self) -> SimulationMetrics:
        """Run the complete simulation."""
        logger.info("Starting GaaS multi-agent simulation...")
        
        # Check backend health
        if not self.check_backend_health():
            raise Exception("Backend is not healthy - cannot start simulation")
        
        # Initialize agents
        if not self.initialize_agents():
            raise Exception("Failed to initialize agents - cannot start simulation")
        
        # Start simulation
        self.running = True
        self.metrics.simulation_start_time = datetime.now()
        
        try:
            end_time = self.metrics.simulation_start_time + timedelta(minutes=self.config.duration_minutes)
            
            logger.info(f"Simulation will run for {self.config.duration_minutes} minutes "
                       f"with {self.config.step_interval_seconds}s intervals")
            
            while self.running and datetime.now() < end_time:
                step_start = time.time()
                
                # Execute simulation step
                self.execute_simulation_step()
                
                # Wait for next step interval
                step_duration = time.time() - step_start
                sleep_time = max(0, self.config.step_interval_seconds - step_duration)
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
            self.metrics.simulation_end_time = datetime.now()
            
            # Calculate final metrics
            all_response_times = []
            for agent in self.agents:
                all_response_times.extend(agent.metrics.response_times)
            
            if all_response_times:
                self.metrics.average_response_time = sum(all_response_times) / len(all_response_times)
            
            logger.info("Simulation completed successfully")
            
        except KeyboardInterrupt:
            logger.info("Simulation interrupted by user")
            self.running = False
            self.metrics.simulation_end_time = datetime.now()
        
        except Exception as e:
            logger.error(f"Simulation failed: {str(e)}")
            self.running = False
            self.metrics.simulation_end_time = datetime.now()
            raise
        
        finally:
            # Save all logged data
            self.performance_logger.save_logs_to_files()
            
            # Save simulation summary
            self.save_simulation_summary()
        
        return self.metrics
    
    def save_simulation_summary(self):
        """Save simulation summary and metrics."""
        summary = {
            "simulation_config": asdict(self.config),
            "simulation_metrics": asdict(self.metrics),
            "agent_summary": []
        }
        
        # Add agent summaries
        for agent in self.agents:
            agent_summary = {
                "agent_id": agent.agent_id,
                "agent_type": agent.agent_type,
                "registered": agent.registered,
                "metrics": asdict(agent.metrics)
            }
            summary["agent_summary"].append(agent_summary)
        
        # Save to JSON file
        with open(f"{self.config.output_directory}/simulation_summary.json", 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Simulation summary saved to {self.config.output_directory}/simulation_summary.json")
    
    def stop_simulation(self):
        """Stop the simulation gracefully."""
        logger.info("Stopping simulation...")
        self.running = False
    
    def cleanup(self):
        """Clean up resources."""
        if self.client:
            self.client.close()

def main():
    """Main entry point for running the simulation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GaaS Multi-Agent Simulation")
    parser.add_argument("--duration", type=int, default=30, help="Simulation duration in minutes")
    parser.add_argument("--agents", type=int, default=15, help="Number of agents to simulate")
    parser.add_argument("--interval", type=float, default=2.0, help="Step interval in seconds")
    parser.add_argument("--backend-url", default="http://localhost:8000", help="Backend URL")
    parser.add_argument("--output-dir", default="./simulation_results", help="Output directory")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create simulation configuration
    config = SimulationConfig(
        duration_minutes=args.duration,
        step_interval_seconds=args.interval,
        backend_url=args.backend_url,
        output_directory=args.output_dir
    )
    
    # Run simulation
    simulation = GaaSSimulation(config)
    
    try:
        metrics = simulation.run_simulation()
        
        # Print final results
        print("\n" + "="*50)
        print("SIMULATION COMPLETED")
        print("="*50)
        print(f"Duration: {metrics.duration_seconds:.1f} seconds")
        print(f"Total Steps: {metrics.total_steps}")
        print(f"Total Actions: {metrics.total_actions}")
        print(f"Total Violations: {metrics.total_violations}")
        print(f"Total Blocks: {metrics.total_blocks}")
        print(f"Total Warnings: {metrics.total_warnings}")
        print(f"Agents Registered: {metrics.agents_registered}")
        print(f"Actions per Minute: {metrics.actions_per_minute:.1f}")
        print(f"Average Response Time: {metrics.average_response_time:.3f}s")
        print(f"Results saved to: {config.output_directory}")
        
    except Exception as e:
        logger.error(f"Simulation failed: {str(e)}")
        return 1
    
    finally:
        simulation.cleanup()
    
    return 0

if __name__ == "__main__":
    exit(main())