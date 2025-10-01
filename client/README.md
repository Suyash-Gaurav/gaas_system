# GaaS Multi-Agent Client Simulation

This directory contains the client simulation system for testing the Governance-as-a-Service (GaaS) backend with multiple agents exhibiting diverse behavioral patterns.

## Overview

The client simulation system provides:
- **Client Interface**: HTTP client for interacting with the GaaS FastAPI backend
- **Multi-Agent System**: 10-20 diverse agents with different compliance behaviors
- **Simulation Orchestration**: Main simulation loop with timing controls and lifecycle management
- **Performance Logging**: Comprehensive data collection for evaluation and analysis

## Architecture

```
client/
├── client_interface.py    # HTTP client for GaaS backend communication
├── agents.py             # Multi-agent system with diverse behaviors
├── simulation.py         # Main simulation orchestration
├── config.py            # Configuration management
├── run_simulation.py    # Main executable script
├── requirements.txt     # Python dependencies
└── README.md           # This documentation
```

## Agent Types

The simulation includes four distinct agent types:

1. **Compliant Agents** (25%): Always follow governance policies and respect enforcement decisions
2. **Non-Compliant Agents** (17%): Frequently violate policies and ignore enforcement decisions
3. **Mixed Behavior Agents** (50%): Variable compliance based on random probability
4. **Adaptive Learning Agents** (8%): Learn from enforcement decisions and adapt behavior over time

## Prerequisites

1. **GaaS Backend Running**: The FastAPI backend must be running and accessible
2. **Python 3.8+**: Required for the client simulation
3. **Network Connectivity**: Client must be able to reach the backend

## Installation

1. Install Python dependencies:
```bash
cd gaas_system/client
pip install -r requirements.txt
```

2. Ensure the GaaS backend is running:
```bash
cd gaas_system/backend
python start_server.py
```

## Usage

### Basic Usage

Run the simulation with default settings:
```bash
python run_simulation.py
```

This will:
- Connect to backend at `http://localhost:8000`
- Run simulation for 30 minutes
- Use 15 agents with mixed behavioral patterns
- Save results to `./simulation_results/`

### Advanced Usage

#### Custom Duration and Agent Count
```bash
python run_simulation.py --duration 60 --agents 20
```

#### Connect to Remote Backend
```bash
python run_simulation.py --backend-host 192.168.1.100 --backend-port 8080
```

#### Custom Output Directory
```bash
python run_simulation.py --output-dir /tmp/gaas_results
```

#### Debug Mode
```bash
python run_simulation.py --log-level DEBUG
```

#### Environment Variables
```bash
export GAAS_BACKEND_HOST=localhost
export GAAS_BACKEND_PORT=8000
export GAAS_SIMULATION_DURATION=45
export GAAS_NUM_AGENTS=18
python run_simulation.py --use-env
```

### Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--backend-host` | localhost | Backend hostname |
| `--backend-port` | 8000 | Backend port |
| `--backend-protocol` | http | Backend protocol (http/https) |
| `--duration` | 30 | Simulation duration (minutes) |
| `--agents` | 15 | Number of agents |
| `--interval` | 2.0 | Step interval (seconds) |
| `--max-concurrent` | 5 | Max concurrent agents |
| `--output-dir` | ./simulation_results | Output directory |
| `--log-level` | INFO | Logging level |
| `--log-file` | client_simulation.log | Log file path |
| `--use-env` | false | Use environment variables |

## Output Files

The simulation generates several output files for analysis:

### CSV Files
- `action_logs.csv`: Detailed log of all agent actions
- `response_times.csv`: API response time measurements
- `enforcement_decisions.csv`: All enforcement decisions made
- `agent_metrics.csv`: Per-agent performance metrics

### JSON Files
- `simulation_summary.json`: Complete simulation summary and metrics

### Log Files
- `client_simulation.log`: Detailed simulation logs

## Data Collection

The simulation collects comprehensive performance data:

### Response Time Metrics
- API call latencies for all endpoints
- Per-agent response time tracking
- Overall system performance metrics

