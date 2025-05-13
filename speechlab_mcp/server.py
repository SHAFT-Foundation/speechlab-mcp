"""
Speechlab MCP Server

This server provides access to Speechlab API endpoints for dubbing and project management.
Each tool that makes an API call is marked for clarity.
"""

import httpx
import os
import json
import logging
from datetime import datetime
from io import BytesIO
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from speechlab_mcp.model import McpProject, McpDubProject
from speechlab_mcp.utils import (
    make_error,
    make_output_path,
    make_output_file,
    handle_input_file,
)
from speechlab_mcp import __version__

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()
api_key = os.getenv("SPEECHLAB_API_KEY")
base_path = os.getenv("SPEECHLAB_MCP_BASE_PATH")
api_base_url = os.getenv("SPEECHLAB_API_BASE_URL", "http://localhost/v1")

if not api_key:
    raise ValueError("SPEECHLAB_API_KEY environment variable is required")

# Add custom client to set User-Agent header
custom_client = httpx.Client(
    headers={
        "User-Agent": f"Speechlab-MCP/{__version__}",
        "Authorization": f"Bearer {api_key}"
    },
    timeout=30.0  # 30 second timeout, matching TypeScript example
)

mcp = FastMCP("Speechlab")

def handle_api_error(error: Exception, context: str) -> None:
    """
    Enhanced error handling for API errors, following the TypeScript example pattern.
    
    Args:
        error: The exception that occurred
        context: Description of the operation being performed
    """
    if isinstance(error, httpx.HTTPStatusError):
        logger.error(f"[🤖 Speechlab] ❌ API Error during {context}: {error}")
        logger.error(f"[🤖 Speechlab] Status: {error.response.status_code}")
        logger.error(f"[🤖 Speechlab] Data: {error.response.text}")
        logger.error(f"[🤖 Speechlab] Headers: {dict(error.response.headers)}")
    elif isinstance(error, httpx.RequestError):
        logger.error(f"[🤖 Speechlab] ❌ Request error during {context}: {error}")
    else:
        logger.error(f"[🤖 Speechlab] ❌ Non-HTTP error during {context}: {error}")

@mcp.tool(
    description="""Create a new project in Speechlab and set it up for dubbing.
    
    Args:
        name: Name of the project
        source_language: Source language code (e.g., 'en' for English)
        target_language: Target language code (e.g., 'es' for Spanish)
        source_file: Path to the source media file for dubbing
        output_directory: Directory where files should be saved. 
            Defaults to $HOME/Desktop if not provided.
    
    Returns:
        TextContent containing the details of the created project
    """
)
def create_project_and_dub(
    name: str,
    source_language: str,
    target_language: str,
    source_file: Optional[str] = None,
    output_directory: Optional[str] = None,
) -> TextContent:
    # Map special language codes like 'es' to their API-specific variants
    api_target_language = target_language
    if target_language == "es":
        api_target_language = "es_la"
        logger.debug(f"[🤖 Speechlab] Mapped target language code '{target_language}' to API target language: '{api_target_language}'")
    
    logger.info(f"[🤖 Speechlab] Creating project '{name}' with source language '{source_language}' and target '{api_target_language}'")
    
    # First, create the project
    try:
        create_response = custom_client.post(
            f"{api_base_url}/projects/createProjectAndDub",
            json={
                "name": name,
                "sourceLanguage": source_language,
                "targetLanguage": api_target_language,
                "dubAccent": api_target_language,  # Added from TypeScript example
                "voiceMatchingMode": "source",     # Added from TypeScript example
                "unitType": "whiteGlove",          # Added from TypeScript example
                "thirdPartyID": f"mcp_{datetime.now().strftime('%Y%m%d%H%M%S')}"  # Unique ID
            }
        )
        create_response.raise_for_status()
        project_data = create_response.json()
        
        logger.info(f"[🤖 Speechlab] ✅ Project created successfully: {project_data}")
        
        # If source file is provided, upload it
        if source_file:
            file_path = handle_input_file(source_file)
            
            logger.info(f"[🤖 Speechlab] Uploading file {file_path} to project {project_data['id']}")
            with open(file_path, "rb") as f:
                files = {"file": (file_path.name, f, "video/mp4")}
                upload_response = custom_client.post(
                    f"{api_base_url}/projects/{project_data['id']}/upload",
                    files=files
                )
                upload_response.raise_for_status()
                upload_data = upload_response.json()
                logger.info(f"[🤖 Speechlab] ✅ File uploaded successfully: {upload_data}")
        
        # Format the project data for return
        project = McpDubProject(
            id=project_data["id"],
            name=project_data["name"],
            status=project_data.get("status", "created"),
            created_at=project_data.get("createdAt", datetime.now().isoformat()),
            updated_at=project_data.get("updatedAt", datetime.now().isoformat()),
            source_language=project_data["sourceLanguage"],
            target_language=project_data["targetLanguage"],
            source_file=source_file if source_file else None,
            metadata=project_data.get("metadata", {})
        )
        
        return TextContent(
            type="text",
            text=f"Project created successfully:\nID: {project.id}\nName: {project.name}\nSource Language: {project.source_language}\nTarget Language: {project.target_language}\nStatus: {project.status}"
        )
        
    except httpx.HTTPStatusError as e:
        handle_api_error(e, f"project creation for '{name}'")
        make_error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"[🤖 Speechlab] ❌ Error creating project: {e}")
        make_error(f"Error creating project: {str(e)}")


