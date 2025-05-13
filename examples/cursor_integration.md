# Speechlab MCP in Cursor

This guide shows how to use Speechlab MCP through the Cursor AI assistant.

## Setup

1. Install the Speechlab MCP package:
   ```bash
   pip install git+https://github.com/speechlab/speechlab-mcp.git
   ```

2. Create a `.env` file in your project with your Speechlab API key:
   ```
   SPEECHLAB_API_KEY=your_api_key_here
   ```

3. Create a simple script called `dubbing_helper.py` in your project:
   ```python
   from speechlab_mcp.server import (
       create_project_and_dub,
       get_projects,
       upload_media,
       start_dubbing,
       check_dubbing_status,
       download_dubbing_result
   )
   
   # This file serves as an import point for Cursor AI to understand
   # the available Speechlab functions
   ```

## Using with Cursor AI

Once you have the package installed and the helper file created, you can ask Cursor AI to perform dubbing tasks. Here are some example prompts:

### Creating a Dubbing Project

```
Cursor, using the speechlab_mcp package, create a new dubbing project called "Product Demo" with English as the source language and Spanish as the target language.
```

### Uploading a Video

```
Cursor, use speechlab_mcp to upload the file at ./videos/product_demo.mp4 to the project ID you just created.
```

### Starting the Dubbing Process

```
Cursor, now use speechlab_mcp to start the dubbing process for that project.
```

### Checking Status

```
Cursor, check the status of the dubbing process using speechlab_mcp.
```

### Downloading the Result

```
Cursor, when the dubbing is complete, download the result to ./output/ using speechlab_mcp.
```

## Tips for Working with Cursor AI

1. **Be Specific**: Always specify the package name (`speechlab_mcp`) in your prompts so Cursor knows which package to use.

2. **Function Names**: If Cursor is having trouble, you might need to be more specific about function names, like "use the create_project_and_dub function from speechlab_mcp".

3. **Error Handling**: Ask Cursor to implement error handling when working with the API.

4. **File Generation**: Cursor can generate entire scripts for you to automate dubbing workflows.

## Example Script Creation

You can ask Cursor to generate a complete script for you:

```
Cursor, create a Python script that uses speechlab_mcp to:
1. Create a dubbing project for English to Japanese translation
2. Upload a video file (accept the path as a command line argument)
3. Start the dubbing process
4. Wait for completion, checking status every 30 seconds
5. Download the result when complete
```

Cursor will generate a fully functional script based on the Speechlab MCP package. 