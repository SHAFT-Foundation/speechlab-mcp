#!/usr/bin/env python3
"""
LangChain Integration Example for Speechlab MCP

This example shows how to integrate Speechlab MCP with LangChain agents,
creating tools that can be used in a LangChain agent workflow.

Requirements:
- speechlab_mcp package installed
- langchain and related packages installed
- OpenAI API key or other LLM API key
- SPEECHLAB_API_KEY environment variable set
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any, List

# Load environment variables
load_dotenv()

# Import LangChain components
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI

# Import Speechlab MCP components
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
from mcp.types import TextContent

# Adapter functions to convert between MCP TextContent and plain text for LangChain
def adapt_to_langchain(response: TextContent) -> str:
    """Convert MCP TextContent response to string for LangChain."""
    return response.text if response and hasattr(response, 'text') else str(response)

def create_project_tool(name: str, source_language: str, target_language: str) -> str:
    """Create a new dubbing project."""
    response = create_project_and_dub(
        name=name,
        source_language=source_language,
        target_language=target_language
    )
    return adapt_to_langchain(response)

def get_projects_tool(limit: int = 10) -> str:
    """Get a list of projects."""
    response = get_projects(limit=limit)
    return adapt_to_langchain(response)

def get_project_tool(project_id: str) -> str:
    """Get details for a specific project."""
    response = get_project(project_id=project_id)
    return adapt_to_langchain(response)

def upload_media_tool(project_id: str, file_path: str) -> str:
    """Upload media to a project."""
    response = upload_media(project_id=project_id, file_path=file_path)
    return adapt_to_langchain(response)

def start_dubbing_tool(project_id: str) -> str:
    """Start the dubbing process for a project."""
    response = start_dubbing(project_id=project_id)
    return adapt_to_langchain(response)

def check_status_tool(project_id: str) -> str:
    """Check the status of a dubbing process."""
    response = check_dubbing_status(project_id=project_id)
    return adapt_to_langchain(response)

def download_result_tool(project_id: str, output_dir: str = "~/Downloads") -> str:
    """Download the dubbing result."""
    response = download_dubbing_result(
        project_id=project_id,
        output_directory=output_dir
    )
    return adapt_to_langchain(response)

def generate_link_tool(project_id: str) -> str:
    """Generate a sharing link for a project."""
    response = generate_sharing_link(project_id=project_id)
    return adapt_to_langchain(response)

# Create LangChain tools
tools = [
    Tool(
        name="CreateDubbingProject",
        func=create_project_tool,
        description="Create a new dubbing project. Args: name, source_language, target_language"
    ),
    Tool(
        name="ListProjects",
        func=get_projects_tool,
        description="List all available dubbing projects. Args: limit (optional)"
    ),
    Tool(
        name="GetProjectDetails",
        func=get_project_tool,
        description="Get details about a specific project. Args: project_id"
    ),
    Tool(
        name="UploadMedia",
        func=upload_media_tool,
        description="Upload a media file to a project. Args: project_id, file_path"
    ),
    Tool(
        name="StartDubbing",
        func=start_dubbing_tool,
        description="Start the dubbing process for a project. Args: project_id"
    ),
    Tool(
        name="CheckDubbingStatus",
        func=check_status_tool,
        description="Check the status of a dubbing job. Args: project_id"
    ),
    Tool(
        name="DownloadDubbingResult",
        func=download_result_tool,
        description="Download the dubbed video. Args: project_id, output_dir (optional)"
    ),
    Tool(
        name="GenerateSharingLink",
        func=generate_link_tool,
        description="Generate a sharing link for a project. Args: project_id"
    )
]

# Setup the LLM
llm = ChatOpenAI(temperature=0)

# Setup memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Setup agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True
)

def run_agent_with_query(query: str) -> str:
    """Run the agent with a user query and return the response."""
    return agent.run(input=query)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Speechlab MCP LangChain Integration Example")
    parser.add_argument("--query", help="User query to process", default=None)
    args = parser.parse_args()
    
    if not args.query:
        print("Running interactive mode. Type 'exit' to quit.")
        print("Example commands:")
        print("- Create a dubbing project called 'Product Demo' in English with Spanish dubbing")
        print("- List all my dubbing projects")
        print("- Check the status of project abc123")
        print("- Upload my video at /path/to/video.mp4 to project abc123")
        print("- Download the result for project abc123")
        
        while True:
            user_input = input("\nEnter your request: ")
            if user_input.lower() in ["exit", "quit"]:
                break
                
            try:
                response = run_agent_with_query(user_input)
                print(f"\nAgent response:\n{response}")
            except Exception as e:
                print(f"Error: {e}")
    else:
        # Run with the provided query
        response = run_agent_with_query(args.query)
        print(response) 