@mcp.tool(
    description="""Get a list of projects from Speechlab.
    
    Args:
        limit: Maximum number of projects to retrieve
        offset: Number of projects to skip
        
    Returns:
        TextContent containing the list of projects
    """
)
def get_projects(
    limit: int = 10,
    offset: int = 0
) -> TextContent:
    logger.info(f"[🤖 Speechlab] Getting projects with limit {limit} and offset {offset}")
    
    try:
        response = custom_client.get(
            f"{api_base_url}/projects",
            params={"limit": limit, "offset": offset, "expand": "true"}  # Added expand parameter from TypeScript example
        )
        response.raise_for_status()
        projects_data = response.json()
        
        logger.info(f"[🤖 Speechlab] ✅ Retrieved {len(projects_data.get('results', []))} projects")
        
        # Handle response format based on TypeScript example
        results = projects_data.get('results', [])
        if not results:
            return TextContent(type="text", text="No projects found.")
        
        # Format the projects data for return
        projects_list = []
        for project_data in results:
            project = McpProject(
                id=project_data["id"],
                name=project_data.get("job", {}).get("name", "Unnamed Project"),
                status=project_data.get("job", {}).get("status", "unknown"),
                created_at=project_data.get("createdAt", "unknown"),
                updated_at=project_data.get("updatedAt", "unknown"),
                metadata=project_data.get("metadata", {})
            )
            projects_list.append(
                f"ID: {project.id}\nName: {project.name}\nStatus: {project.status}\nCreated: {project.created_at}"
            )
        
        formatted_projects = "\n\n".join(projects_list)
        return TextContent(
            type="text",
            text=f"Retrieved {len(projects_list)} projects:\n\n{formatted_projects}"
        )
        
    except httpx.HTTPStatusError as e:
        handle_api_error(e, "listing projects")
        make_error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"[🤖 Speechlab] ❌ Error getting projects: {e}")
        make_error(f"Error getting projects: {str(e)}")


@mcp.tool(
    description="""Get a specific project by ID.
    
    Args:
        project_id: ID of the project to retrieve
        
    Returns:
        TextContent containing the project details
    """
)
def get_project(
    project_id: str
) -> TextContent:
    logger.info(f"[🤖 Speechlab] Getting project with ID {project_id}")
    
    try:
        response = custom_client.get(
            f"{api_base_url}/projects/{project_id}",
            params={"expand": "true"}  # Added from TypeScript example
        )
        response.raise_for_status()
        project_data = response.json()
        
        logger.info(f"[🤖 Speechlab] ✅ Retrieved project: {project_data.get('id', 'unknown ID')}")
        
        # Format the project data for return, adjust based on the TypeScript example structure
        job_data = project_data.get("job", {})
        project = McpDubProject(
            id=project_data["id"],
            name=job_data.get("name", "Unnamed Project"),
            status=job_data.get("status", "unknown"),
            created_at=project_data.get("createdAt", "unknown"),
            updated_at=project_data.get("updatedAt", "unknown"),
            source_language=job_data.get("sourceLanguage", "unknown"),
            target_language=job_data.get("targetLanguage", "unknown"),
            source_file=None,  # Source file info not in response
            metadata=project_data.get("metadata", {})
        )
        
        # Check for additional information from translations
        translations = project_data.get("translations", [])
        translation_info = ""
        if translations:
            first_translation = translations[0]
            translation_info = f"\nTranslation Language: {first_translation.get('language', 'unknown')}"
            
            # Check for dub information
            dubs = first_translation.get("dub", [])
            if dubs:
                first_dub = dubs[0]
                translation_info += f"\nDub Status: {first_dub.get('mergeStatus', 'unknown')}"
                
                # Check for media files
                medias = first_dub.get("medias", [])
                if medias:
                    media_count = len(medias)
                    translation_info += f"\nMedia Files: {media_count}"
        
        return TextContent(
            type="text",
            text=f"Project Details:\nID: {project.id}\nName: {project.name}\nStatus: {project.status}\nSource Language: {project.source_language}\nTarget Language: {project.target_language}\nCreated: {project.created_at}\nUpdated: {project.updated_at}{translation_info}"
        )
        
    except httpx.HTTPStatusError as e:
        handle_api_error(e, f"getting project {project_id}")
        make_error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"[🤖 Speechlab] ❌ Error getting project: {e}")
        make_error(f"Error getting project: {str(e)}")


