#!/usr/bin/env python3
"""
Web Traffic Simulator Script

This script simulates user sessions and click events on a target endpoint to artificially generate traffic.
Configuration is loaded from config.json.
"""
import requests
import random
import time
import os
import json
import logging
import signal
from typing import List, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --------------------------------------------------------------
# Configure logging
# --------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------
# Global state for graceful shutdown
# --------------------------------------------------------------
shutdown_requested = False
simulation_stats = {
    'total_attempts': 0,
    'successful_visits': 0,
    'failed_visits': 0,
    'start_time': None
}

def signal_handler(signum: int, frame) -> None:
    """Handle shutdown signals gracefully."""
    global shutdown_requested
    shutdown_requested = True
    logger.info("Shutdown signal received. Completing current simulation and exiting gracefully...")

def print_final_stats() -> None:
    """Print final statistics of the simulation campaign."""
    if simulation_stats['start_time']:
        duration = time.time() - simulation_stats['start_time']
        logger.info("=" * 50)
        logger.info("SIMULATION CAMPAIGN COMPLETED")
        logger.info("=" * 50)
        logger.info("Total attempts: %d", simulation_stats['total_attempts'])
        logger.info("Successful visits: %d", simulation_stats['successful_visits'])
        logger.info("Failed visits: %d", simulation_stats['failed_visits'])
        if simulation_stats['total_attempts'] > 0:
            success_rate = (simulation_stats['successful_visits'] / simulation_stats['total_attempts']) * 100
            logger.info("Success rate: %.1f%%", success_rate)
        logger.info("Campaign duration: %.1f seconds", duration)
        logger.info("=" * 50)

# --------------------------------------------------------------
# Load configuration from JSON file
# --------------------------------------------------------------
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.json")

def load_config(filepath: str = CONFIG_FILE) -> Dict[str, Any]:
    """
    Load simulation settings from a JSON configuration file.

    Raises:
        FileNotFoundError: If the config file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    Returns:
        dict: Configuration settings.
    """
    if not os.path.exists(filepath):
        logger.error("Configuration file not found: %s", filepath)
        raise FileNotFoundError(f"Configuration file not found: {filepath}")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in config file: %s", e)
        raise
    return config

# Load settings
try:
    config = load_config()
except Exception:
    logger.critical("Failed to load configuration. Exiting.")
    exit(1)

# Required settings
try:
    DETAIL_URL = config["detail_url"]
    CLICK_URL = config["click_url"]
    USER_ID = config["user_id"]
except KeyError as e:
    logger.critical("Missing required config key: %s", e)
    exit(1)

# Optional settings with defaults
RUN_COUNT = config.get("run_count", 20)
agents_file = config.get("agents_file", "rotation_agents.txt")
# If agents_file is relative, make it relative to config directory
if not os.path.isabs(agents_file):
    AGENTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", agents_file)
else:
    AGENTS_FILE = agents_file
MIN_DELAY = config.get("min_delay", 1)
MAX_DELAY = config.get("max_delay", 300)


def create_session_with_retries() -> requests.Session:
    """
    Create a requests.Session with automatic retries for transient errors.
    """
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def random_ip() -> str:
    """Generate a random public IPv4 address, excluding private and reserved ranges."""
    while True:
        octets = [
            random.randint(1, 223),
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(1, 254)
        ]
        first, second = octets[0], octets[1]
        # skip private/reserved
        if (
            first == 10 or
            first == 127 or
            (first == 169 and second == 254) or
            (first == 172 and 16 <= second <= 31) or
            (first == 192 and second == 168)
        ):
            continue
        return ".".join(map(str, octets))


def load_user_agents(filepath: str = AGENTS_FILE) -> List[str]:
    """Load User-Agent strings from a file (one per line)."""
    if not os.path.exists(filepath):
        logger.error("User-Agent file not found: %s", filepath)
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        agents = [line.strip() for line in f if line.strip()]
    if not agents:
        logger.warning("No user agents loaded from file.")
    return agents


def simulate_session(session: requests.Session, user_agents: List[str]) -> bool:
    """
    Simulate a single user session:
      1. Load detail page to register a view
      2. Send a click event with simulated IP and User-Agent

    Returns:
        bool: True if simulation completed successfully, False otherwise
    """
    ip_addr = random_ip()
    ua = random.choice(user_agents)
    logger.info("Sending visit simulation: IP=%s UA=%s", ip_addr, ua)

    headers = {"User-Agent": ua}

    # Step 1: register page view
    try:
        session.get(DETAIL_URL, headers=headers, timeout=10)
        logger.info("Page visit registered successfully")
    except requests.RequestException as e:
        logger.error("Failed to register page visit: %s", e)
        return False

    # Step 2: register click event
    params = {"id": USER_ID, "ipaddress": ip_addr, "_": random.randint(int(1e12), int(2e12))}
    headers.update({"Referer": DETAIL_URL, "Accept": "*/*"})
    try:
        response = session.get(CLICK_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info("Visit simulation completed successfully: status=%s", response.status_code)
        return True
    except requests.HTTPError as e:
        logger.error("Click endpoint HTTP error: %s", e)
        return False
    except requests.RequestException as e:
        logger.error("Failed to send click event: %s", e)
        return False


def run_simulation(count: int = RUN_COUNT, min_delay: float = MIN_DELAY, max_delay: float = MAX_DELAY) -> None:
    """
    Execute the traffic simulation campaign with randomized delays between visits.

    Args:
        count (int): Number of visit simulations to execute.
        min_delay (float): Minimum wait time between visits (seconds).
        max_delay (float): Maximum wait time between visits (seconds).
    """
    global shutdown_requested, simulation_stats

    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    user_agents = load_user_agents()
    if not user_agents:
        logger.critical("No User-Agent strings available. Exiting.")
        return

    session = create_session_with_retries()
    simulation_stats['start_time'] = time.time()

    logger.info("Starting traffic simulation campaign: %d visits planned", count)
    logger.info("Press Ctrl+C to stop gracefully")

    try:
        for i in range(1, count + 1):
            if shutdown_requested:
                logger.info("Shutdown requested, stopping after current simulation...")
                break

            logger.info("Starting visit simulation %d/%d", i, count)
            simulation_stats['total_attempts'] += 1

            success = simulate_session(session, user_agents)
            if success:
                simulation_stats['successful_visits'] += 1
            else:
                simulation_stats['failed_visits'] += 1

            # Check for shutdown request before delay
            if shutdown_requested or i == count:
                break

            delay = random.uniform(min_delay, max_delay)
            logger.info("Waiting %.1f seconds before next visit simulation", delay)

            # Sleep in small chunks to allow quick response to shutdown
            sleep_chunks = int(delay)
            sleep_remainder = delay - sleep_chunks

            for _ in range(sleep_chunks):
                if shutdown_requested:
                    break
                time.sleep(1)

            if not shutdown_requested and sleep_remainder > 0:
                time.sleep(sleep_remainder)

    except KeyboardInterrupt:
        logger.warning("Keyboard interrupt received, shutting down gracefully...")
    except Exception as e:
        logger.critical("Unexpected error in simulation campaign: %s", e)
    finally:
        print_final_stats()
