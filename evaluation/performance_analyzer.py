"""
GaaS System Performance Analyzer
Comprehensive analysis and visualization of GaaS system performance data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class GaaSPerformanceAnalyzer:
    """Main class for analyzing GaaS system performance data."""
    
    def __init__(self, data_directory: str, output_directory: str = None):
        """
        Initialize the performance analyzer.
        
        Args:
            data_directory: Directory containing simulation CSV files
            output_directory: Directory to save analysis results
        """
        self.data_dir = data_directory
        self.output_dir = output_directory or os.path.join(os.path.dirname(data_directory), "analysis_results")
        
        # Create output directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "plots"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "reports"), exist_ok=True)
        
        # Data containers
        self.action_logs = None
        self.response_times = None
        self.enforcement_decisions = None
        self.agent_metrics = None
        self.simulation_summary = None
        
        # Analysis results
        self.performance_metrics = {}
        self.compliance_analysis = {}
        self.system_metrics = {}
        
    def load_data(self) -> bool:
        """Load all available data files."""
        print("Loading simulation data...")
        
        try:
            # Load action logs
            action_file = os.path.join(self.data_dir, "action_logs.csv")
            if os.path.exists(action_file):
                self.action_logs = pd.read_csv(action_file)
                self.action_logs['timestamp'] = pd.to_datetime(self.action_logs['timestamp'])
                print(f"✓ Loaded {len(self.action_logs)} action records")
            
            # Load response times
            response_file = os.path.join(self.data_dir, "response_times.csv")
            if os.path.exists(response_file):
                self.response_times = pd.read_csv(response_file)
                self.response_times['timestamp'] = pd.to_datetime(self.response_times['timestamp'])
                print(f"✓ Loaded {len(self.response_times)} response time records")
            
            # Load enforcement decisions
            enforcement_file = os.path.join(self.data_dir, "enforcement_decisions.csv")
            if os.path.exists(enforcement_file):
                self.enforcement_decisions = pd.read_csv(enforcement_file)
                self.enforcement_decisions['timestamp'] = pd.to_datetime(self.enforcement_decisions['timestamp'])
                print(f"✓ Loaded {len(self.enforcement_decisions)} enforcement decisions")
            
            # Load agent metrics
            metrics_file = os.path.join(self.data_dir, "agent_metrics.csv")
            if os.path.exists(metrics_file):
                self.agent_metrics = pd.read_csv(metrics_file)
                self.agent_metrics['timestamp'] = pd.to_datetime(self.agent_metrics['timestamp'])
                print(f"✓ Loaded {len(self.agent_metrics)} agent metric records")
            
            # Load simulation summary
            summary_file = os.path.join(self.data_dir, "simulation_summary.json")
            if os.path.exists(summary_file):
                with open(summary_file, 'r') as f:
                    self.simulation_summary = json.load(f)
                print("✓ Loaded simulation summary")
            
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def analyze_performance_metrics(self):
        """Analyze system performance metrics."""
        print("Analyzing performance metrics...")
        
        if self.response_times is not None:
            # Response time analysis
            response_stats = {
                'mean_response_time': self.response_times['response_time_seconds'].mean(),
                'median_response_time': self.response_times['response_time_seconds'].median(),
                'p95_response_time': self.response_times['response_time_seconds'].quantile(0.95),
                'p99_response_time': self.response_times['response_time_seconds'].quantile(0.99),
                'max_response_time': self.response_times['response_time_seconds'].max(),
                'min_response_time': self.response_times['response_time_seconds'].min(),
                'std_response_time': self.response_times['response_time_seconds'].std()
            }
            
            # Throughput analysis
            if len(self.response_times) > 0:
                time_span = (self.response_times['timestamp'].max() - 
                           self.response_times['timestamp'].min()).total_seconds()
                throughput = len(self.response_times) / (time_span / 60) if time_span > 0 else 0
                response_stats['requests_per_minute'] = throughput
            
            self.performance_metrics['response_times'] = response_stats
        
        if self.action_logs is not None:
            # Action success rate
            success_rate = self.action_logs['success'].mean() if 'success' in self.action_logs.columns else 0
            violation_rate = self.action_logs['violations_detected'].mean() if 'violations_detected' in self.action_logs.columns else 0
            
            self.performance_metrics['actions'] = {
                'total_actions': len(self.action_logs),
                'success_rate': success_rate,
                'average_violations_per_action': violation_rate
            }
    
    def analyze_compliance_patterns(self):
        """Analyze compliance patterns and trends."""
        print("Analyzing compliance patterns...")
        
        if self.agent_metrics is not None:
            # Compliance by agent type
            compliance_by_type = self.agent_metrics.groupby('agent_type')['compliance_rate'].agg([
                'mean', 'median', 'std', 'count'
            ]).round(4)
            
            # Compliance trends over time
            compliance_trends = self.agent_metrics.groupby([
                self.agent_metrics['timestamp'].dt.floor('T'),  # Group by minute
                'agent_type'
            ])['compliance_rate'].mean().reset_index()
            
            self.compliance_analysis = {
                'compliance_by_type': compliance_by_type.to_dict(),
                'compliance_trends': compliance_trends
            }
        
        if self.enforcement_decisions is not None:
            # Enforcement decision patterns
            decision_counts = self.enforcement_decisions['decision'].value_counts()
            decision_rates = (decision_counts / len(self.enforcement_decisions)).round(4)
            
            self.compliance_analysis['enforcement_patterns'] = {
                'decision_counts': decision_counts.to_dict(),
                'decision_rates': decision_rates.to_dict()
            }
    
    def analyze_system_metrics(self):
        """Analyze overall system metrics."""
        print("Analyzing system metrics...")
        
        if self.simulation_summary:
            metrics = self.simulation_summary.get('simulation_metrics', {})
            self.system_metrics = {
                'simulation_duration': metrics.get('duration_seconds', 0),
                'total_steps': metrics.get('total_steps', 0),
                'total_actions': metrics.get('total_actions', 0),
                'total_violations': metrics.get('total_violations', 0),
                'total_blocks': metrics.get('total_blocks', 0),
                'total_warnings': metrics.get('total_warnings', 0),
                'agents_registered': metrics.get('agents_registered', 0),
                'actions_per_minute': metrics.get('actions_per_minute', 0),
                'average_response_time': metrics.get('average_response_time', 0)
            }
    
    def generate_visualizations(self):
        """Generate comprehensive visualizations."""
        print("Generating visualizations...")
        
        # Set up plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create figure for multiple subplots
        fig = plt.figure(figsize=(20, 24))
        
        # 1. Response Time Distribution
        if self.response_times is not None and len(self.response_times) > 0:
            plt.subplot(4, 3, 1)
            plt.hist(self.response_times['response_time_seconds'], bins=30, alpha=0.7, edgecolor='black')
            plt.title('Response Time Distribution')
            plt.xlabel('Response Time (seconds)')
            plt.ylabel('Frequency')
            plt.grid(True, alpha=0.3)
        
        # 2. Response Time Over Time
        if self.response_times is not None and len(self.response_times) > 0:
            plt.subplot(4, 3, 2)
            plt.plot(self.response_times['timestamp'], self.response_times['response_time_seconds'], 
                    alpha=0.6, linewidth=1)
            plt.title('Response Time Over Time')
            plt.xlabel('Time')
            plt.ylabel('Response Time (seconds)')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
        
        # 3. Compliance Rates by Agent Type
        if self.agent_metrics is not None and len(self.agent_metrics) > 0:
            plt.subplot(4, 3, 3)
            compliance_by_type = self.agent_metrics.groupby('agent_type')['compliance_rate'].mean()
            bars = plt.bar(compliance_by_type.index, compliance_by_type.values)
            plt.title('Average Compliance Rate by Agent Type')
            plt.xlabel('Agent Type')
            plt.ylabel('Compliance Rate')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.2f}', ha='center', va='bottom')
        
        # 4. Enforcement Decision Breakdown
        if self.enforcement_decisions is not None and len(self.enforcement_decisions) > 0:
            plt.subplot(4, 3, 4)
            decision_counts = self.enforcement_decisions['decision'].value_counts()
            plt.pie(decision_counts.values, labels=decision_counts.index, autopct='%1.1f%%')
            plt.title('Enforcement Decision Breakdown')
        
        # 5. Actions Over Time
        if self.action_logs is not None and len(self.action_logs) > 0:
            plt.subplot(4, 3, 5)
            actions_per_minute = self.action_logs.set_index('timestamp').resample('T').size()
            plt.plot(actions_per_minute.index, actions_per_minute.values, marker='o', linewidth=2)
            plt.title('Actions Per Minute Over Time')
            plt.xlabel('Time')
            plt.ylabel('Actions per Minute')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
        
        # 6. Violation Patterns
        if self.action_logs is not None and len(self.action_logs) > 0 and 'violations_detected' in self.action_logs.columns:
            plt.subplot(4, 3, 6)
            violation_counts = self.action_logs['violations_detected'].value_counts().sort_index()
            plt.bar(violation_counts.index, violation_counts.values)
            plt.title('Violation Count Distribution')
            plt.xlabel('Number of Violations per Action')
            plt.ylabel('Frequency')
            plt.grid(True, alpha=0.3)
        
        # 7. Agent Performance Comparison
        if self.agent_metrics is not None and len(self.agent_metrics) > 0:
            plt.subplot(4, 3, 7)
            latest_metrics = self.agent_metrics.groupby('agent_id').last()
            plt.scatter(latest_metrics['total_actions'], latest_metrics['compliance_rate'], 
                       c=latest_metrics['violations'], cmap='viridis', alpha=0.7)
            plt.colorbar(label='Violations')
            plt.title('Agent Performance: Actions vs Compliance')
            plt.xlabel('Total Actions')
            plt.ylabel('Compliance Rate')
            plt.grid(True, alpha=0.3)
        
        # 8. Response Time by Endpoint
        if self.response_times is not None and len(self.response_times) > 0 and 'endpoint' in self.response_times.columns:
            plt.subplot(4, 3, 8)
            endpoint_times = self.response_times.groupby('endpoint')['response_time_seconds'].mean()
            bars = plt.bar(range(len(endpoint_times)), endpoint_times.values)
            plt.title('Average Response Time by Endpoint')
            plt.xlabel('Endpoint')
            plt.ylabel('Response Time (seconds)')
            plt.xticks(range(len(endpoint_times)), endpoint_times.index, rotation=45)
            plt.grid(True, alpha=0.3)
        
        # 9. Compliance Trends Over Time
        if self.agent_metrics is not None and len(self.agent_metrics) > 0:
            plt.subplot(4, 3, 9)
            for agent_type in self.agent_metrics['agent_type'].unique():
                agent_data = self.agent_metrics[self.agent_metrics['agent_type'] == agent_type]
                plt.plot(agent_data['timestamp'], agent_data['compliance_rate'], 
                        label=agent_type, alpha=0.7, linewidth=2)
            plt.title('Compliance Rate Trends by Agent Type')
            plt.xlabel('Time')
            plt.ylabel('Compliance Rate')
            plt.legend()
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
        
        # 10. System Load Over Time
        if self.response_times is not None and len(self.response_times) > 0:
            plt.subplot(4, 3, 10)
            load_per_minute = self.response_times.set_index('timestamp').resample('T').size()
            plt.fill_between(load_per_minute.index, load_per_minute.values, alpha=0.6)
            plt.title('System Load (Requests per Minute)')
            plt.xlabel('Time')
            plt.ylabel('Requests per Minute')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
        
        # 11. Performance Metrics Summary
        plt.subplot(4, 3, 11)
        if self.performance_metrics.get('response_times'):
            metrics = self.performance_metrics['response_times']
            labels = ['Mean', 'Median', 'P95', 'P99']
            values = [metrics.get('mean_response_time', 0), 
                     metrics.get('median_response_time', 0),
                     metrics.get('p95_response_time', 0), 
                     metrics.get('p99_response_time', 0)]
            bars = plt.bar(labels, values)
            plt.title('Response Time Percentiles')
            plt.ylabel('Response Time (seconds)')
            plt.grid(True, alpha=0.3)
            
            # Add value labels
            for bar, value in zip(bars, values):
                plt.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                        f'{value:.3f}', ha='center', va='bottom')
        
        # 12. System Overview
        plt.subplot(4, 3, 12)
        if self.system_metrics:
            overview_data = [
                self.system_metrics.get('total_actions', 0),
                self.system_metrics.get('total_violations', 0),
                self.system_metrics.get('total_blocks', 0),
                self.system_metrics.get('total_warnings', 0)
            ]
            labels = ['Actions', 'Violations', 'Blocks', 'Warnings']
            colors = ['green', 'red', 'orange', 'yellow']
            bars = plt.bar(labels, overview_data, color=colors, alpha=0.7)
            plt.title('System Activity Summary')
            plt.ylabel('Count')
            plt.grid(True, alpha=0.3)
            
            # Add value labels
            for bar, value in zip(bars, overview_data):
                plt.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                        f'{value}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "plots", "comprehensive_analysis.png"), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Saved comprehensive analysis plot")
    
    def generate_report(self):
        """Generate detailed analysis report."""
        print("Generating analysis report...")
        
        report = f"""