@mcp.tool(
    description="""Upload a media file to an existing project.
    
    Args:
        project_id: ID of the project to upload to
        file_path: Path to the media file to upload
        
    Returns:
        TextContent containing the upload result
    """
)
def upload_media(
    project_id: str,
    file_path: str
) -> TextContent:
    logger.info(f"[🤖 Speechlab] Uploading media file {file_path} to project {project_id}")
    
    try:
        file_path_obj = handle_input_file(file_path)
        
        with open(file_path_obj, "rb") as f:
            files = {"file": (file_path_obj.name, f, "video/mp4")}
            response = custom_client.post(
                f"{api_base_url}/projects/{project_id}/upload",
                files=files
            )
            response.raise_for_status()
            upload_data = response.json()
            
        logger.info(f"[🤖 Speechlab] ✅ File uploaded successfully: {upload_data}")
        
        return TextContent(
            type="text",
            text=f"File uploaded successfully to project {project_id}.\nFile: {file_path_obj.name}"
        )
        
    except httpx.HTTPStatusError as e:
        handle_api_error(e, f"uploading media to project {project_id}")
        make_error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"[🤖 Speechlab] ❌ Error uploading media: {e}")
        make_error(f"Error uploading media: {str(e)}")


@mcp.tool(
    description="""Start the dubbing process for a project.
    
    Args:
        project_id: ID of the project to start dubbing
        
    Returns:
        TextContent containing the result of the dubbing request
    """
)
def start_dubbing(
    project_id: str
) -> TextContent:
    logger.info(f"[🤖 Speechlab] Starting dubbing process for project {project_id}")
    
    try:
        response = custom_client.post(
            f"{api_base_url}/projects/{project_id}/dub"
        )
        response.raise_for_status()
        dub_data = response.json()
        
        logger.info(f"[🤖 Speechlab] ✅ Dubbing process started: {dub_data}")
        
        return TextContent(
            type="text",
            text=f"Dubbing process started for project {project_id}.\nStatus: {dub_data.get('status', 'processing')}\nETA: {dub_data.get('eta', 'unknown')}"
        )
        
    except httpx.HTTPStatusError as e:
        handle_api_error(e, f"starting dubbing for project {project_id}")
        make_error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"[🤖 Speechlab] ❌ Error starting dubbing: {e}")
        make_error(f"Error starting dubbing: {str(e)}")


@mcp.tool(
    description="""Check the status of a dubbing job for a project.
    
    Args:
        project_id: ID of the project to check
        
    Returns:
        TextContent containing the status of the dubbing job
    """
)
def check_dubbing_status(
    project_id: str
) -> TextContent:
    logger.info(f"[🤖 Speechlab] Checking dubbing status for project {project_id}")
    
    try:
        # Fetch the full project details to get comprehensive status info
        response = custom_client.get(
            f"{api_base_url}/projects/{project_id}",
            params={"expand": "true"}
        )
        response.raise_for_status()
        project_data = response.json()
        
        logger.info(f"[🤖 Speechlab] Retrieved project for status check: {project_data}")
        
        # Get the job status from the structure
        job_data = project_data.get("job", {})
        status = job_data.get("status", "UNKNOWN")
        
        # Calculate a progress estimate based on status
        progress = "0%"
        if status == "PROCESSING":
            progress = "50%"
        elif status == "COMPLETE":
            progress = "100%"
        
        # Look for translation and dub details
        translations = project_data.get("translations", [])
        dub_status = "Not started"
        media_info = ""
        
        if translations:
            first_translation = translations[0]
            dubs = first_translation.get("dub", [])
            
            if dubs:
                first_dub = dubs[0]
                dub_status = first_dub.get("mergeStatus", "Unknown")
                
                # Check for media files
                medias = first_dub.get("medias", [])
                if medias:
                    media_count = len(medias)
                    media_info = f"\nMedia Files: {media_count} files available"
                    
                    # Find output media if available
                    output_media = next((m for m in medias if m.get("operationType") == "OUTPUT"), None)
                    if output_media and output_media.get("presignedURL"):
                        media_info += f"\nOutput media available for download"
        
        # Format the status with all the details
        status_text = (
            f"Dubbing Status for Project {project_id}:\n"
            f"Status: {status}\n"
            f"Progress: {progress}\n"
            f"Dub Process: {dub_status}{media_info}"
        )
        
        return TextContent(type="text", text=status_text)
        
    except httpx.HTTPStatusError as e:
        handle_api_error(e, f"checking status for project {project_id}")
        make_error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"[🤖 Speechlab] ❌ Error checking dubbing status: {e}")
        make_error(f"Error checking dubbing status: {str(e)}")


