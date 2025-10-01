#!/usr/bin/env python3
"""
Main runner script for the GaaS multi-agent client simulation.
This script provides an easy way to run the complete simulation system.
"""

import sys
import os
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Add the client directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ClientSimulationConfig
from client_interface import GaaSClient, ClientConfig
from simulation import GaaSSimulation, SimulationConfig
from agents import create_agent_population

def setup_logging(config: ClientSimulationConfig):
    """Set up logging configuration."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    if config.console_logging:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(log_format))
        root_logger.addHandler(console_handler)
    
    # File handler
    if config.file_logging:
        # Ensure log directory exists
        log_path = Path(config.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(config.log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        root_logger.addHandler(file_handler)

def check_backend_connectivity(config: ClientSimulationConfig) -> bool:
    """Check if the backend is accessible."""
    client_config = ClientConfig(
        base_url=config.backend_url,
        timeout=config.connection_timeout,
        max_retries=1,
        retry_delay=config.retry_delay
    )
    
    client = GaaSClient(client_config)
    
    try:
        response, response_time = client.health_check()
        if response.get('status') == 'healthy':
            print(f"✓ Backend is healthy (response time: {response_time:.3f}s)")
            print(f"  - Registered agents: {response.get('registered_agents', 0)}")
            print(f"  - Active policies: {response.get('active_policies', 0)}")
            return True
        else:
            print(f"✗ Backend health check failed: {response}")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to backend at {config.backend_url}: {str(e)}")
        return False
    finally:
        client.close()

def print_simulation_info(config: ClientSimulationConfig):
    """Print simulation configuration information."""
    print("\n" + "="*60)
    print("GaaS MULTI-AGENT SIMULATION")
    print("="*60)
    print(f"Backend URL: {config.backend_url}")
    print(f"Simulation Duration: {config.simulation_duration_minutes} minutes")
    print(f"Step Interval: {config.step_interval_seconds} seconds")
    print(f"Number of Agents: {config.num_agents}")
    print(f"Max Concurrent Agents: {config.max_concurrent_agents}")
    print(f"Output Directory: {config.output_directory}")
    print(f"Log Level: {config.log_level}")
    print("-"*60)
    
    # Calculate agent distribution
    compliant_count = max(1, int(config.num_agents * config.compliant_agent_ratio))
    non_compliant_count = max(1, int(config.num_agents * config.non_compliant_agent_ratio))
    mixed_count = max(1, int(config.num_agents * config.mixed_behavior_agent_ratio))
    adaptive_count = config.num_agents - compliant_count - non_compliant_count - mixed_count
    
    print("Agent Distribution:")
    print(f"  - Compliant: {compliant_count}")
    print(f"  - Non-Compliant: {non_compliant_count}")
    print(f"  - Mixed Behavior: {mixed_count}")
    print(f"  - Adaptive Learning: {adaptive_count}")
    print("="*60)

def run_simulation_with_config(config: ClientSimulationConfig) -> int:
    """Run the simulation with the given configuration."""
    logger = logging.getLogger(__name__)
    
    try:
        # Validate configuration
        config.validate()
        logger.info("Configuration validated successfully")
        
        # Print simulation information
        print_simulation_info(config)
        
        # Check backend connectivity
        print("\nChecking backend connectivity...")
        if not check_backend_connectivity(config):
            print("\nERROR: Cannot connect to backend. Please ensure the GaaS backend is running.")
            print(f"Expected backend URL: {config.backend_url}")
            print("\nTo start the backend, run:")
            print("  cd gaas_system/backend")
            print("  python start_server.py")
            return 1
        
        # Create simulation configuration
        sim_config = SimulationConfig(
            duration_minutes=config.simulation_duration_minutes,
            step_interval_seconds=config.step_interval_seconds,
            max_concurrent_agents=config.max_concurrent_agents,
            log_interval_steps=config.log_interval_steps,
            backend_url=config.backend_url,
            output_directory=config.output_directory
        )
        
        # Create and run simulation
        print(f"\nStarting simulation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Press Ctrl+C to stop the simulation early\n")
        
        simulation = GaaSSimulation(sim_config)
        
        try:
            metrics = simulation.run_simulation()
            
            # Print final results
            print("\n" + "="*60)
            print("SIMULATION COMPLETED SUCCESSFULLY")
            print("="*60)
            print(f"Duration: {metrics.duration_seconds:.1f} seconds")
            print(f"Total Steps: {metrics.total_steps}")
            print(f"Total Actions: {metrics.total_actions}")
            print(f"Total Violations: {metrics.total_violations}")
            print(f"Total Blocks: {metrics.total_blocks}")
            print(f"Total Warnings: {metrics.total_warnings}")
            print(f"Agents Registered: {metrics.agents_registered}")
            print(f"Actions per Minute: {metrics.actions_per_minute:.1f}")
            print(f"Average Response Time: {metrics.average_response_time:.3f}s")
            print(f"\nResults saved to: {config.output_directory}")
            print("="*60)
            
            return 0
            
        except KeyboardInterrupt:
            print("\n\nSimulation interrupted by user")
            return 0
            
        finally:
            simulation.cleanup()
            
    except Exception as e:
        logger.error(f"Simulation failed: {str(e)}")
        print(f"\nERROR: Simulation failed - {str(e)}")
        return 1

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="GaaS Multi-Agent Client Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings
  python run_simulation.py
  
  # Run for 60 minutes with 20 agents
  python run_simulation.py --duration 60 --agents 20
  
  # Connect to remote backend
  python run_simulation.py --backend-host 192.168.1.100 --backend-port 8080
  
  # Run with custom output directory
  python run_simulation.py --output-dir /tmp/gaas_results
  
  # Run with debug logging
  python run_simulation.py --log-level DEBUG
        """
    )
    
    # Backend connection arguments
    parser.add_argument("--backend-host", default="localhost",
                       help="Backend host (default: localhost)")
    parser.add_argument("--backend-port", type=int, default=8000,
                       help="Backend port (default: 8000)")
    parser.add_argument("--backend-protocol", default="http",
                       choices=["http", "https"],
                       help="Backend protocol (default: http)")
    
    # Simulation arguments
    parser.add_argument("--duration", type=int, default=30,
                       help="Simulation duration in minutes (default: 30)")
    parser.add_argument("--agents", type=int, default=15,
                       help="Number of agents to simulate (default: 15)")
    parser.add_argument("--interval", type=float, default=2.0,
                       help="Step interval in seconds (default: 2.0)")
    parser.add_argument("--max-concurrent", type=int, default=5,
                       help="Maximum concurrent agents (default: 5)")
    
    # Output arguments
    parser.add_argument("--output-dir", default="./simulation_results",
                       help="Output directory (default: ./simulation_results)")
    parser.add_argument("--log-level", default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level (default: INFO)")
    parser.add_argument("--log-file", default="client_simulation.log",
                       help="Log file path (default: client_simulation.log)")
    
    # Configuration source
    parser.add_argument("--use-env", action="store_true",
                       help="Load configuration from environment variables")
    
    args = parser.parse_args()
    
    # Create configuration
    if args.use_env:
        config = ClientSimulationConfig.from_environment()
        print("Using configuration from environment variables")
    else:
        config = ClientSimulationConfig()
    
    # Override with command line arguments
    config.backend_host = args.backend_host
    config.backend_port = args.backend_port
    config.backend_protocol = args.backend_protocol
    config.simulation_duration_minutes = args.duration
    config.num_agents = args.agents
    config.step_interval_seconds = args.interval
    config.max_concurrent_agents = args.max_concurrent
    config.output_directory = args.output_dir
    config.log_level = args.log_level
    config.log_file = args.log_file
    
    # Setup logging
    setup_logging(config)
    
    # Run simulation
    return run_simulation_with_config(config)

if __name__ == "__main__":
    sys.exit(main())