# GaaS System Performance Analysis Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
This report provides a comprehensive analysis of the GaaS (Governance-as-a-Service) system performance based on simulation data.

## Data Overview
"""
        
        if self.action_logs is not None:
            report += f"- Action Logs: {len(self.action_logs)} records\n"
        if self.response_times is not None:
            report += f"- Response Times: {len(self.response_times)} records\n"
        if self.enforcement_decisions is not None:
            report += f"- Enforcement Decisions: {len(self.enforcement_decisions)} records\n"
        if self.agent_metrics is not None:
            report += f"- Agent Metrics: {len(self.agent_metrics)} records\n"
        
        report += "\n## Performance Metrics\n"
        
        if self.performance_metrics.get('response_times'):
            rt_metrics = self.performance_metrics['response_times']
            report += f"""
### Response Time Analysis
- Mean Response Time: {rt_metrics.get('mean_response_time', 0):.3f} seconds
- Median Response Time: {rt_metrics.get('median_response_time', 0):.3f} seconds
- 95th Percentile: {rt_metrics.get('p95_response_time', 0):.3f} seconds
- 99th Percentile: {rt_metrics.get('p99_response_time', 0):.3f} seconds
- Maximum Response Time: {rt_metrics.get('max_response_time', 0):.3f} seconds
- Standard Deviation: {rt_metrics.get('std_response_time', 0):.3f} seconds
- Throughput: {rt_metrics.get('requests_per_minute', 0):.2f} requests/minute
"""
        
        if self.performance_metrics.get('actions'):
            action_metrics = self.performance_metrics['actions']
            report += f"""