@mcp.tool(
    description="""Download a completed dubbing result.
    
    Args:
        project_id: ID of the project to download the result for
        output_directory: Directory to save the downloaded file (optional)
        
    Returns:
        TextContent containing the path to the downloaded file
    """
)
def download_dubbing_result(
    project_id: str,
    output_directory: Optional[str] = None
) -> TextContent:
    logger.info(f"[🤖 Speechlab] Downloading dubbing result for project {project_id}")
    
    try:
        # First get project details to find the output media URL
        project_response = custom_client.get(
            f"{api_base_url}/projects/{project_id}",
            params={"expand": "true"}
        )
        project_response.raise_for_status()
        project_data = project_response.json()
        
        # Navigate the response structure to find the output media
        translations = project_data.get("translations", [])
        if not translations:
            make_error("No translations found in the project.")
            
        # Look through translations for dubs with media
        download_url = None
        for translation in translations:
            dubs = translation.get("dub", [])
            if not dubs:
                continue
                
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
            url_response = custom_client.get(
                f"{api_base_url}/projects/{project_id}/download"
            )
            url_response.raise_for_status()
            url_data = url_response.json()
            
            if "url" not in url_data:
                make_error("No download URL available. The dubbing may not be complete.")
            
            download_url = url_data["url"]
        
        # Download the file
        logger.info(f"[🤖 Speechlab] Downloading from URL: {download_url}")
        download_response = httpx.get(download_url)
        download_response.raise_for_status()
        
        # Save the file
        output_path = make_output_path(output_directory, base_path)
        output_file_name = make_output_file("dub", f"project_{project_id}", output_path, "mp4")
        
        with open(output_path / output_file_name, "wb") as f:
            f.write(download_response.content)
        
        logger.info(f"[🤖 Speechlab] ✅ Dubbing result downloaded to {output_path / output_file_name}")
        
        return TextContent(
            type="text",
            text=f"Dubbing result downloaded successfully.\nFile saved at: {output_path / output_file_name}"
        )
        
    except httpx.HTTPStatusError as e:
        handle_api_error(e, f"downloading result for project {project_id}")
        make_error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"[🤖 Speechlab] ❌ Error downloading dubbing result: {e}")
        make_error(f"Error downloading dubbing result: {str(e)}")


@mcp.tool(
    description="""Generate a sharing link for a project that can be shared with others.
    
    Args:
        project_id: ID of the project to generate a sharing link for
        
    Returns:
        TextContent containing the sharing link
    """
)
def generate_sharing_link(
    project_id: str
) -> TextContent:
    logger.info(f"[🤖 Speechlab] Generating sharing link for project {project_id}")
    
    try:
        response = custom_client.post(
            f"{api_base_url}/collaborations/generateSharingLink",
            json={"projectId": project_id}
        )
        response.raise_for_status()
        link_data = response.json()
        
        if "link" not in link_data:
            make_error("No sharing link was returned in the response.")
            
        sharing_link = link_data["link"]
        logger.info(f"[🤖 Speechlab] ✅ Generated sharing link: {sharing_link}")
        
        return TextContent(
            type="text",
            text=f"Sharing link generated successfully for project {project_id}.\nLink: {sharing_link}\n\nThis link can be shared with others to view the project."
        )
        
    except httpx.HTTPStatusError as e:
        handle_api_error(e, f"generating sharing link for project {project_id}")
        make_error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"[🤖 Speechlab] ❌ Error generating sharing link: {e}")
        make_error(f"Error generating sharing link: {str(e)}")


def main():
    logger.info("[🤖 Speechlab] Starting Speechlab MCP server")
    """Run the MCP server"""
    mcp.run()


if __name__ == "__main__":
    main() 