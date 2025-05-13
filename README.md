# Speechlab MCP

A Claude plugin for interacting with the Speechlab AI dubbing platform.

## Overview

Speechlab MCP provides a Claude desktop plugin that allows you to interact with the Speechlab AI dubbing platform directly from Claude. This plugin simplifies the process of creating and managing dubbing projects for your media content.

With this plugin, you can:

- Create dubbing projects with custom language pairs
- Upload media files for dubbing
- Monitor dubbing progress
- Check project status in real-time
- Download completed dubbed media files

## Quick Start

```bash
# Install the package
pip install git+https://github.com/speechlab/speechlab-mcp.git

# Configure with your API key
python -m speechlab_mcp --api-key YOUR_API_KEY
```

## Detailed Installation

### Prerequisites

- Python 3.8 or higher
- A Speechlab API key
- Claude desktop application

### Install from source

1. Clone the repository:
   ```bash
   git clone https://github.com/speechlab/speechlab-mcp.git
   cd speechlab-mcp
   ```

2. Install the package:
   ```bash
   pip install .
   ```

3. Configure the plugin for Claude:
   ```bash
   python -m speechlab_mcp --api-key YOUR_API_KEY
   ```

   Or if you have the API key in a .env file:
   ```bash
   # Create a .env file in the current directory
   echo "SPEECHLAB_API_KEY=your_api_key_here" > .env
   
   # Then run the configuration
   python -m speechlab_mcp
   ```

## API Configuration

The Speechlab MCP plugin connects to the Speechlab API. By default, it uses `http://localhost/v1` as the API base URL, but you can configure it:

```bash
# Configure with custom API URL
python -m speechlab_mcp --api-key YOUR_API_KEY --base-url https://api.speechlab.ai/v1
```

## Usage in Claude

Once installed, the plugin will be available in Claude desktop. Here are some examples of how to use it:

### 1. Create a Dubbing Project

```
Create a new dubbing project named "Product Demo Video" with English as the source language and Spanish as the target language.
```

Claude will call the `create_project_and_dub` endpoint to create your project and report back with the project ID and details.

### 2. Upload Media to a Project

```
Upload the file at /Users/username/Videos/product_demo.mp4 to project ID abc123.
```

Claude will handle the file upload and confirm when it's complete.

### 3. Start the Dubbing Process

```
Start the dubbing process for project ID abc123.
```

Claude will initiate the dubbing process on the Speechlab platform.

### 4. Check Dubbing Status

```
Check the status of the dubbing process for project ID abc123.
```

Claude will query the API for the current status, progress percentage, and estimated completion time.

### 5. Download Dubbed Media

```
Download the completed dubbed video for project ID abc123 to my Desktop.
```

Once dubbing is complete, Claude will download the final video file to your specified location.

## Advanced Configuration

The plugin supports several configuration options:

1. Using the command-line argument:
   ```bash
   python -m speechlab_mcp --api-key YOUR_API_KEY
   ```

2. Setting an environment variable:
   ```bash
   export SPEECHLAB_API_KEY=YOUR_API_KEY
   python -m speechlab_mcp
   ```

3. Using a .env file in the current directory:
   ```
   SPEECHLAB_API_KEY=YOUR_API_KEY
   SPEECHLAB_API_BASE_URL=https://api.speechlab.ai/v1  # Optional
   SPEECHLAB_MCP_BASE_PATH=~/speechlab-files  # Optional, for file operations
   ```

## API Features

The Speechlab MCP plugin provides these core functionalities:

- **Project Management**: Create, retrieve, and list dubbing projects
- **Media Handling**: Upload source media files to projects
- **Dubbing Operations**: Start dubbing processes and monitor status
- **Results Management**: Download completed dubbed files

## Troubleshooting

- **Authentication Issues**: Ensure your API key is correct and has the necessary permissions.
- **File Upload Problems**: Verify the file path exists and the file is a supported media format.
- **Status Check Failures**: The project ID might be incorrect or the project might have been deleted.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 