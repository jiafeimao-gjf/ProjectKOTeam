# CODEBUDDY.md

This file provides guidance to CodeBuddy Code when working with code in this repository.

## Project Overview

This is a Vue 3 frontend application built with Vite that serves as an AI assistant interface. The application provides multiple interaction modes for users to interact with AI models including Q&A, project engines, and image chat capabilities.

## Development Commands

### Core Development
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

## Architecture

### Technology Stack
- **Vue 3**: Progressive JavaScript framework with Composition API and `<script setup>` syntax
- **Vite**: Fast build tool and development server
- **Vue Router**: Client-side routing (minimal implementation)
- **marked**: Markdown parser with code highlighting support
- **highlight.js**: Syntax highlighting for code blocks
- **DOMPurify**: XSS protection for markdown rendering
- **EventSource (SSE)**: Server-Sent Events for streaming AI responses

### Project Structure
```
src/
├── App.vue                 # Main application component with mode switching
├── main.js                # Application entry point with component registration
├── style.css              # Global styles
├── components/            # Reusable Vue components
│   ├── QnA.vue           # Core Question & Answer component
│   ├── QnAv2.vue         # Enhanced Q&A component
│   ├── ProjectEngine.vue # Software project mode v1
│   ├── CustomProjectEngine.vue # Custom project mode
│   ├── SoftwareProjectEngine.vue # Software project mode v2
│   ├── HistoryQA.vue     # Historical Q&A viewer
│   └── ImageChat.vue     # Image chat functionality
├── pages/
│   └── QnAPage.vue       # Page-level Q&A component
├── utils/
│   └── llm.js            # LLM integration utilities for streaming responses
└── router/
    └── router.js         # Vue Router configuration
```

### Backend Integration
The frontend proxies API requests to a backend server:
- **Proxy Configuration**: `/api` endpoints proxy to `http://127.0.0.1:5888`
- **Key API Endpoints**:
  - `/api/chat_start`: Start chat session with streamed responses
  - `/api/models`: Get available AI models
  - `/api/get_his_list`: Retrieve chat history list
  - `/api/get_his_content`: Get specific chat history content
  - `/api/image_chat`: Handle image upload and chat

### Component Architecture
- **Mode Switching**: App.vue manages different interaction modes via reactive `mode` ref
- **Component Registration**: All components are globally registered in main.js
- **Streaming Responses**: AI responses use EventSource for real-time streaming
- **Markdown Rendering**: Responses are parsed with marked and syntax highlighted with highlight.js

### Key Features
1. **Multi-Mode Interface**: 7 different interaction modes (Q&A, Q&A v2, Project modes, Custom Project, History, Image Chat)
2. **Real-time Streaming**: AI responses stream in real-time using Server-Sent Events
3. **Markdown Support**: Full markdown rendering with code highlighting and XSS protection
4. **Model Selection**: Users can choose from available AI models
5. **System Prompts**: Support for custom system context/prefix prompts
6. **Chat History**: Persistent chat history with retrieval capabilities

## Development Conventions

### Vue 3 Patterns
- Use `<script setup>` syntax for components
- Leverage Composition API with `ref`, `computed`, `watch`, etc.
- Follow Single File Component (SFC) structure

### API Integration
- Use the `fetchStreamAnswer` utility from `utils/llm.js` for streaming responses
- All API calls go through the `/api` proxy configured in vite.config.js
- Handle both streaming responses and error states appropriately

### Styling
- Scoped CSS in components with `<style scoped>`
- Flexbox-based responsive layouts
- Component-specific class naming following BEM-like patterns

### Error Handling
- Implement proper error handling for API requests
- Use loading states during async operations
- Handle EventSource connection errors gracefully

## Backend Requirements

The frontend requires a backend server running on `http://127.0.0.1:5888` with the following capabilities:
- Support for streaming chat responses via Server-Sent Events
- Multiple AI model endpoints
- Chat history persistence and retrieval
- Image upload and processing capabilities
- CORS configuration for the frontend origin