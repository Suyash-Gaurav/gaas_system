#!/usr/bin/env python3
"""
GaaS System Performance Evaluation Runner
Main script to execute comprehensive performance evaluation and analysis.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from performance_analyzer import GaaSPerformanceAnalyzer

def setup_logging(log_level=logging.INFO):
    """Setup logging configuration."""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('evaluation.log')
        ]
    )

def check_data_availability(data_directory: str) -> dict:
    """Check what simulation data files are available."""
    expected_files = {
        'action_logs.csv': 'Individual agent actions and results',
        'response_times.csv': 'API response time measurements',
        'enforcement_decisions.csv': 'Policy enforcement decisions',
        'agent_metrics.csv': 'Agent-specific performance metrics',
        'simulation_summary.json': 'Overall simulation summary'
    }
    
    available_files = {}
    missing_files = {}
    
    for filename, description in expected_files.items():
        filepath = os.path.join(data_directory, filename)
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            available_files[filename] = {
                'path': filepath,
                'size_bytes': file_size,
                'description': description
            }
        else:
            missing_files[filename] = description
    
    return {
        'available': available_files,
        'missing': missing_files,
        'total_expected': len(expected_files),
        'total_available': len(available_files)
    }

def print_data_status(data_status: dict):
    """Print the status of available data files."""
    print("\n" + "="*60)
    print("DATA AVAILABILITY STATUS")
    print("="*60)
    
    print(f"Available files: {data_status['total_available']}/{data_status['total_expected']}")
    
    if data_status['available']:
        print("\n✓ Available data files:")
        for filename, info in data_status['available'].items():
            size_kb = info['size_bytes'] / 1024
            print(f"  - {filename}: {size_kb:.1f} KB - {info['description']}")
    
    if data_status['missing']:
        print("\n❌ Missing data files:")
        for filename, description in data_status['missing'].items():
            print(f"  - {filename}: {description}")
    
    print("="*60)

def run_evaluation_pipeline(data_directory: str, output_directory: str = None) -> bool:
    """Run the complete evaluation pipeline."""
    logger = logging.getLogger(__name__)
    
    # Check data availability
    data_status = check_data_availability(data_directory)
    print_data_status(data_status)
    
    if data_status['total_available'] == 0:
        logger.error("No simulation data files found. Cannot proceed with evaluation.")
        logger.info("Please run the simulation first to generate performance data.")
        return False
    
    # Set up output directory
    if not output_directory:
        output_directory = os.path.join(os.path.dirname(data_directory), "evaluation_results")
    
    logger.info(f"Starting evaluation with data from: {data_directory}")
    logger.info(f"Results will be saved to: {output_directory}")
    
    # Initialize analyzer
    analyzer = GaaSPerformanceAnalyzer(data_directory, output_directory)
    
    # Run analysis
    try:
        success = analyzer.run_complete_analysis()
        
        if success:
            logger.info("✓ Evaluation completed successfully!")
            print("\n" + "="*60)
            print("EVALUATION COMPLETED SUCCESSFULLY")
            print("="*60)
            print(f"Results saved to: {output_directory}")
            print("\nGenerated outputs:")
            print("  - Comprehensive analysis plots")
            print("  - Detailed performance report")
            print("  - Analysis results JSON")
            print("="*60)
        else:
            logger.error("❌ Evaluation failed")
            return False
            
    except Exception as e:
        logger.error(f"Evaluation failed with error: {e}")
        return False
    
    return True

def demonstrate_analysis_framework():
    """Demonstrate the analysis framework structure and capabilities."""
    print("\n" + "="*60)
    print("GaaS PERFORMANCE EVALUATION FRAMEWORK")
    print("="*60)
    
    print("""
This evaluation framework provides comprehensive analysis of GaaS system performance:

📊 PERFORMANCE METRICS ANALYSIS:
  • Response time distributions and percentiles
  • API throughput and latency measurements
  • System load patterns over time
  • Endpoint-specific performance analysis

📈 COMPLIANCE ANALYSIS:
  • Compliance rates by agent type
  • Compliance trends over simulation time
  • Policy enforcement decision patterns
  • Violation detection and categorization

🔍 SYSTEM METRICS:
  • Overall simulation statistics
  • Agent registration and activity
  • Resource utilization patterns
  • Error rates and system health

📋 VISUALIZATION OUTPUTS:
  • Response time distribution histograms
  • Performance trends over time
  • Compliance rate comparisons
  • Enforcement decision breakdowns
  • Agent behavior analysis charts
  • System load and throughput graphs

📄 REPORTING:
  • Detailed markdown analysis report
  • Statistical summaries and insights
  • Performance recommendations
  • JSON results for further processing

USAGE:
  1. Run GaaS simulation to generate performance data
  2. Execute this evaluation script with data directory
  3. Review generated plots and analysis report
  4. Use insights for system optimization
""")
    
    print("="*60)

def main():
    """Main entry point for the evaluation runner."""
    parser = argparse.ArgumentParser(
        description='GaaS System Performance Evaluation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_evaluation.py --data-dir ../client/simulation_results
  python run_evaluation.py --data-dir ./data --output-dir ./results
  python run_evaluation.py --demo
        """
    )
    
    parser.add_argument(
        '--data-dir',
        help='Directory containing simulation data files'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Output directory for evaluation results (optional)'
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Show framework demonstration and capabilities'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting GaaS Performance Evaluation")
    
    # Show demo if requested
    if args.demo:
        demonstrate_analysis_framework()
        return 0
    
    # Validate arguments
    if not args.data_dir:
        print("Error: --data-dir is required (or use --demo to see framework capabilities)")
        parser.print_help()
        return 1
    
    if not os.path.exists(args.data_dir):
        logger.error(f"Data directory does not exist: {args.data_dir}")
        return 1
    
    # Run evaluation
    try:
        success = run_evaluation_pipeline(args.data_dir, args.output_dir)
        return 0 if success else 1
        
    except KeyboardInterrupt:
        logger.info("Evaluation interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())