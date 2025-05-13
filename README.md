# 🎬 Speechlab MCP 

<div align="center">

![Speechlab MCP](https://img.shields.io/badge/Speechlab-MCP-brightgreen?style=for-the-badge&logo=data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyB3aWR0aD0iMjU2cHgiIGhlaWdodD0iMjU2cHgiIHZpZXdCb3g9IjAgMCAyNTYgMjU2IiB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgZmlsbD0id2hpdGUiPgogIDxwYXRoIGQ9Ik0xMjggMjRDNjkuNjQgMjQgMjQgNjkuNjQgMjQgMTI4UzY5LjY0IDIzMiAxMjggMjMyUzIzMiAxODYuMzYgMjMyIDEyOFMxODYuMzYgMjQgMTI4IDI0Wk03MiA5NkgxMTJWMTYwSDcyVjk2Wk0xNDQgOTZIMTg0VjE2MEgxNDRWOTZaIiAvPgogIDxwYXRoIGZpbGwtcnVsZT0iZXZlbm9kZCIgZD0iTTEyOCAxMjBDMTM3LjI0NyAxMjAgMTQ0LjggMTI3LjU1MyAxNDQuOCAxMzZDMTQ0LjggMTQ0LjQ0NyAxMzcuMjQ3IDE1MiAxMjggMTUyQzExOC43NTMgMTUyIDExMS4yIDE0NC40NDcgMTExLjIgMTM2QzExMS4yIDEyNy41NTMgMTE4Ljc1MyAxMjAgMTI4IDEyMFoiIGNsaXAtcnVsZT0iZXZlbm9kZCIgLz4KPC9zdmc+Cg==)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)

**A universal AI-compatible interface for interacting with the Speechlab AI dubbing platform**

</div>

## 🔍 Overview

Speechlab MCP is a versatile interface that enables AI assistants to interact with the Speechlab AI dubbing platform. This tool bridges the gap between natural language instructions and the Speechlab API, allowing for seamless dubbing operations.

<div align="center">
    
```
Your Content → 🤖 AI + Speechlab MCP → 🎙️ Professional Dubbing → 🌎 Global Audiences
```

</div>

### 🧠 Multi-Platform Support

This package is designed to work with:

- ✅ **Claude Desktop** (direct plugin integration)
- ✅ **Cursor Editor** (via Cursor's AI assistant)
- ✅ **Anthropic API Apps** (via function calling)
- ✅ **LangChain Apps** (as a tool in agent flows)
- ✅ **Any LLM Application** with API access

## 🚀 Quick Start

```bash
# Option 1: Use our interactive setup script
python setup_speechlab_mcp.py

# Option 2: Manual installation
pip install git+https://github.com/speechlab/speechlab-mcp.git
python -m speechlab_mcp --api-key YOUR_API_KEY
```

## 📋 Features

- 🎬 **Project Management**: Create and manage dubbing projects
- 🎙️ **Language Support**: Works with 20+ languages and nearly 300 language pairs
- 🔄 **Workflow Automation**: Automate the entire dubbing process from creation to download
- 📊 **Status Monitoring**: Real-time progress tracking and status updates
- 🔗 **Sharing Capabilities**: Generate shareable links for collaboration
- 🧩 **AI Integration**: Seamlessly integrates with AI assistants and workflows

## 🛠️ Detailed Installation

### Prerequisites

- Python 3.8 or higher
- A Speechlab API key
- For Claude integration: Claude desktop application
- For other integrations: Your preferred AI-enabled application

### Install from source

1. Clone the repository:
   ```bash
   git clone https://github.com/speechlab/speechlab-mcp.git
   cd speechlab-mcp
   ```

2. Run the setup script (recommended):
   ```bash
   python setup_speechlab_mcp.py
   ```

   Or install manually:
   ```bash
   pip install .
   ```

3. Configure for Claude integration (if using setup script, this is done automatically):
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

## 🔌 API Configuration

The Speechlab MCP plugin connects to the Speechlab API. By default, it uses `http://localhost/v1` as the API base URL, but you can configure it:

```bash
# Configure with custom API URL
python -m speechlab_mcp --api-key YOUR_API_KEY --base-url https://api.speechlab.ai/v1
```

## 🤖 Integration Methods

### Claude Desktop

Once installed as a Claude plugin, you can use natural language to interact with Speechlab:

```
Create a new dubbing project named "Product Demo Video" with English as the source language and Spanish as the target language.
```

### Cursor Editor Integration

When using Cursor's AI assistant:

1. Reference the Speechlab MCP package in your project
2. Ask the Cursor AI to use the package to perform dubbing operations:

```
Using the Speechlab MCP package, can you create a new dubbing project for my video file at ./videos/demo.mp4 with English to Japanese translation?
```

See [examples/cursor_integration.md](examples/cursor_integration.md) for detailed instructions.

### API Integration (Python)

```python
from speechlab_mcp.server import create_project_and_dub, start_dubbing, check_dubbing_status

# Create a new project
project_id = create_project_and_dub(
    name="API Demo", 
    source_language="en", 
    target_language="fr"
)

# Upload media and start dubbing
upload_media(project_id, "/path/to/video.mp4")
start_dubbing(project_id)

# Check status
status = check_dubbing_status(project_id)
```

See [examples/integration_example.py](examples/integration_example.py) for a complete example.

### LangChain Integration

```python
from langchain.agents import Tool
from speechlab_mcp.server import create_project_and_dub, check_dubbing_status

tools = [
    Tool(
        name="CreateDubbingProject",
        func=lambda x: create_project_and_dub(name=x['name'], source_language=x['source'], target_language=x['target']),
        description="Create a dubbing project with Speechlab"
    ),
    Tool(
        name="CheckDubbingStatus",
        func=lambda x: check_dubbing_status(project_id=x),
        description="Check the status of a dubbing project"
    )
]

# Use these tools in your LangChain agent
```

See [examples/langchain_agent_example.py](examples/langchain_agent_example.py) for a complete example.

### Anthropic API Integration

```python
# Define Speechlab tools for Claude
TOOLS = [
    {
        "name": "create_project_and_dub",
        "description": "Create a new dubbing project with Speechlab",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "source_language": {"type": "string"},
                "target_language": {"type": "string"}
            },
            "required": ["name", "source_language", "target_language"]
        }
    }
]

# Use with Anthropic's client
response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Create a dubbing project for my product video"}],
    tools=TOOLS
)
```

See [examples/anthropic_api_example.py](examples/anthropic_api_example.py) for a complete example.

## 📱 Usage Examples

### Creating a Dubbing Project

```
Create a new dubbing project named "Product Demo Video" with English as the source language and Spanish as the target language.
```

### Uploading Media

```
Upload the file at /Users/username/Videos/product_demo.mp4 to project ID abc123.
```

### Starting the Dubbing Process

```
Start the dubbing process for project ID abc123.
```

### Checking Status

```
Check the status of the dubbing process for project ID abc123.
```

### Downloading Results

```
Download the completed dubbed video for project ID abc123 to my Desktop.
```

### Generating a Sharing Link

```
Generate a sharing link for project ID abc123 so I can share it with my team.
```

## ✨ Why This Matters

### 🌍 Breaking Language Barriers

By connecting AI assistants directly to dubbing technology, Speechlab MCP democratizes access to global communication. Your content can reach international audiences with professional-quality dubbing, all through simple natural language requests.

### ⚡ Workflow Acceleration

Traditional dubbing processes are complex and time-consuming. With Speechlab MCP, you can:

- Reduce dubbing project setup time from hours to seconds
- Automate repetitive tasks through simple AI instructions
- Monitor projects without logging into separate dashboards
- Share results with stakeholders through simple commands

### 🧠 AI-Native Integration

As AI becomes a central part of creative workflows, tools need to be AI-compatible. Speechlab MCP is designed from the ground up to be used by both humans and AI systems, creating a future-proof bridge between language models and professional dubbing services.

## 🔐 Advanced Configuration

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

## 🧩 API Features

The Speechlab MCP plugin provides these core functionalities:

- **Project Management**: Create, retrieve, and list dubbing projects
- **Media Handling**: Upload source media files to projects
- **Dubbing Operations**: Start dubbing processes and monitor status
- **Results Management**: Download completed dubbed files
- **Collaboration**: Generate sharing links for team access

## 📚 Example Code Repository

The `examples/` directory contains sample code for various integration methods:

- **[examples/integration_example.py](examples/integration_example.py)**: Direct Python integration
- **[examples/langchain_agent_example.py](examples/langchain_agent_example.py)**: LangChain agent integration
- **[examples/anthropic_api_example.py](examples/anthropic_api_example.py)**: Anthropic API integration
- **[examples/cursor_integration.md](examples/cursor_integration.md)**: Guide for Cursor editor integration

## ❓ Troubleshooting

- **Authentication Issues**: Ensure your API key is correct and has the necessary permissions.
- **File Upload Problems**: Verify the file path exists and the file is a supported media format.
- **Status Check Failures**: The project ID might be incorrect or the project might have been deleted.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details. 