### Compliance Metrics
- Enforcement decision rates (allow/warn/block)
- Violation detection rates
- Agent compliance patterns over time

### Behavioral Metrics
- Action patterns by agent type
- Learning progression for adaptive agents
- Policy violation trends

## API Endpoints Used

The client simulation interacts with these GaaS backend endpoints:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/register_agent` | Register agents with the system |
| POST | `/submit_action_log` | Submit agent action logs |
| GET | `/enforcement_decision` | Get enforcement decisions |
| POST | `/upload_policy` | Upload governance policies |
| GET | `/compliance_report` | Generate compliance reports |
| GET | `/health` | Check backend health |

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GAAS_BACKEND_HOST` | localhost | Backend hostname |
| `GAAS_BACKEND_PORT` | 8000 | Backend port |
| `GAAS_BACKEND_PROTOCOL` | http | Backend protocol |
| `GAAS_CONNECTION_TIMEOUT` | 30 | Connection timeout (seconds) |
| `GAAS_MAX_RETRIES` | 3 | Maximum retry attempts |
| `GAAS_RETRY_DELAY` | 1.0 | Retry delay (seconds) |
| `GAAS_SIMULATION_DURATION` | 30 | Simulation duration (minutes) |
| `GAAS_STEP_INTERVAL` | 2.0 | Step interval (seconds) |
| `GAAS_NUM_AGENTS` | 15 | Number of agents |
| `GAAS_MAX_CONCURRENT` | 5 | Max concurrent agents |
| `GAAS_LOG_INTERVAL` | 10 | Logging interval (steps) |
| `GAAS_OUTPUT_DIR` | ./simulation_results | Output directory |
| `GAAS_LOG_LEVEL` | INFO | Logging level |

## Troubleshooting

### Backend Connection Issues
```
ERROR: Cannot connect to backend. Please ensure the GaaS backend is running.
```
**Solution**: Start the backend server:
```bash
cd gaas_system/backend
python start_server.py
```

### Agent Registration Failures
```
Failed to register agent X: Agent with ID X already exists
```
**Solution**: This is normal if restarting simulation quickly. The backend maintains agent registry in memory.

### Performance Issues
If simulation runs slowly:
1. Reduce `--max-concurrent` value
2. Increase `--interval` value
3. Reduce `--agents` count
4. Check backend server resources

### Output Directory Permissions
```
PermissionError: [Errno 13] Permission denied: './simulation_results'
```
**Solution**: Ensure write permissions or use different output directory:
```bash
python run_simulation.py --output-dir /tmp/gaas_results
```

## Integration with Backend

The client simulation is designed to work with the existing GaaS backend:

1. **Schema Compatibility**: Uses exact data schemas from `backend/app/schemas.py`
2. **Endpoint Compatibility**: Matches all FastAPI endpoints in `backend/app/main.py`
3. **Configuration Alignment**: Uses same host/port settings as backend configuration

## Performance Considerations

- **Concurrent Agents**: Limited by `max_concurrent_agents` setting to prevent overwhelming backend
- **Step Intervals**: Configurable timing to balance realism and performance
- **Retry Logic**: Built-in retry mechanism for handling temporary network issues
- **Memory Usage**: Logs are accumulated in memory and written at simulation end

## Development

### Adding New Agent Types

1. Create new agent class inheriting from `BaseAgent`
2. Implement `generate_action()` and `decide_action_execution()` methods
3. Add to `create_agent_population()` function in `agents.py`

### Extending Metrics Collection

1. Add new fields to `AgentMetrics` or `SimulationMetrics` dataclasses
2. Update logging methods in `PerformanceLogger`
3. Modify CSV output generation in `save_logs_to_files()`

### Custom Behaviors

Agent behaviors can be customized by:
- Modifying action generation patterns
- Adjusting compliance probabilities
- Adding new context parameters
- Implementing learning algorithms

## License

This client simulation system is part of the GaaS project and follows the same licensing terms.