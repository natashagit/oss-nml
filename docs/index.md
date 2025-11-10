# Welcome to the AI Client Service

This project is a professional-grade AI client service built using a component-based architecture with a clear separation between interface and implementation.

The service provides chat completion capabilities using OpenAI's API with OAuth 2.0 authentication via Google. It demonstrates best practices for building maintainable, testable, and scalable Python applications.

## Key Features

- **OAuth 2.0 Authentication**: Secure user authentication via Google OAuth
- **Session-Based Storage**: No database required - credentials stored in encrypted sessions
- **Component-Based Architecture**: Clear separation of concerns with adapter pattern
- **Type Safety**: Type-safe dataclasses for all API models
- **RESTful API**: FastAPI service with interactive documentation
- **Streaming Support**: Real-time streaming of chat completions

## Architecture Overview

The project is organized into five main components:

1. **`ai_client_api`**: Abstract interface defining the AI client contract
2. **`openai_client_impl`**: Concrete implementation using OpenAI's API
3. **`ai_client_service`**: FastAPI service exposing REST endpoints
4. **`ai_client_adapter`**: Adapter wrapping the service client
5. **`ai_client_service_client`**: Auto-generated client from OpenAPI spec

This documentation site provides an overview of the project's architecture, API contracts, and usage guidelines.
