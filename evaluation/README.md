
# GaaS System Performance Evaluation

This module provides comprehensive performance evaluation and analysis for the Governance-as-a-Service (GaaS) system. It analyzes simulation data to generate insights about system performance, compliance patterns, and operational metrics.

## Overview

The evaluation framework processes real simulation data from the GaaS multi-agent system to provide:

- **Performance Analysis**: Response times, throughput, latency percentiles
- **Compliance Monitoring**: Agent compliance rates, policy enforcement patterns
- **System Metrics**: Overall system health, resource utilization, error rates
- **Visualization**: Comprehensive charts and plots for data interpretation
- **Reporting**: Detailed analysis reports with insights and recommendations

## Directory Structure

```
evaluation/
├── performance_analyzer.py    # Main analysis engine
├── run_evaluation.py         # Evaluation runner script
├── requirements.txt          # Python dependencies
├── README.md                # This documentation
├── data/                    # Input data directory
├── plots/                   # Generated visualizations
└── reports/                 # Analysis reports
```

## Data Requirements

The evaluation system expects the following CSV files from simulation runs:

### Input Data Files

1. **action_logs.csv** - Individual agent actions and results
   - `timestamp`: ISO format timestamp
   - `agent_id`: Unique agent identifier
   - `action_type`: Type of action performed
   - `action_description`: Description of the action
   - `resource_accessed`: Resource being accessed
   - `success`: Boolean success indicator
   - `violations_detected`: Number of violations found
   - `violations`: List of specific violations

2. **response_times.csv** - API response time measurements
   - `timestamp`: ISO format timestamp
   - `agent_id`: Agent making the request
   - `endpoint`: API endpoint called
   - `response_time_seconds`: Response time in seconds

3. **enforcement_decisions.csv** - Policy enforcement decisions
   - `timestamp`: ISO format timestamp
   - `agent_id`: Agent ID
   - `proposed_action`: Action that was proposed
   - `decision`: Enforcement decision (allow/block/warn)
   - `violation_count`: Number of violations
   - `violations`: List of violation types

4. **agent_metrics.csv** - Agent-specific performance metrics
   - `timestamp`: ISO format timestamp
   - `agent_id`: Agent identifier
   - `agent_type`: Type of agent (compliant/non-compliant/mixed/adaptive)
   - `total_actions`: Total actions performed
   - `compliant_actions`: Number of compliant actions
   - `violations`: Number of violations
   - `blocked_actions`: Number of blocked actions
   - `warnings_received`: Number of warnings
   - `compliance_rate`: Compliance percentage
   - `average_response_time`: Average response time

5. **simulation_summary.json** - Overall simulation summary
   - Simulation configuration and overall metrics

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run evaluation on simulation data:

```bash
python run_evaluation.py --data-dir /path/to/simulation/results
```

### Advanced Usage

Specify custom output directory:

```bash
python run_evaluation.py --data-dir ./simulation_results --output-dir ./my_analysis
```

Enable verbose logging:

```bash
python run_evaluation.py --data-dir ./data --verbose
```

### Framework Demonstration

View framework capabilities:

```bash
python run_evaluation.py --demo
```

## Analysis Components

### 1. Performance Metrics Analysis

- **Response Time Analysis**: Mean, median, percentiles (95th, 99th)
- **Throughput Metrics**: Requests per minute, system load patterns
- **Latency Distribution**: Response time histograms and trends
- **Endpoint Performance**: Per-endpoint response time analysis

### 2. Compliance Analysis

- **Compliance Rates**: By agent type and over time
- **Policy Enforcement**: Decision patterns (allow/block/warn)
- **Violation Patterns**: Types and frequency of violations
- **Agent Behavior**: Compliance trends and adaptations

### 3. System Metrics

- **Simulation Overview**: Duration, steps, total actions
- **Agent Statistics**: Registration success, activity levels
- **Error Analysis**: Failure rates and error patterns
- **Resource Utilization**: System load and capacity metrics

## Generated Outputs

### Visualizations

The system generates comprehensive plots including:

- Response time distribution histograms
- Performance trends over time
- Compliance rate comparisons by agent type
- Enforcement decision breakdowns (pie charts)
- System load and throughput graphs
- Agent performance scatter plots
- Violation pattern analysis

### Reports

- **Markdown Report**: Detailed analysis with findings and recommendations
- **JSON Results**: Machine-readable analysis results
- **Statistical Summaries**: Key metrics and percentiles

### File Outputs

```
evaluation_results/
├── plots/
│   └── comprehensive_analysis.png    # All visualizations
├── reports/
│   └── performance_analysis_report.md # Detailed report
└── analysis_results.json             # JSON results
```

## Key Features

### Robust Data Processing
- Handles missing data gracefully
- Validates data integrity
- Processes large datasets efficiently

### Comprehensive Analysis
- Multiple analysis dimensions
- Statistical rigor
- Trend identification

### Professional Visualizations
- Publication-quality plots
- Clear labeling and legends
- Multiple chart types

### Actionable Insights
- Performance bottleneck identification
- Compliance pattern analysis
- System optimization recommendations

## Integration with GaaS System

This evaluation module integrates with:

- **Backend System**: Analyzes API performance data
- **Client Simulation**: Processes multi-agent simulation results
- **Policy Engine**: Evaluates enforcement effectiveness

## Example Workflow

1. **Run Simulation**: Execute the GaaS multi-agent simulation
   ```bash
   cd ../client
   python run_simulation.py --duration 30 --agents 15
   ```

2. **Analyze Results**: Run performance evaluation
   ```bash
   cd ../evaluation
   python run_evaluation.py --data-dir ../client/simulation_results
   ```

3. **Review Outputs**: Examine generated plots and reports
   - View `plots/comprehensive_analysis.png`
   - Read `reports/performance_analysis_report.md`
   - Process `analysis_results.json` for further analysis

## Performance Considerations

- **Memory Usage**: Efficient pandas operations for large datasets
- **Processing Time**: Optimized analysis algorithms
- **Scalability**: Handles varying simulation sizes
- **Output Size**: Compressed visualizations and structured reports

## Troubleshooting

### Common Issues

1. **No Data Files Found**
   - Ensure simulation has been run successfully
   - Check data directory path
   - Verify file permissions

2. **Import Errors**
   - Install required dependencies: `pip install -r requirements.txt`
   - Check Python version compatibility

3. **Memory Issues**
   - For large datasets, consider processing in chunks
   - Monitor system memory usage

### Data Quality Checks

The system performs automatic data validation:
- Timestamp format verification
- Numeric field validation
- Missing value detection
- Data consistency checks

## Contributing

When extending the evaluation framework:

1. Follow existing code structure and patterns
2. Add comprehensive documentation
3. Include error handling and validation
4. Test with various data scenarios
5. Update this README with new features

## Dependencies

- `pandas>=2.0.0`: Data processing and analysis
- `matplotlib>=3.7.0`: Visualization and plotting
- `seaborn>=0.12.0`: Statistical visualizations
- `numpy>=1.24.0`: Numerical computations