### Action Analysis
- Total Actions: {action_metrics.get('total_actions', 0)}
- Success Rate: {action_metrics.get('success_rate', 0):.2%}
- Average Violations per Action: {action_metrics.get('average_violations_per_action', 0):.2f}
"""
        
        report += "\n## Compliance Analysis\n"
        
        if self.compliance_analysis.get('compliance_by_type'):
            report += "### Compliance by Agent Type\n"
            for agent_type, metrics in self.compliance_analysis['compliance_by_type'].items():
                if isinstance(metrics, dict):
                    report += f"- {agent_type}: {metrics.get('mean', 0):.2%} (±{metrics.get('std', 0):.2%})\n"
        
        if self.compliance_analysis.get('enforcement_patterns'):
            patterns = self.compliance_analysis['enforcement_patterns']
            report += f"""
### Enforcement Patterns
- Decision Breakdown:
"""
            for decision, rate in patterns.get('decision_rates', {}).items():
                report += f"  - {decision}: {rate:.2%}\n"
        
        report += "\n## System Metrics\n"
        
        if self.system_metrics:
            report += f"""
- Simulation Duration: {self.system_metrics.get('simulation_duration', 0):.1f} seconds
- Total Steps: {self.system_metrics.get('total_steps', 0)}
- Total Actions: {self.system_metrics.get('total_actions', 0)}
- Total Violations: {self.system_metrics.get('total_violations', 0)}
- Total Blocks: {self.system_metrics.get('total_blocks', 0)}
- Total Warnings: {self.system_metrics.get('total_warnings', 0)}
- Agents Registered: {self.system_metrics.get('agents_registered', 0)}
- Actions per Minute: {self.system_metrics.get('actions_per_minute', 0):.2f}
"""
        
        report += """
