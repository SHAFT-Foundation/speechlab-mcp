#!/usr/bin/env python3
"""
Integration Example for Speechlab MCP

This example shows how to use Speechlab MCP in a standalone Python application,
without requiring Claude desktop or any specific AI assistant.

Requirements:
- speechlab_mcp package installed
- SPEECHLAB_API_KEY environment variable set
"""

import os
import time
import logging
from dotenv import load_dotenv
from speechlab_mcp.server import (
    create_project_and_dub,
    get_project,
    upload_media,
    start_dubbing,
    check_dubbing_status,
    download_dubbing_result,
    generate_sharing_link
)
from mcp.types import TextContent  # Required for handling responses

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("speechlab-integration")

# Load API key from environment
load_dotenv()
API_KEY = os.getenv("SPEECHLAB_API_KEY")

if not API_KEY:
    raise ValueError("SPEECHLAB_API_KEY environment variable is required")

def extract_project_id(text_content: TextContent) -> str:
    """Extract project ID from a TextContent response."""
    # Parse the ID from the response text
    for line in text_content.text.split('\n'):
        if line.startswith("ID:"):
            return line.split("ID:")[1].strip()
    return None

def wait_for_completion(project_id: str, max_attempts: int = 20, delay: int = 15) -> bool:
    """
    Poll the project status until it completes or exceeds max attempts.
    
    Args:
        project_id: The project ID to check
        max_attempts: Maximum number of status checks
        delay: Seconds to wait between checks
        
    Returns:
        True if project completed successfully, False otherwise
    """
    logger.info(f"Waiting for project {project_id} to complete...")
    
    for attempt in range(max_attempts):
        logger.info(f"Checking status (attempt {attempt+1}/{max_attempts})...")
        response = check_dubbing_status(project_id)
        
        # Look for completion or failure indicators in the status
        if "Status: COMPLETE" in response.text:
            logger.info("Project completed successfully!")
            return True
        elif "Status: FAILED" in response.text:
            logger.error("Project processing failed!")
            return False
            
        # Continue waiting if still in progress
        logger.info(f"Project still processing. Current status: {response.text}")
        logger.info(f"Waiting {delay} seconds before next check...")
        time.sleep(delay)
    
    logger.warning(f"Maximum attempts ({max_attempts}) reached without completion")
    return False

def run_example_workflow(video_path: str = None):
    """
    Run a complete example workflow from project creation to downloading results.
    
    Args:
        video_path: Optional path to a video file for uploading
    """
    logger.info("Starting Speechlab integration example")
    
    # 1. Create a new project
    logger.info("Creating a new dubbing project...")
    project_response = create_project_and_dub(
        name="Integration Example",
        source_language="en",
        target_language="es",
        source_file=video_path  # Will be None if not provided
    )
    logger.info(f"Project created: {project_response.text}")
    
    # Extract the project ID
    project_id = extract_project_id(project_response)
    if not project_id:
        logger.error("Failed to extract project ID from response")
        return
    
    # 2. Upload media if not already uploaded during creation
    if video_path and "source_file" not in project_response.text.lower():
        logger.info(f"Uploading video file: {video_path}")
        upload_response = upload_media(project_id, video_path)
        logger.info(f"Upload result: {upload_response.text}")
    
    # 3. Start the dubbing process
    logger.info("Starting dubbing process...")
    dub_response = start_dubbing(project_id)
    logger.info(f"Dubbing started: {dub_response.text}")
    
    # 4. Wait for the project to complete
    if wait_for_completion(project_id):
        # 5. Generate a sharing link
        logger.info("Generating sharing link...")
        link_response = generate_sharing_link(project_id)
        logger.info(f"Sharing link: {link_response.text}")
        
        # 6. Download the result
        logger.info("Downloading dubbed video...")
        download_dir = os.path.expanduser("~/Downloads")
        download_response = download_dubbing_result(project_id, download_dir)
        logger.info(f"Download result: {download_response.text}")
        
        logger.info("Workflow completed successfully!")
    else:
        logger.error("Workflow did not complete successfully.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Speechlab MCP Integration Example")
    parser.add_argument("--video", help="Path to video file to process", default=None)
    args = parser.parse_args()
    
    run_example_workflow(args.video) 