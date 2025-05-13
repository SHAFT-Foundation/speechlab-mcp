#!/usr/bin/env python3
"""
Anthropic API Integration Example for Speechlab MCP

This example shows how to integrate Speechlab MCP with Anthropic's API directly,
creating function calling capabilities that can be used by Claude.

Requirements:
- speechlab_mcp package installed
- anthropic Python package installed
- ANTHROPIC_API_KEY environment variable set
- SPEECHLAB_API_KEY environment variable set
"""

import os
import json
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import anthropic
from anthropic.types import MessageParam

# Import Speechlab MCP components
from speechlab_mcp.server import (
    create_project_and_dub,
    get_projects,
    get_project,
    upload_media,
    start_dubbing,
    check_dubbing_status,
    download_dubbing_result
)
from mcp.types import TextContent

# Load environment variables
load_dotenv()

# Initialize the Anthropic client
client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

# Function to convert TextContent to a dictionary
def text_content_to_dict(response: TextContent) -> Dict[str, Any]:
    """Convert TextContent to a dictionary for Anthropic API."""
    if not response:
        return {"text": "No response received"}
    
    return {"text": response.text}

# Define the tools that will be available to Claude
TOOLS = [
    {
        "name": "create_project_and_dub",
        "description": "Create a new dubbing project with Speechlab",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the project"
                },
                "source_language": {
                    "type": "string",
                    "description": "Source language code (e.g., 'en' for English)"
                },
                "target_language": {
                    "type": "string",
                    "description": "Target language code (e.g., 'es' for Spanish)"
                }
            },
            "required": ["name", "source_language", "target_language"]
        }
    },
    {
        "name": "get_projects",
        "description": "Get a list of projects from Speechlab",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of projects to retrieve (default: 10)"
                }
            }
        }
    },
    {
        "name": "get_project",
        "description": "Get details of a specific project by ID",
        "input_schema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "ID of the project to retrieve"
                }
            },
            "required": ["project_id"]
        }
    },
    {
        "name": "upload_media",
        "description": "Upload a media file to an existing project",
        "input_schema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "ID of the project to upload to"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the media file to upload"
                }
            },
            "required": ["project_id", "file_path"]
        }
    },
    {
        "name": "start_dubbing",
        "description": "Start the dubbing process for a project",
        "input_schema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "ID of the project to start dubbing"
                }
            },
            "required": ["project_id"]
        }
    },
    {
        "name": "check_dubbing_status",
        "description": "Check the status of a dubbing job for a project",
        "input_schema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "ID of the project to check"
                }
            },
            "required": ["project_id"]
        }
    },
    {
        "name": "download_dubbing_result",
        "description": "Download a completed dubbing result",
        "input_schema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "ID of the project to download the result for"
                },
                "output_directory": {
                    "type": "string",
                    "description": "Directory to save the downloaded file (optional)"
                }
            },
            "required": ["project_id"]
        }
    }
]

# Function to execute the tool calls
def execute_tool_call(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool call based on the name and parameters."""
    try:
        if tool_name == "create_project_and_dub":
            response = create_project_and_dub(**parameters)
            return text_content_to_dict(response)
        
        elif tool_name == "get_projects":
            response = get_projects(**parameters)
            return text_content_to_dict(response)
        
        elif tool_name == "get_project":
            response = get_project(**parameters)
            return text_content_to_dict(response)
        
        elif tool_name == "upload_media":
            response = upload_media(**parameters)
            return text_content_to_dict(response)
        
        elif tool_name == "start_dubbing":
            response = start_dubbing(**parameters)
            return text_content_to_dict(response)
        
        elif tool_name == "check_dubbing_status":
            response = check_dubbing_status(**parameters)
            return text_content_to_dict(response)
        
        elif tool_name == "download_dubbing_result":
            response = download_dubbing_result(**parameters)
            return text_content_to_dict(response)
        
        else:
            return {"text": f"Unknown tool: {tool_name}"}
    
    except Exception as e:
        return {"text": f"Error executing {tool_name}: {str(e)}"}

def process_user_message(messages: List[MessageParam]) -> str:
    """
    Process a user message with Claude and handle any tool calls.
    
    Args:
        messages: List of previous messages in the conversation
        
    Returns:
        Claude's response text
    """
    # Call Claude with the messages and available tools
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=messages,
        tools=TOOLS
    )
    
    # Check if Claude wants to call a tool
    if response.content and hasattr(response.content[0], 'tool_calls') and response.content[0].tool_calls:
        # Process each tool call
        tool_results = []
        for tool_call in response.content[0].tool_calls:
            tool_name = tool_call.name
            parameters = json.loads(tool_call.input)
            
            print(f"Executing tool call: {tool_name} with parameters: {parameters}")
            result = execute_tool_call(tool_name, parameters)
            tool_results.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps(result)
            })
        
        # Send the tool results back to Claude
        final_response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=messages + [response],
            tool_results=tool_results
        )
        
        # Return the final response
        if final_response.content:
            return final_response.content[0].text
        else:
            return "No response from Claude after tool execution."
    
    # If no tool calls, just return the response
    if response.content:
        return response.content[0].text
    else:
        return "No response from Claude."

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Speechlab MCP Anthropic API Integration Example")
    parser.add_argument("--query", help="User query to process", default=None)
    args = parser.parse_args()
    
    # Example conversation
    conversation = [
        {
            "role": "system",
            "content": "You are an assistant that helps users with video dubbing using Speechlab. You have access to tools that let you create dubbing projects, upload media, start dubbing processes, and download results."
        }
    ]
    
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
                
            # Add the user message to the conversation
            conversation.append({
                "role": "user",
                "content": user_input
            })
            
            try:
                # Process the message with Claude
                response = process_user_message(conversation)
                print(f"\nClaude response:\n{response}")
                
                # Add Claude's response to the conversation history
                conversation.append({
                    "role": "assistant",
                    "content": response
                })
            except Exception as e:
                print(f"Error: {e}")
    else:
        # Add the user query to the conversation
        conversation.append({
            "role": "user",
            "content": args.query
        })
        
        # Process the message with Claude
        response = process_user_message(conversation)
        print(response) 