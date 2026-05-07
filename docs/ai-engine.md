# AI Engine (Deprecated)

> **Note:** The AI Engine module is deprecated. For creating new AI-powered features, use the [LangChain integration](overview.md#ai-integration) in `server/langchain/` instead. This documentation is provided for reference and maintenance purposes.

The AI Engine module provides a simple abstraction layer for interacting with generative AI models. It was originally designed for basic prompt-response interactions before the more sophisticated LangChain integration was added.

## Overview

The module consists of:
- `AIEngine` - Base class with mock responses (for testing)
- `GeminiAIEngine` - Implementation using Google's Gemini models
- Custom exceptions for error handling

**Location:** `ai_engine/`

## Base `AIEngine` Class

The base `AIEngine` class returns mock responses. This is useful for:
- Development without API costs
- Testing without network dependencies
- CI/CD pipelines

**Location:** `ai_engine/__init__.py`

Example:
```python
from ai_engine import AIEngine

# Create an instance
ai = AIEngine()

# Run a prompt (returns mock response)
response = await ai.exec_prompt("What is 2+2?")
# Returns: "GenAI response for What is 2+2?"

# Start a chat session
session = await ai.start_session()
response = await session.send_message("Hello!")
# Returns: "GenAI chat response to Hello!"
```

### Testing Exception Handling

The base class supports special prompts that trigger exceptions for testing:

```python
# Trigger a NoResultError
await ai.exec_prompt("@raise no_result")

# Trigger a PromptBlockedError
await ai.exec_prompt("@raise blocked")
```

## GeminiAIEngine Class

The `GeminiAIEngine` class provides real AI responses using Google's Gemini models.

**Location:** `ai_engine/gemini.py`

### Initialization

```python
from ai_engine.gemini import GeminiAIEngine

# Initialize with your API key
ai = GeminiAIEngine(
    key="your-google-api-key",
    model="gemini-2.5-flash"  # Optional, this is the default
)
```

### Running Prompts

```python
# Simple prompt
response = await ai.exec_prompt("Explain Python decorators in simple terms")
print(response)
```

### Chat Sessions

Chat sessions maintain conversation history, allowing for multi-turn conversations:

```python
# Start a session with an optional system message
session = await ai.start_session("You are a helpful coding assistant.")

# Have a conversation
response1 = await session.send_message("What is a Python list?")
print(response1)

response2 = await session.send_message("How do I add items to it?")
print(response2)  # The AI remembers the context about lists
```

## Exceptions

The module defines custom exceptions for error handling:

**Location:** `ai_engine/exceptions.py`

### `NoResultError`

Raised when the AI model returns no response (empty result).

```python
from ai_engine.exceptions import NoResultError

try:
    response = await ai.exec_prompt("...")
except NoResultError:
    print("The AI didn't return a response")
```

### `PromptBlockedError`

Raised when the prompt or response is blocked by safety filters.

```python
from ai_engine.exceptions import PromptBlockedError

try:
    response = await ai.exec_prompt("...")
except PromptBlockedError:
    print("The content was blocked by safety filters")
```

## How Avoor Configures AI Engine

The AI engine is configured via the `AVR_AI` environment variable:

| Value | Engine Used |
|-------|-------------|
| `mock` (default) | Base `AIEngine` with mock responses |
| `gemini` | `GeminiAIEngine` with real Gemini API |

When using `gemini`, you must also set `AVR_GAK` to your Google API key.

**Configuration in `server/__init__.py`:**

```python
from server.env_vars import AI_ENGINE, GEMINI_API_KEY

if AI_ENGINE == "gemini":
    from ai_engine.gemini import GeminiAIEngine
    ai = GeminiAIEngine(GEMINI_API_KEY)
else:
    from ai_engine import AIEngine
    ai = AIEngine()
```

## API Reference

### AIEngine

| Method | Description |
|--------|-------------|
| `__init__()` | Creates a new AI engine instance |
| `async exec_prompt(prompt: str) -> str` | Runs a prompt and returns the response |
| `async start_session(start_message: str = None) -> AIChatSession` | Starts a chat session |

### AIChatSession

| Method | Description |
|--------|-------------|
| `async send_message(message: str) -> str` | Sends a message and returns the AI's response |

## Migration to LangChain

For new features, use the LangChain integration instead of AI Engine:

```python
# Old way (AI Engine) - simple but limited
from server import ai
response = await ai.exec_prompt("Plan my day")

# New way (LangChain) - powerful with tool support
from server.langchain import create_graph
graph = create_graph()
# Supports tools, state management, structured outputs, etc.
```

The LangChain integration provides:
- **Tools**: AI can perform actions (add to plan, export calendar)
- **State Management**: Complex conversation flows with LangGraph
- **Structured Output**: Typed responses with Pydantic models
- **Better Prompting**: System prompts with persona and constraints

See `server/langchain/` for the implementation.

## Further Reading

- [Google Generative AI Python SDK](https://ai.google.dev/gemini-api/docs/quickstart?lang=python)
- [LangChain Documentation](https://python.langchain.com/docs/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
