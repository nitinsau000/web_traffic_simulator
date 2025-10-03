# Web Traffic Simulator

A professional Python tool for simulating realistic web traffic patterns on web applications. Designed for legitimate testing, development, and research purposes - including bypassing IP-based restrictions, testing web services, and analyzing traffic behavior in online systems.

## Why this tool?
This tool was originally developed after I discovered a flaw in an IP-based visitor counting mechanism used by a web application. The system was intended to track unique visits, but due to improper validation, it could be bypassed. This script was created to simulate artificial visits and test the flaw in a controlled and reproducible way.

## Overview

The simulator replicates authentic user behavior by generating realistic web traffic with proper timing, headers, and network characteristics. It enables effective testing of how applications respond to varied traffic patterns and helps identify weaknesses in traffic handling logic.

## What it does

The simulator creates authentic user sessions by:

- **Page View Simulation**: Generates realistic page load requests
- **Click Event Tracking**: Simulates user interaction events with proper parameters
- **IP Address Rotation**: Uses randomized public IP addresses for realistic traffic distribution
- **User-Agent Rotation**: Cycles through authentic browser User-Agent strings
- **Realistic Timing**: Implements human-like delays between interactions
- **Session Management**: Maintains proper HTTP session state

## Quick Start

1. **Install Python requirements:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your configuration:**
   Edit `config/config.json` with your target URLs and settings:

   ```json
   {
     "detail_url": "https://example.com/page/detail",
     "click_url": "https://example.com/api/click",
     "user_id": "your_user_id_here",
     "run_count": 20,
     "min_delay": 1,
     "max_delay": 300
   }
   ```

3. **Add User-Agent strings:**
   Put real browser User-Agent strings in `config/rotation_agents.txt` (one per line)

4. **Run the simulation:**

   ```bash
   python main.py
   ```

5. **Monitor and Control:**
   - Press `Ctrl+C` to stop gracefully at any time
   - The tool will complete the current simulation and show final statistics
   - All activity is logged with timestamps for monitoring

## Configuration Options

| Setting       | Description                                    | Default               |
| ------------- | ---------------------------------------------- | --------------------- |
| `detail_url`  | Target page URL for view simulation (required) | -                     |
| `click_url`   | Click tracking endpoint URL (required)         | -                     |
| `user_id`     | Application user/session ID (required)         | -                     |
| `run_count`   | Number of traffic simulations to execute       | 20                    |
| `agents_file` | File containing User-Agent strings             | "rotation_agents.txt" |
| `min_delay`   | Minimum delay between requests (seconds)       | 1                     |
| `max_delay`   | Maximum delay between requests (seconds)       | 300                   |

## Features

- **Intelligent IP Generation**: Creates realistic public IPv4 addresses excluding private ranges
- **Robust Retry Logic**: Automatic retry handling for transient network errors
- **Authentic Headers**: Proper referrer, accept, and user-agent headers
- **Comprehensive Error Handling**: Graceful handling of network and application errors
- **Detailed Logging**: Complete activity logging with configurable levels
- **Cache Prevention**: Timestamp-based cache busting for accurate testing
- **Type Safety**: Full Python type hints for better code reliability
- **Graceful Shutdown**: Safe interruption with statistics and proper cleanup

## File Structure

```
web_traffic_simulator/
├── main.py                          # Entry point script
├── src/                             # Source code package
│   ├── __init__.py                  # Package initialization
│   └── web_traffic_simulator.py     # Main simulation library
├── config/                          # Configuration files (gitignored - create manually)
│   ├── config.json                  # Application settings
│   └── rotation_agents.txt          # User-Agent strings
├── requirements.txt                 # Python dependencies
├── .gitignore                       # Git ignore rules
├── LICENSE                          # CC BY-NC-SA 4.0 License
└── README.md                        # This file
```

## How it works

1. **Campaign Initialization**: Sets up signal handlers and loads configuration
2. **Page View Registration**: Loads the target page to establish a valid session
3. **Click Event Simulation**: Sends interaction events with:
   - Randomized public IP address for geographic distribution
   - Authentic browser User-Agent string from configured list
   - Unique timestamp parameters to prevent caching
   - Proper HTTP referrer headers for realistic traffic flow
4. **Statistics Tracking**: Monitors success rates and performance metrics
5. **Graceful Completion**: Shows detailed campaign statistics upon completion or interruption

### Campaign Statistics

Upon completion or interruption, the simulator displays comprehensive statistics, for example:

```
==================================================
SIMULATION CAMPAIGN COMPLETED
==================================================
Total attempts: 45
Successful visits: 43
Failed visits: 2
Success rate: 95.6%
Campaign duration: 342.1 seconds
==================================================
```

## Example User-Agent Configuration

Your `config/rotation_agents.txt` should contain authentic browser User-Agent strings, one per line:

```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

## Safety & Compliance Features

- **Rate Limiting**: Configurable delays prevent overwhelming target servers
- **Public IP Only**: Excludes private and reserved IP address ranges
- **Graceful Shutdown**: Safe interruption with Ctrl+C, completes current simulation before stopping
- **Campaign Statistics**: Detailed success/failure tracking and performance metrics
- **Timeout Protection**: Request timeouts prevent hanging connections
- **Error Recovery**: Robust error handling maintains stability
- **Signal Handling**: Proper SIGINT and SIGTERM handling for clean exits

## Legitimate Use Cases

- **Application Testing**: Load testing and performance analysis
- **Analytics Validation**: Testing tracking implementations and data collection
- **Development**: Testing user interaction flows in controlled environments
- **Research**: Academic research on web traffic patterns and user behavior
- **Quality Assurance**: Automated testing of web application functionality

## Requirements

- Python 3.12 or higher
- `requests` library (install with: `pip install -r requirements.txt`)
- Internet connection
- Valid target application URLs for testing

---

## Legal Notice & Responsible Use

**IMPORTANT**: This tool is designed exclusively for legitimate testing and development purposes. Users must:

- Only test applications they own or have explicit permission to test
- Comply with all applicable terms of service and legal requirements
- Respect rate limits and server capacity
- Use responsibly and ethically

**Prohibited Uses**:

- Unauthorized traffic generation
- Circumventing security measures
- Violating terms of service
- Any illegal or malicious activities

The developer assumes no responsibility for misuse of this tool. Users are solely responsible for ensuring their use complies with all applicable laws and regulations.