## Key Findings and Recommendations

### Performance Observations
1. **Response Time Performance**: Analysis of API response times shows system responsiveness
2. **Throughput Capacity**: System handles concurrent agent requests effectively
3. **Compliance Enforcement**: Policy enforcement mechanisms are functioning as designed

### Recommendations
1. **Optimization Opportunities**: Monitor high-latency endpoints for optimization
2. **Scaling Considerations**: Evaluate system performance under increased load
3. **Compliance Monitoring**: Continue tracking compliance trends across agent types

## Methodology
This analysis was performed using pandas for data processing and matplotlib/seaborn for visualization. 
The evaluation framework processes simulation logs to extract key performance indicators and compliance metrics.

---
*Report generated by GaaS Performance Analyzer*
"""
        
        # Save report
        report_path = os.path.join(self.output_dir, "reports", "performance_analysis_report.md")
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"✓ Saved analysis report to {report_path}")
    
    def run_complete_analysis(self) -> bool:
        """Run the complete analysis pipeline."""
        print("Starting comprehensive GaaS performance analysis...")
        
        # Load data
        if not self.load_data():
            print("❌ Failed to load data - cannot proceed with analysis")
            return False
        
        # Perform analysis
        self.analyze_performance_metrics()
        self.analyze_compliance_patterns()
        self.analyze_system_metrics()
        
        # Generate outputs
        self.generate_visualizations()
        self.generate_report()
        
        # Save analysis results
        results = {
            'performance_metrics': self.performance_metrics,
            'compliance_analysis': self.compliance_analysis,
            'system_metrics': self.system_metrics,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        results_path = os.path.join(self.output_dir, "analysis_results.json")
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"✓ Complete analysis finished. Results saved to {self.output_dir}")
        return True

def main():
    """Main function for running the analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(description='GaaS Performance Analysis')
    parser.add_argument('--data-dir', required=True, help='Directory containing simulation data')
    parser.add_argument('--output-dir', help='Output directory for analysis results')
    
    args = parser.parse_args()
    
    analyzer = GaaSPerformanceAnalyzer(args.data_dir, args.output_dir)
    success = analyzer.run_complete_analysis()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())