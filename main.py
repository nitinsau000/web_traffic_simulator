#!/usr/bin/env python3
"""
Web Traffic Simulator Runner

Entry point for running traffic simulation campaigns.
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

from src.web_traffic_simulator import run_simulation

if __name__ == "__main__":
    run_simulation()