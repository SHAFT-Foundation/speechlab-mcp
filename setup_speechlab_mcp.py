#!/usr/bin/env python3
"""
Speechlab MCP Setup Script

This script guides users through the setup process for Speechlab MCP,
helping them configure the API key and install the package.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("speechlab-setup")

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8 or higher is required.")
        logger.error(f"   Current version: {sys.version}")
        return False
    logger.info(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def install_package(package_path="."):
    """Install the Speechlab MCP package."""
    try:
        logger.info("📦 Installing Speechlab MCP...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", package_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info("✅ Package installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install package: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False

def setup_api_key(api_key=None):
    """Set up the Speechlab API key."""
    if not api_key:
        logger.info("🔑 No API key provided. Checking environment...")
        api_key = os.environ.get("SPEECHLAB_API_KEY")
        
        if not api_key:
            logger.info("❓ No API key found in environment variables.")
            api_key = input("Enter your Speechlab API key (or leave empty to skip): ")
    
    if api_key:
        # Create .env file in current directory
        env_path = Path(".env")
        try:
            with open(env_path, "w") as f:
                f.write(f"SPEECHLAB_API_KEY={api_key}\n")
            logger.info(f"✅ API key saved to {env_path.absolute()}")
            
            # Also set the environment variable for current session
            os.environ["SPEECHLAB_API_KEY"] = api_key
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save API key: {e}")
            return False
    else:
        logger.warning("⚠️ No API key provided. You'll need to set SPEECHLAB_API_KEY environment variable later.")
        return False

def configure_for_claude(api_key=None):
    """Configure Speechlab MCP for Claude desktop."""
    if not api_key:
        api_key = os.environ.get("SPEECHLAB_API_KEY")
    
    if not api_key:
        logger.error("❌ No API key available for Claude configuration.")
        return False
    
    try:
        logger.info("🤖 Configuring for Claude desktop...")
        cmd = [sys.executable, "-m", "speechlab_mcp", "--api-key", api_key]
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info("✅ Claude configuration completed!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to configure for Claude: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to configure for Claude: {e}")
        return False

def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Speechlab MCP Setup")
    parser.add_argument("--api-key", help="Your Speechlab API key")
    parser.add_argument("--skip-install", action="store_true", help="Skip package installation")
    parser.add_argument("--skip-claude", action="store_true", help="Skip Claude desktop configuration")
    args = parser.parse_args()
    
    logger.info("🎬 Welcome to Speechlab MCP Setup!")
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install package
    if not args.skip_install:
        if not install_package():
            return 1
    else:
        logger.info("📦 Skipping package installation...")
    
    # Set up API key
    api_key_setup = setup_api_key(args.api_key)
    
    # Configure for Claude
    if not args.skip_claude:
        if not configure_for_claude(args.api_key):
            logger.warning("⚠️ Claude configuration failed or skipped.")
    else:
        logger.info("🤖 Skipping Claude desktop configuration...")
    
    logger.info("\n🎉 Setup completed!")
    logger.info("You can now use Speechlab MCP:")
    logger.info("- With Claude desktop (if configured)")
    logger.info("- By importing in your Python code: from speechlab_mcp import *")
    logger.info("- With the example scripts in the 'examples/' directory")
    
    if not api_key_setup:
        logger.info("\n⚠️ Remember to set your SPEECHLAB_API_KEY environment variable before using the package!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 