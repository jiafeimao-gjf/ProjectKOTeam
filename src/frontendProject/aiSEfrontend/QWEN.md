# Qwen Code Assistant - aISEfrontend Project Context

## Project Overview

This is a Vue 3 frontend application built with Vite, serving as an AI assistant interface. The application provides multiple interaction modes for users to interact with AI models, including:

- Question & Answer mode (v1 and v2)
- Software Project mode (v1 and v2)
- Custom Project mode

The application connects to a backend API server running on `http://127.0.0.1:5888` through a proxy configured in the Vite configuration. It features a modern UI with markdown rendering, code highlighting, and streamed responses from AI models.

## Project Structure

```
aiSEfrontend/
├── index.html
├── package.json
├── vite.config.js
├── README.md
├── public/
├── src/
│   ├── App.vue
│   ├── main.js
│   ├── style.css
│   ├── assets/
│   ├── components/
│   ├── pages/
│   └── router/
```

### Key Files and Components

- `App.vue`: Main application component with mode switching functionality
- `QnA.vue`: Core Question & Answer component with markdown rendering and streaming responses
- `vite.config.js`: Vite configuration with API proxy to backend server
- `package.json`: Dependencies including Vue 3, marked (markdown parser), highlight.js (code highlighting)

## Technologies Used

- **Vue 3**: Progressive JavaScript framework with Composition API
- **Vite**: Fast build tool and development server
- **Vue Router**: Client-side routing (though currently minimal)
- **marked**: Markdown parser with code highlighting support
- **highlight.js**: Syntax highlighting for code blocks
- **EventSource (SSE)**: Server-Sent Events for streaming AI responses

## Building and Running

### Development Server
```bash
# Install dependencies
npm install

# Start development server (runs on http://localhost:5173 by default)
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview
```

### API Integration
The frontend proxies API requests to `/api` endpoints to the backend server at `http://127.0.0.1:5888`. Key API endpoints include:
- `/api/chat_start`: Start a chat session with streamed responses
- `/api/models`: Get available AI models

## Development Conventions

- **Vue 3 Composition API**: Components use `<script setup>` syntax
- **Single File Components (SFC)**: Each component is contained in a `.vue` file
- **Markdown Rendering**: AI responses are parsed and rendered as markdown with code highlighting
- **Responsive Design**: CSS uses flexbox for responsive layouts
- **Streaming Responses**: AI responses are streamed using Server-Sent Events (SSE)

### Component Architecture

The application follows a modular component architecture:
- **Pages**: High-level page components (currently only QnAPage)
- **Components**: Reusable UI components for different interaction modes
- **Mode Switching**: App.vue manages different interaction modes via a ref

### Key Features

1. **Multi-Model Support**: Users can select from various AI models
2. **Real-time Streaming**: AI responses are streamed in real-time
3. **Markdown Support**: Responses are rendered with markdown formatting and code blocks
4. **Conversation History**: Maintains history of questions and answers
5. **Customizable System Prompt**: Allows users to provide system context for AI responses

## Testing

The project doesn't appear to have an explicit testing setup configured in the package.json, but Vue 3 projects typically use Vitest or similar testing frameworks.

## Backend Integration

The frontend is designed to work with a backend server running on port 5888, accessible via the `/api` proxy endpoint. The application exchanges data in JSON format and receives streamed responses via Server-Sent Events.

## Development Notes

- The application uses DOMPurify for XSS protection when rendering markdown content
- Code blocks in AI responses are automatically highlighted using highlight.js
- The UI includes loading states and error handling for API interactions
- The application supports multiple interaction modes with a clean switching mechanism