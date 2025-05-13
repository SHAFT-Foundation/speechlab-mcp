from pydantic import BaseModel
from typing import Dict, Optional, List, Any


class McpProject(BaseModel):
    """
    Represents a Speechlab project in the MCP interface.
    
    Attributes:
        id: Unique identifier for the project
        name: Display name of the project
        status: Current status (e.g., "CREATED", "PROCESSING", "COMPLETE")
        created_at: ISO-8601 timestamp of creation time
        updated_at: ISO-8601 timestamp of last update time
        metadata: Additional project metadata
    """
    id: str
    name: str
    status: str
    created_at: str
    updated_at: str
    metadata: Optional[Dict[str, Any]] = None


class McpDubProject(BaseModel):
    """
    Represents a Speechlab dubbing project with language details.
    
    Attributes:
        id: Unique identifier for the project
        name: Display name of the project
        status: Current status (e.g., "CREATED", "PROCESSING", "COMPLETE")
        created_at: ISO-8601 timestamp of creation time
        updated_at: ISO-8601 timestamp of last update time
        source_language: ISO language code for the source language
        target_language: ISO language code for the target language
        source_file: Path to the original uploaded source file (if available)
        metadata: Additional project metadata
    """
    id: str
    name: str
    status: str
    created_at: str
    updated_at: str
    source_language: str
    target_language: str
    source_file: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DubMedia(BaseModel):
    """
    Represents a media file associated with a dubbing project.
    
    Attributes:
        id: Unique identifier for the media file
        uri: URI to access the media file
        category: Media category (e.g., "VIDEO", "AUDIO")
        content_type: MIME type of the media file
        format: File format (e.g., "mp4", "wav")
        operation_type: Type of operation (e.g., "INPUT", "OUTPUT")
        presigned_url: URL for direct media access (if available)
    """
    id: str
    uri: str
    category: str
    content_type: str
    format: str
    operation_type: str
    presigned_url: Optional[str] = None 