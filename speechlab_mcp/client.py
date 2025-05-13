"""
Speechlab Client

A programmatic client wrapper for the Speechlab API that doesn't require the MCP structure.
This allows for more direct API usage in regular Python applications.
"""

import os
import httpx
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from speechlab_mcp.utils import (
    make_error,
    make_output_path,
    make_output_file,
    handle_input_file,
)
from speechlab_mcp import __version__

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SpeechlabClient:
    """
    Client for interacting with the Speechlab API.
    
    This client provides direct access to Speechlab APIs without requiring
    the MCP framework, making it suitable for use in regular Python applications.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0
    ):
        """
        Initialize the Speechlab client.
        
        Args:
            api_key: The Speechlab API key. If not provided, will look for SPEECHLAB_API_KEY env var
            base_url: The base URL for the Speechlab API. Defaults to http://localhost/v1
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.environ.get("SPEECHLAB_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Provide it to the constructor or set SPEECHLAB_API_KEY environment variable.")
            
        self.base_url = base_url or os.environ.get("SPEECHLAB_API_BASE_URL", "http://localhost/v1")
        self.timeout = timeout
        
        # Create HTTP client
        self.client = httpx.Client(
            headers={
                "User-Agent": f"Speechlab-MCP/{__version__}",
                "Authorization": f"Bearer {self.api_key}"
            },
            timeout=timeout
        )
        
        logger.info(f"[🤖 Speechlab] Client initialized with base URL: {self.base_url}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def create_project(
        self,
        name: str,
        source_language: str,
        target_language: str
    ) -> Dict[str, Any]:
        """
        Create a new dubbing project.
        
        Args:
            name: Name of the project
            source_language: Source language code (e.g., 'en' for English)
            target_language: Target language code (e.g., 'es' for Spanish)
            
        Returns:
            Dict containing the created project details
        """
        # Map special language codes if needed
        api_target_language = target_language
        if target_language == "es":
            api_target_language = "es_la"
        
        logger.info(f"[🤖 Speechlab] Creating project '{name}' with source '{source_language}' and target '{api_target_language}'")
        
        try:
            response = self.client.post(
                f"{self.base_url}/projects/createProjectAndDub",
                json={
                    "name": name,
                    "sourceLanguage": source_language,
                    "targetLanguage": api_target_language,
                    "dubAccent": api_target_language,
                    "voiceMatchingMode": "source",
                    "unitType": "whiteGlove",
                    "thirdPartyID": f"client_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                }
            )
            response.raise_for_status()
            project_data = response.json()
            logger.info(f"[🤖 Speechlab] ✅ Project created successfully: {project_data}")
            return project_data
        except httpx.HTTPStatusError as e:
            logger.error(f"[🤖 Speechlab] ❌ HTTP error when creating project: {e}")
            logger.error(f"[🤖 Speechlab] Status: {e.response.status_code}")
            logger.error(f"[🤖 Speechlab] Response: {e.response.text}")
            raise
    
    def upload_media(
        self,
        project_id: str,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Upload a media file to a project.
        
        Args:
            project_id: ID of the project to upload to
            file_path: Path to the media file
            
        Returns:
            Dict containing the upload result
        """
        logger.info(f"[🤖 Speechlab] Uploading media file {file_path} to project {project_id}")
        
        try:
            # Validate the file
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise ValueError(f"File does not exist: {file_path}")
            
            with open(file_path_obj, "rb") as f:
                files = {"file": (file_path_obj.name, f, "video/mp4")}
                response = self.client.post(
                    f"{self.base_url}/projects/{project_id}/upload",
                    files=files
                )
                response.raise_for_status()
                upload_data = response.json()
                
            logger.info(f"[🤖 Speechlab] ✅ File uploaded successfully: {upload_data}")
            return upload_data
        except httpx.HTTPStatusError as e:
            logger.error(f"[🤖 Speechlab] ❌ HTTP error when uploading media: {e}")
            raise
        
    def start_dubbing(self, project_id: str) -> Dict[str, Any]:
        """
        Start the dubbing process for a project.
        
        Args:
            project_id: ID of the project to start dubbing
            
        Returns:
            Dict containing the result of the dubbing request
        """
        logger.info(f"[🤖 Speechlab] Starting dubbing process for project {project_id}")
        
        try:
            response = self.client.post(
                f"{self.base_url}/projects/{project_id}/dub"
            )
            response.raise_for_status()
            dub_data = response.json()
            
            logger.info(f"[🤖 Speechlab] ✅ Dubbing process started: {dub_data}")
            return dub_data
        except httpx.HTTPStatusError as e:
            logger.error(f"[🤖 Speechlab] ❌ HTTP error when starting dubbing: {e}")
            raise
    
    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """
        Get the current status of a project.
        
        Args:
            project_id: ID of the project to check
            
        Returns:
            Dict containing the project status
        """
        logger.info(f"[🤖 Speechlab] Getting status for project {project_id}")
        
        try:
            response = self.client.get(
                f"{self.base_url}/projects/{project_id}",
                params={"expand": "true"}
            )
            response.raise_for_status()
            project_data = response.json()
            
            logger.info(f"[🤖 Speechlab] ✅ Retrieved project status")
            return project_data
        except httpx.HTTPStatusError as e:
            logger.error(f"[🤖 Speechlab] ❌ HTTP error when getting project status: {e}")
            raise

    def get_projects(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """
        Get a list of projects.
        
        Args:
            limit: Maximum number of projects to retrieve
            offset: Number of projects to skip
            
        Returns:
            Dict containing the list of projects
        """
        logger.info(f"[🤖 Speechlab] Getting projects with limit {limit} and offset {offset}")
        
        try:
            response = self.client.get(
                f"{self.base_url}/projects",
                params={"limit": limit, "offset": offset, "expand": "true"}
            )
            response.raise_for_status()
            projects_data = response.json()
            
            logger.info(f"[🤖 Speechlab] ✅ Retrieved {len(projects_data.get('results', []))} projects")
            return projects_data
        except httpx.HTTPStatusError as e:
            logger.error(f"[🤖 Speechlab] ❌ HTTP error when getting projects: {e}")
            raise
    
    def download_result(
        self,
        project_id: str,
        output_directory: Optional[str] = None
    ) -> str:
        """
        Download the dubbing result for a project.
        
        Args:
            project_id: ID of the project
            output_directory: Directory to save the result (defaults to ~/Desktop)
            
        Returns:
            Path to the downloaded file
        """
        logger.info(f"[🤖 Speechlab] Downloading result for project {project_id}")
        
        try:
            # First get project details to find the output media URL
            project_data = self.get_project_status(project_id)
            
            # Navigate the response structure to find the output media
            download_url = None
            translations = project_data.get("translations", [])
            
            for translation in translations:
                dubs = translation.get("dub", [])
                
                for dub in dubs:
                    medias = dub.get("medias", [])
                    for media in medias:
                        if media.get("operationType") == "OUTPUT" and media.get("presignedURL"):
                            download_url = media.get("presignedURL")
                            break
                    if download_url:
                        break
                if download_url:
                    break
            
            if not download_url:
                # Try alternative API endpoint if structured search fails
                url_response = self.client.get(
                    f"{self.base_url}/projects/{project_id}/download"
                )
                url_response.raise_for_status()
                url_data = url_response.json()
                
                if "url" not in url_data:
                    raise ValueError("No download URL available. The dubbing may not be complete.")
                
                download_url = url_data["url"]
            
            # Download the file
            logger.info(f"[🤖 Speechlab] Downloading from URL: {download_url}")
            download_response = httpx.get(download_url)
            download_response.raise_for_status()
            
            # Save the file
            output_path = Path(os.path.expanduser(output_directory or "~/Desktop"))
            output_path.mkdir(parents=True, exist_ok=True)
            output_file_name = f"dub_project_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            output_file_path = output_path / output_file_name
            
            with open(output_file_path, "wb") as f:
                f.write(download_response.content)
            
            logger.info(f"[🤖 Speechlab] ✅ Result downloaded to {output_file_path}")
            return str(output_file_path)
        except httpx.HTTPStatusError as e:
            logger.error(f"[🤖 Speechlab] ❌ HTTP error when downloading result: {e}")
            raise
        
    def generate_sharing_link(self, project_id: str) -> str:
        """
        Generate a sharing link for a project.
        
        Args:
            project_id: ID of the project
            
        Returns:
            Sharing link URL
        """
        logger.info(f"[🤖 Speechlab] Generating sharing link for project {project_id}")
        
        try:
            response = self.client.post(
                f"{self.base_url}/collaborations/generateSharingLink",
                json={"projectId": project_id}
            )
            response.raise_for_status()
            link_data = response.json()
            
            if "link" not in link_data:
                raise ValueError("No sharing link was returned in the response.")
                
            sharing_link = link_data["link"]
            logger.info(f"[🤖 Speechlab] ✅ Generated sharing link: {sharing_link}")
            return sharing_link
        except httpx.HTTPStatusError as e:
            logger.error(f"[🤖 Speechlab] ❌ HTTP error when generating sharing link: {e}")
            raise
    
    def wait_for_completion(
        self,
        project_id: str,
        max_attempts: int = 20,
        delay_seconds: int = 15,
        callback=None
    ) -> bool:
        """
        Wait for a project to complete by polling status.
        
        Args:
            project_id: ID of the project to check
            max_attempts: Maximum number of status checks
            delay_seconds: Seconds to wait between checks
            callback: Optional callback function to call with status updates
            
        Returns:
            True if project completed successfully, False otherwise
        """
        import time
        
        logger.info(f"[🤖 Speechlab] Waiting for project {project_id} to complete (max {max_attempts} attempts, {delay_seconds}s delay)")
        
        for attempt in range(max_attempts):
            try:
                project_data = self.get_project_status(project_id)
                status = project_data.get("job", {}).get("status", "UNKNOWN")
                
                logger.info(f"[🤖 Speechlab] Poll #{attempt+1}: Project status: {status}")
                
                # Call the callback if provided
                if callback:
                    callback(attempt, project_data)
                
                if status == "COMPLETE":
                    logger.info(f"[🤖 Speechlab] ✅ Project completed successfully after {attempt+1} attempts!")
                    return True
                elif status == "FAILED":
                    logger.error(f"[🤖 Speechlab] ❌ Project failed to process after {attempt+1} attempts!")
                    return False
                    
                # Calculate progress
                progress = "0%"
                if status == "PROCESSING":
                    progress = "50%"  # Simplified progress estimate
                
                logger.info(f"[🤖 Speechlab] ⏳ Poll #{attempt+1}: Project still processing. Progress: {progress}")
                
                if attempt < max_attempts - 1:
                    logger.info(f"[🤖 Speechlab] Waiting {delay_seconds}s before next check...")
                    time.sleep(delay_seconds)
            except Exception as e:
                logger.error(f"[🤖 Speechlab] ❌ Error checking status (attempt {attempt+1}): {e}")
                if attempt < max_attempts - 1:
                    logger.info(f"[🤖 Speechlab] Waiting {delay_seconds}s before next check...")
                    time.sleep(delay_seconds)
        
        logger.warning(f"[🤖 Speechlab] ⏰ Maximum attempts ({max_attempts}) reached without completion.")
        return False
    
# Example usage
if __name__ == "__main__":
    client = SpeechlabClient()
    # Create a new project
    project = client.create_project("API Client Test", "en", "es")
    print(f"Created project: {project}")
    client.close() 