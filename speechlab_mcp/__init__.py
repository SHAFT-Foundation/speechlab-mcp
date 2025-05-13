"""
Speechlab MCP package.

This package provides interfaces to interact with the Speechlab AI dubbing platform.
It can be used as a Claude desktop plugin or directly imported into other applications.
"""
__version__ = "0.1.0"

# Export main functions for easier importing
from speechlab_mcp.server import (
    create_project_and_dub,
    get_projects,
    get_project,
    upload_media,
    start_dubbing,
    check_dubbing_status,
    download_dubbing_result,
    generate_sharing_link
)

# Export model classes
from speechlab_mcp.model import McpProject, McpDubProject, DubMedia

# Export client
from speechlab_mcp.client import SpeechlabClient 