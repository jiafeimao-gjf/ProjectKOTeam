# LLM Service Backend Project

## Project Overview

This is a Flask-based backend service that provides an interface to Large Language Models (LLM) through Ollama. The service offers various features including text chat, image analysis, model listing, and chat history management. It's designed as part of a larger ProjectKO Team system.

## Architecture

The project follows a simple Flask-based architecture with the following key components:

- **app.py**: Main Flask application with REST API endpoints
- **src/llm_caller.py**: Core LLM interaction logic with streaming capabilities
- **log/log_utils.py**: Logging utilities
- **db/mysql_uils.py**: MySQL database utilities (currently not actively used)
- **history/**: Directory for storing chat history in markdown format
- **test/**: Test files for API and LLM functionality

## Key Features

1. **Text Chat**: Provides streaming responses via Server-Sent Events (SSE)
2. **Image Chat**: Supports image analysis with base64 encoding
3. **Model Listing**: Retrieves available models from Ollama
4. **Role-based Prompts**: Configurable prompts for different roles (project manager, product manager, architect, developer, tester)
5. **Chat History**: Automatic saving and retrieval of conversation history
6. **Browser Chat**: Additional endpoint for browser-based chat functionality

## Dependencies

- Flask: Web framework
- Ollama: LLM interface library
- SQLAlchemy: For MySQL database connection
- PyMongo: For MongoDB connection (currently commented out)

## API Documentation

### 1. Chat Initialization
**Endpoint:** `POST /chat_start`

**Description:** Initializes a new chat session and returns a UUID for the session.

**Request Body:**
```json
{
  "prompt": "string, required - The initial prompt for the chat",
  "model": "string, required - The model to use for the chat"
}
```

**Response:**
- Success: A string with the format `/api/chat?uuid={session-uuid}`
- Error: Error message if prompt or model is empty

### 2. Chat Streaming
**Endpoint:** `GET /chat`

**Description:** Streams chat responses using Server-Sent Events (SSE). Requires a valid UUID from `/chat_start`.

**Query Parameters:**
```
uuid: string, required - The session UUID from /chat_start
```

**Response:**
- Success: Streaming response in SSE format with chat content
- Error: Error message if UUID is invalid or missing

### 3. Model Listing
**Endpoint:** `GET /models`

**Description:** Retrieves a list of available models from Ollama.

**Request:** No parameters required

**Response:**
```json
{
  "models": ["array of model names"]
}
```

### 4. Get Prompt Configurations
**Endpoint:** `GET /prompt_config`

**Description:** Retrieves the available role-based prompt configurations.

**Request:** No parameters required

**Response:**
```json
{
  "prompts": ["array of role-based prompts"]
}
```

### 5. Update Prompt Configurations
**Endpoint:** `POST /prompt_config`

**Description:** Updates the role-based prompt configurations. (Currently disabled in code)

**Request Body:**
```json
{
  "prompts": ["array of role-based prompts, required"]
}
```

**Response:**
```json
{
  "msg": "success",
  "code": 0
}
```

### 6. Browser Chat
**Endpoint:** `POST /browser_chat`

**Description:** Direct chat endpoint for browser integration.

**Request Body:**
```json
{
  "question": "string, required - The question to ask the model"
}
```

**Response:**
- Success: Streaming response in SSE format with chat content
- Error: JSON error response if question is missing

### 7. Image Chat
**Endpoint:** `POST /image_chat`

**Description:** Performs image analysis and returns insights about the image.

**Form Parameters:**
```
image: file, required - The image file to analyze
model: string, optional - The model to use (default: "qwen3-vl:4b")
prompt: string, optional - The prompt for image analysis (default: "请分析图片, 最后一行用10个字以内的总结这个图片")
```

**Response:**
- Success: Streaming response in SSE format with image analysis
- Error: JSON error response if image is missing

### 8. Get History List
**Endpoint:** `GET /get_his_list`

**Description:** Retrieves a list of historical chat sessions.

**Request:** No parameters required

**Response:**
```json
{
  "directory_name": ["array of file names in that directory"]
}
```

### 9. Get History Content
**Endpoint:** `GET /get_his_content`

**Description:** Retrieves the content of a specific historical chat file.

**Query Parameters:**
```
file_name: string, required - The name of the history file to retrieve
```

**Response:**
```json
{
  "msg": "success",
  "code": 0,
  "content": "string - The content of the history file"
}
```

## Building and Running

To run the project:

1. Ensure Ollama is installed and running with the required models
2. Install Python dependencies (likely in a requirements.txt file not found in the project)
3. Run the application:
   ```bash
   python app.py
   ```
   or
   ```bash
   python -m flask run --host=0.0.0.0 --port=5888
   ```

The application runs on port 5888 by default and is accessible on all network interfaces (0.0.0.0).

## Development Conventions

- Uses Server-Sent Events (SSE) for streaming responses
- Markdown format for storing chat history
- Structured logging throughout the application
- Role-based prompt system for different user types
- Base64 encoding for image data in image chat functionality

## Testing

The project includes test files in the `test/` directory:
- `llmtest.py`: Basic LLM functionality test
- `testapi.py`: API endpoint testing script
- `mongo_test.py`: MongoDB testing (though MongoDB is currently commented out)

## Notes

- The project has database utilities for MySQL but currently uses file-based storage for chat history
- MongoDB code is present but commented out in the LLM caller module
- The system is designed to support multiple LLM models through Ollama
- History files are stored in timestamp-based directories under the `history/` folder