#!/usr/bin/env python3
"""
Direct Client Example for Speechlab MCP

This example shows how to use the SpeechlabClient directly,
without requiring the MCP Claude plugin or any AI assistant.

Requirements:
- speechlab_mcp package installed
- SPEECHLAB_API_KEY environment variable set
"""

import os
import time
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

from speechlab_mcp.client import SpeechlabClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("speechlab-client-example")

# Load environment variables
load_dotenv()

def status_callback(attempt, project_data):
    """
    Callback function for status updates.
    
    Args:
        attempt: The attempt number (0-based)
        project_data: The project data from the API
    """
    status = project_data.get("job", {}).get("status", "UNKNOWN")
    
    # You could implement custom logic here, such as:
    # - Sending notifications
    # - Updating a progress bar in a UI
    # - Logging to a database
    # - Triggering other processes
    
    logger.info(f"Status update (attempt {attempt+1}): {status}")

def validate_file(file_path):
    """
    Validate that a file exists and is a valid media file.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        Absolute path to the file
    """
    if not file_path:
        raise ValueError("No file path provided")
    
    path = Path(file_path).expanduser().absolute()
    
    if not path.exists():
        raise ValueError(f"File does not exist: {path}")
    
    # Simple extension check
    valid_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.wmv', '.m4v']
    if path.suffix.lower() not in valid_extensions:
        logger.warning(f"Warning: File extension {path.suffix} might not be a supported video format")
    
    return str(path)

def run_dubbing_workflow(
    video_path,
    project_name,
    source_language,
    target_language,
    output_dir=None,
    api_key=None,
    base_url=None
):
    """
    Run a complete dubbing workflow using SpeechlabClient.
    
    Args:
        video_path: Path to the video file
        project_name: Name for the project
        source_language: Source language code (e.g., 'en')
        target_language: Target language code (e.g., 'es')
        output_dir: Directory to save output files
        api_key: Speechlab API key (optional)
        base_url: Speechlab API base URL (optional)
        
    Returns:
        Dict with workflow results
    """
    logger.info(f"Starting dubbing workflow for video: {video_path}")
    
    # Validate input file
    try:
        validated_path = validate_file(video_path)
        logger.info(f"Validated video file: {validated_path}")
    except ValueError as e:
        logger.error(f"File validation error: {e}")
        return {"status": "ERROR", "message": str(e)}
    
    # Create directory for output if needed
    if output_dir:
        output_path = Path(output_dir).expanduser().absolute()
        output_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {output_path}")
    else:
        output_path = Path.home() / "Downloads"
        logger.info(f"Using default output directory: {output_path}")
    
    # Initialize client
    try:
        with SpeechlabClient(api_key=api_key, base_url=base_url) as client:
            results = {}
            
            # 1. Create project
            logger.info(f"Creating project '{project_name}' ({source_language} → {target_language})")
            project = client.create_project(
                name=project_name,
                source_language=source_language,
                target_language=target_language
            )
            project_id = project.get("projectId")
            if not project_id:
                raise ValueError("Failed to get project ID from response")
            
            results["project_id"] = project_id
            logger.info(f"Project created successfully! ID: {project_id}")
            
            # 2. Upload media
            logger.info(f"Uploading video: {validated_path}")
            upload_result = client.upload_media(
                project_id=project_id,
                file_path=validated_path
            )
            logger.info("Video uploaded successfully!")
            
            # 3. Start dubbing
            logger.info("Starting dubbing process...")
            dub_result = client.start_dubbing(project_id=project_id)
            logger.info("Dubbing process started successfully!")
            
            # 4. Wait for completion
            logger.info("Waiting for dubbing to complete...")
            completion = client.wait_for_completion(
                project_id=project_id,
                max_attempts=30,
                delay_seconds=20,
                callback=status_callback
            )
            
            if completion:
                logger.info("Dubbing completed successfully!")
                results["status"] = "COMPLETE"
                
                # 5. Generate sharing link
                logger.info("Generating sharing link...")
                sharing_link = client.generate_sharing_link(project_id=project_id)
                results["sharing_link"] = sharing_link
                logger.info(f"Sharing link: {sharing_link}")
                
                # 6. Download the result
                logger.info(f"Downloading result to {output_path}...")
                download_path = client.download_result(
                    project_id=project_id,
                    output_directory=str(output_path)
                )
                results["output_file"] = download_path
                logger.info(f"Downloaded to: {download_path}")
            else:
                logger.error("Dubbing did not complete within the expected time.")
                results["status"] = "TIMEOUT"
            
            return results
    except Exception as e:
        logger.exception(f"Error in dubbing workflow: {e}")
        return {"status": "ERROR", "message": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Speechlab Client Example")
    parser.add_argument("--video", required=True, help="Path to the video file to dub")
    parser.add_argument("--name", default="Client Example", help="Project name")
    parser.add_argument("--source", default="en", help="Source language code (default: en)")
    parser.add_argument("--target", default="es", help="Target language code (default: es)")
    parser.add_argument("--output", help="Output directory for downloaded files")
    parser.add_argument("--api-key", help="Speechlab API key (will use SPEECHLAB_API_KEY env var if not provided)")
    parser.add_argument("--api-url", help="Speechlab API base URL (will use SPEECHLAB_API_BASE_URL env var if not provided)")
    
    args = parser.parse_args()
    
    result = run_dubbing_workflow(
        video_path=args.video,
        project_name=args.name,
        source_language=args.source,
        target_language=args.target,
        output_dir=args.output,
        api_key=args.api_key,
        base_url=args.api_url
    )
    
    if result["status"] == "COMPLETE":
        print("\n✅ Dubbing workflow completed successfully!")
        print(f"📋 Project ID: {result['project_id']}")
        print(f"🔗 Sharing Link: {result['sharing_link']}")
        print(f"📁 Output File: {result['output_file']}")
    else:
        print(f"\n❌ Dubbing workflow failed: {result.get('message', 'Unknown error')}")

if __name__ == "__main__":
    main() 