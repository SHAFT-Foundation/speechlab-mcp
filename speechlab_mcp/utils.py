import os
from pathlib import Path
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SpeechlabMcpError(Exception):
    pass


def make_error(error_text: str):
    logger.error(f"Error: {error_text}")
    raise SpeechlabMcpError(error_text)


def is_file_writeable(path: Path) -> bool:
    if path.exists():
        return os.access(path, os.W_OK)
    parent_dir = path.parent
    return os.access(parent_dir, os.W_OK)


def make_output_file(
    tool: str, text: str, output_path: Path, extension: str, full_id: bool = False
) -> Path:
    id = text if full_id else text[:5]

    output_file_name = f"{tool}_{id.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
    return output_path / output_file_name


def make_output_path(
    output_directory: str | None, base_path: str | None = None
) -> Path:
    output_path = None
    if output_directory is None:
        output_path = Path.home() / "Desktop"
    elif not os.path.isabs(output_directory) and base_path:
        output_path = Path(os.path.expanduser(base_path)) / Path(output_directory)
    else:
        output_path = Path(os.path.expanduser(output_directory))
    if not is_file_writeable(output_path):
        make_error(f"Directory ({output_path}) is not writeable")
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def handle_input_file(file_path: str, audio_content_check: bool = True) -> Path:
    """Handle file input paths, checking existence and type if needed."""
    if not os.path.isabs(file_path) and not os.environ.get("SPEECHLAB_MCP_BASE_PATH"):
        make_error(
            "File path must be an absolute path if SPEECHLAB_MCP_BASE_PATH is not set"
        )
    path = Path(file_path)
    if not path.exists():
        make_error(f"File ({path}) does not exist")
    elif not path.is_file():
        make_error(f"Path ({path}) is not a file")

    # Add audio file check if needed
    if audio_content_check:
        if not check_media_file(path):
            make_error(f"File ({path}) is not a recognized media file")
    return path


def check_media_file(path: Path) -> bool:
    """Check if file is a recognized media file type."""
    media_extensions = {
        ".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac",
        ".mp4", ".mov", ".avi", ".mkv", ".webm"
    }
    return path.suffix.lower() in media_extensions 