# Contributing Guide

This guide will help you understand how the codebase is organized, how components work together, and how to start contributing.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Repository Structure](#repository-structure)
- [Testing Strategy](#testing-strategy)
- [Development Tools](#development-tools)
- [Getting Started](#getting-started)

---

## Architecture Overview

### Components

This project uses a **component-based architecture** that separates abstract interfaces from concrete implementations. There are two main components in this repository:

#### 1. `mail_client_api` (Abstract Interface)

**Location**: `src/mail_client_api/`

**Purpose**: Defines the contract for what any mail client should be able to do, without specifying how to do it.

**Key Classes**:
- **`Client` (ABC)**: Abstract base class defining mail client operations:
  - `get_messages(max_results: int) -> Iterator[Message]` - Fetch multiple messages
  - `get_message(message_id: str) -> Message` - Fetch a specific message
  - `delete_message(message_id: str) -> bool` - Delete a message
  - `mark_as_read(message_id: str) -> bool` - Mark a message as read

- **`Message` (ABC)**: Abstract base class defining message properties:
  - `id: str` - Unique message identifier
  - `from_: str` - Sender's email address
  - `to: str` - Recipient's email address
  - `date: str` - Date the message was sent
  - `subject: str` - Message subject line
  - `body: str` - Message body content

**Factory Functions**: 
- `get_client(*, interactive: bool) -> Client` - Returns a Client instance (placeholder, replaced at runtime)
- `get_message(msg_id: str, raw_data: str) -> Message` - Returns a Message instance (placeholder, replaced at runtime)

**Dependencies**: None (pure abstraction layer)

#### 2. `gmail_client_impl` (Concrete Implementation)

**Location**: `src/gmail_client_impl/`

**Purpose**: Provides a Gmail-specific implementation of the mail client contract using Google's Gmail API.

**Key Classes**:
- **`GmailClient`**: Concrete implementation of `Client`
  - Handles OAuth2 authentication (environment variables, token files, interactive flow)
  - Makes API calls to Gmail API
  - Returns `Message` objects via the factory function
  
- **`GmailMessage`**: Concrete implementation of `Message`
  - Parses base64-encoded Gmail raw message data
  - Decodes RFC 2047 email headers
  - Extracts plain text body from multipart messages
  - Handles malformed messages gracefully

**Features**:
- Multiple authentication modes (environment variables, token file, interactive OAuth)
- Robust error handling for API failures
- Binary garbage detection for malformed messages
- Automatic credential refresh

**Dependencies**: 
- `mail_client_api` (implements its contracts)
- `google-api-python-client`, `google-auth`, `google-auth-oauthlib` (for Gmail API access)

#### How Components Interact

The interaction follows a **dependency injection pattern**:

```
┌─────────────────────────┐
│       main.py           │
│    (Application)        │
└───────────┬─────────────┘
            │
            │ 1. import mail_client_api
            │ 2. import gmail_client_impl  ← triggers registration
            │
            ▼
┌─────────────────────────┐
│   mail_client_api       │  ◄──── Defines abstract contracts
│   (Interface Layer)     │        (Client ABC, Message ABC)
└──────────▲──────────────┘
           │
           │ implements & registers
           │
┌──────────┴──────────────┐
│  gmail_client_impl      │  ◄──── Fulfills contracts
│  (Implementation)       │        (GmailClient, GmailMessage)
└─────────────────────────┘        Registers at import time
```

**Step-by-step flow**:

1. `main.py` imports `mail_client_api` - the abstract interface layer is loaded
2. `main.py` imports `gmail_client_impl` - this triggers automatic registration:
   - `gmail_client_impl/__init__.py` calls `register()` at import time
   - The `register()` function replaces the abstract factory functions with concrete implementations
3. Application code calls `mail_client_api.get_client()` - returns a `GmailClient` instance
4. Application uses the client through the `Client` interface - doesn't know or care that it's specifically Gmail

**Key Benefit**: The application (`main.py`) only depends on the stable interface (`mail_client_api`), never on the volatile implementation (`gmail_client_impl`). We can swap Gmail for Outlook, IMAP, or any other implementation without changing a single line in `main.py`.

### Interface Design

The project uses **Abstract Base Classes (ABC)** to define interfaces. This design follows key principles from [A Philosophy of Software Design by John Ousterhout](https://www.youtube.com/watch?v=bmSAYlu0NcY).

#### Principle 1: Deep Modules with Simple Interfaces

**Definition**: The best modules are those that provide powerful functionality through simple interfaces. The interface should be much simpler than the implementation.

**How it is applied here**:

The `Client` interface exposes only **four methods**:

```python
class Client(ABC):
    """Abstract base class representing a mail client for email operations."""
    
    @abstractmethod
    def get_messages(self, max_results: int = 10) -> Iterator[Message]:
        """Return an iterator of messages from the inbox."""
        raise NotImplementedError
    
    @abstractmethod
    def get_message(self, message_id: str) -> Message:
        """Return a message by its ID."""
        raise NotImplementedError
    
    @abstractmethod
    def delete_message(self, message_id: str) -> bool:
        """Delete a message by its ID."""
        raise NotImplementedError
    
    @abstractmethod
    def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read by its ID."""
        raise NotImplementedError
```

This simple interface hides **massive complexity**:
- OAuth2 authentication (multiple modes: env vars, token files, interactive flow)
- HTTP error handling and retries
- Base64 decoding of Gmail message data
- RFC 2047 email header decoding
- Multipart message parsing
- Character encoding detection
- Binary garbage detection
- API rate limiting and pagination

The interface is **4 methods**. The implementation is **~350 lines of code**. That's a deep module.

#### Principle 2: Information Hiding

**Definition**: Hide implementation details that are likely to change. Expose only what users of the module need to know.

**How it is applied here**:

The `Message` interface uses **read-only properties**:

```python
class Message(ABC):
    """Abstract base class representing an email message."""
    
    @property
    @abstractmethod
    def id(self) -> str:
        """Return the unique identifier of the message."""
        raise NotImplementedError
    
    @property
    @abstractmethod
    def from_(self) -> str:
        """Return the sender's email address."""
        raise NotImplementedError
    
    @property
    @abstractmethod
    def to(self) -> str:
        """Return the recipient's email address."""
        raise NotImplementedError
    
    @property
    @abstractmethod
    def date(self) -> str:
        """Return the date the message was sent."""
        raise NotImplementedError
    
    @property
    @abstractmethod
    def subject(self) -> str:
        """Return the subject line of the message."""
        raise NotImplementedError
    
    @property
    @abstractmethod
    def body(self) -> str:
        """Return the plain text content of the message."""
        raise NotImplementedError
```

What users **don't** need to know:
- How Gmail stores messages (base64-encoded raw format)
- How to parse RFC 2047 encoded headers (e.g., `=?UTF-8?B?...?=`)
- How to extract plain text from multipart MIME messages
- How to handle malformed or binary garbage data
- What character encoding was used in the original message

All these details are **hidden** inside `GmailMessage`. Users just access `.subject` or `.body` and get a string.

#### Principle 3: Design for Change

**Definition**: Design interfaces so that the implementation can evolve without breaking client code.

**How it is applied here**:

The interface-implementation split means we can make changes without breaking anything:

**Changes that are easy**:
- Replace Gmail with Outlook, IMAP, or any other email service (just create a new implementation)
- Update Gmail API from v1 to v2 (only changes `GmailClient`, not the interface)
- Add caching, retry logic, or logging (implementation detail)
- Change authentication mechanism (implementation detail)
- Optimize message parsing (implementation detail)

**Changes that would be hard** (requiring interface changes):
- Add a new method like `send_message()` (changes the contract - all implementations must support it)
- Change `get_messages()` to return a list instead of an iterator (breaks existing code)

By keeping the interface stable, we protect all code that depends on it.

### Design Justifications

#### Why Abstract Base Classes (ABC) instead of duck typing?

Python supports "duck typing" - if it walks like a duck and quacks like a duck, it's a duck. Why not just implement classes with matching method names?

**Reasons for ABC**:

1. **Explicit contracts**: ABCs make it clear that `GmailClient` **intentionally** implements the `Client` interface. With duck typing, matching methods could be coincidental.

2. **Compile-time checking**: Type checkers like MyPy can verify that implementations match the contract before the code even runs:
   ```bash
   $ uv run mypy src/
   # Will catch if GmailClient is missing a required method
   ```

3. **Runtime enforcement**: You cannot instantiate an ABC directly, and Python prevents incomplete implementations:
   ```python
   class BadClient(Client):
       def get_messages(self):
           pass  # Missing 3 other methods!
   
   client = BadClient()  # Raises TypeError at runtime
   ```

4. **Documentation**: ABCs serve as living documentation. IDEs can auto-complete methods, and developers can see exactly what needs to be implemented.

5. **Introspection**: ABCs can be introspected at runtime:
   ```python
   isinstance(gmail_client, mail_client_api.Client)  # True
   ```

#### Why properties for Message instead of methods?

We could have used methods like `get_subject()` instead of properties like `.subject`. Why properties?

**Reasons for properties**:

1. **Read-only access**: Properties can be read-only, preventing accidental modification:
   ```python
   message.subject = "new subject"  # Error - can't set attribute
   ```

2. **Cleaner syntax**: Properties look like attributes, making code more readable:
   ```python
   print(message.subject)      # Clean, natural
   print(message.get_subject()) # Verbose, method call overhead feeling
   ```

3. **Hides computation**: Properties hide that parsing might be happening behind the scenes:
   ```python
   # User thinks they're just accessing an attribute
   # Actually: decoding RFC 2047, handling errors, etc.
   subject = message.subject
   ```

4. **Consistent with Python conventions**: Python's built-in types use properties (e.g., `exception.args`, `datetime.year`)

#### Why factory functions instead of constructors?

Instead of requiring users to call `GmailClient()` directly, we provide `get_client()`. Why?

**Reasons for factory functions**:

1. **Stable entry point**: The factory function name (`get_client`) never changes, even if the implementation class name changes.

2. **Dependency injection**: Factory functions can be replaced at runtime (see next section):
   ```python
   mail_client_api.get_client = get_client_impl  # Injection happens here
   ```

3. **Hides implementation**: Users don't need to know which class to import:
   ```python
   # Good: Works with any implementation
   client = mail_client_api.get_client()
   
   # Bad: Tightly coupled to Gmail
   client = GmailClient()
   ```

4. **Configuration flexibility**: Factory functions can handle complex initialization:
   ```python
   client = mail_client_api.get_client(interactive=False)
   # Factory decides how to handle the interactive parameter
   ```

### Implementation Details

This section explains **how** the interface is implemented in Python and what language features make this design possible.

#### Python Feature 1: Abstract Base Classes (ABC)

Python's `abc` module provides the `ABC` class and `@abstractmethod` decorator for defining interfaces.

**Defining an abstract interface**:

```python
# src/mail_client_api/src/mail_client_api/client.py

from abc import ABC, abstractmethod
from collections.abc import Iterator
from mail_client_api.message import Message

class Client(ABC):
    """Abstract base class representing a mail client for email operations."""

    @abstractmethod
    def get_message(self, message_id: str) -> Message:
        """Return a message by its ID."""
        raise NotImplementedError

    @abstractmethod
    def delete_message(self, message_id: str) -> bool:
        """Delete a message by its ID."""
        raise NotImplementedError

    @abstractmethod
    def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read by its ID."""
        raise NotImplementedError

    @abstractmethod
    def get_messages(self, max_results: int = 10) -> Iterator[Message]:
        """Return an iterator of messages from the inbox."""
        raise NotImplementedError
```

**What this accomplishes**:

1. **Cannot instantiate directly**: Trying to create a `Client()` will raise `TypeError`
2. **Enforces implementation**: Subclasses must implement all `@abstractmethod` methods or they cannot be instantiated
3. **Type checking**: MyPy can verify that `GmailClient` implements all required methods
4. **Documentation**: The ABC serves as a contract that developers can reference

**Implementing the interface**:

```python
# src/gmail_client_impl/src/gmail_client_impl/gmail_impl.py

import mail_client_api

class GmailClient(mail_client_api.Client):
    """Concrete implementation of the Client abstraction using Gmail API."""
    
    def __init__(self, service: Resource | None = None, *, interactive: bool = False) -> None:
        # ... authentication logic ...
        self.service = build("gmail", "v1", credentials=creds)
    
    def get_message(self, message_id: str) -> message.Message:
        # ... Gmail API call ...
        return message.get_message(msg_id=message_id, raw_data=raw_content)
    
    def delete_message(self, message_id: str) -> bool:
        # ... Gmail API call ...
        return True
    
    def mark_as_read(self, message_id: str) -> bool:
        # ... Gmail API call ...
        return True
    
    def get_messages(self, max_results: int = 10) -> Iterator[message.Message]:
        # ... Gmail API calls ...
        for msg_summary in messages_summary:
            yield message.get_message(...)
```

Because `GmailClient` inherits from `mail_client_api.Client` and implements all abstract methods, it's a valid implementation.

#### Python Feature 2: Properties with @abstractmethod

Python's `@property` decorator combined with `@abstractmethod` creates abstract read-only attributes.

**Defining abstract properties**:

```python
# src/mail_client_api/src/mail_client_api/message.py

from abc import ABC, abstractmethod

class Message(ABC):
    """Abstract base class representing an email message."""

    @property
    @abstractmethod
    def id(self) -> str:
        """Return the unique identifier of the message."""
        raise NotImplementedError

    @property
    @abstractmethod
    def from_(self) -> str:
        """Return the sender's email address."""
        raise NotImplementedError

    @property
    @abstractmethod
    def to(self) -> str:
        """Return the recipient's email address."""
        raise NotImplementedError

    @property
    @abstractmethod
    def date(self) -> str:
        """Return the date the message was sent."""
        raise NotImplementedError

    @property
    @abstractmethod
    def subject(self) -> str:
        """Return the subject line of the message."""
        raise NotImplementedError

    @property
    @abstractmethod
    def body(self) -> str:
        """Return the plain text content of the message."""
        raise NotImplementedError
```

**Implementing abstract properties**:

```python
# src/gmail_client_impl/src/gmail_client_impl/message_impl.py

class GmailMessage(message.Message):
    """Concrete implementation of the Message abstraction for Gmail messages."""

    def __init__(self, msg_id: str, raw_data: str) -> None:
        self._id = msg_id
        self._raw_data = raw_data
        decoded_bytes = base64.urlsafe_b64decode(raw_data.encode("utf-8"))
        self._parsed: EmailMessage = email.message_from_bytes(decoded_bytes)

    @property
    def id(self) -> str:
        """Get the unique message identifier."""
        return self._id

    @property
    def from_(self) -> str:
        """Get the email sender."""
        return self._parsed.get("From", "")

    @property
    def subject(self) -> str:
        """Get the email subject, decoding RFC 2047 if necessary."""
        subject_header = self._parsed.get("Subject", "")
        # ... complex decoding logic ...
        return decoded_subject

    # ... other properties ...
```

The combination of `@property` and `@abstractmethod` forces implementations to provide these properties while allowing complex logic behind simple attribute access.

#### Python Feature 3: Function Reassignment (for Dependency Injection)

Python treats functions as first-class objects - they can be reassigned at runtime. This enables the factory pattern.

**Defining placeholder factory functions**:

```python
# src/mail_client_api/src/mail_client_api/client.py

def get_client(*, interactive: bool = False) -> Client:
    """Return an instance of a Mail Client."""
    raise NotImplementedError
```

```python
# src/mail_client_api/src/mail_client_api/message.py

def get_message(msg_id: str, raw_data: str) -> Message:
    """Return an instance of a Message."""
    raise NotImplementedError
```

Initially, these functions just raise `NotImplementedError`. They're placeholders waiting to be replaced.

**Replacing factory functions at runtime**:

```python
# src/gmail_client_impl/src/gmail_client_impl/gmail_impl.py

def get_client_impl(*, interactive: bool = False) -> mail_client_api.Client:
    """Return a configured GmailClient instance."""
    return GmailClient(interactive=interactive)

def register() -> None:
    """Register the Gmail client implementation with the mail client API."""
    mail_client_api.get_client = get_client_impl  # ← Function reassignment!
```

```python
# src/gmail_client_impl/src/gmail_client_impl/message_impl.py

def get_message_impl(msg_id: str, raw_data: str) -> message.Message:
    """Return an instance of the concrete GmailMessage implementation."""
    return GmailMessage(msg_id=msg_id, raw_data=raw_data)

def register() -> None:
    """Register the Gmail message implementation with the message abstraction."""
    message.get_message = get_message_impl  # ← Function reassignment!
    mail_client_api.get_message = get_message_impl  # ← Also exported from top-level API
```

After `register()` is called, `mail_client_api.get_client()` no longer raises `NotImplementedError` - it returns a real `GmailClient` instance.

**Why this works in Python**:

In Python, module-level functions are just attributes of the module object. Reassigning them is as simple as:
```python
import some_module
some_module.function_name = new_function  # Perfectly legal!
```

This would be difficult or impossible in statically-typed languages like Java or C++, but Python's dynamic nature makes it natural.

#### Summary of Python Features

| Feature | Purpose | Where Used |
|---------|---------|------------|
| `abc.ABC` | Define abstract base classes | `Client`, `Message` |
| `@abstractmethod` | Mark methods that must be implemented | All methods in `Client` and `Message` |
| `@property` | Create attribute-like access for methods | All attributes in `Message` |
| Function reassignment | Enable dependency injection pattern | `register()` functions |
| First-class functions | Treat functions as objects that can be passed/assigned | Factory functions |

#### Extra Credit: ABC vs. Protocol

**Protocol** (from the `typing` module) provides an alternative approach to defining interfaces in Python. While this project uses ABC, it's worth understanding the difference.

**What is Protocol?**

Protocol enables **structural subtyping** (also called "duck typing") - a class satisfies a Protocol if it has the right methods, regardless of inheritance.

**Example using Protocol**:

```python
from typing import Protocol, Iterator

class Client(Protocol):
    """Protocol defining a mail client interface."""
    
    def get_messages(self, max_results: int = 10) -> Iterator[Message]: ...
    def get_message(self, message_id: str) -> Message: ...
    def delete_message(self, message_id: str) -> bool: ...
    def mark_as_read(self, message_id: str) -> bool: ...
```

With Protocol, `GmailClient` **doesn't need to inherit** from `Client`:

```python
class GmailClient:  # No inheritance!
    """This class satisfies the Client protocol just by having the right methods."""
    
    def get_messages(self, max_results: int = 10) -> Iterator[Message]:
        # implementation...
    
    # ... other methods ...

# This type checks fine with MyPy:
def process_client(client: Client) -> None:
    messages = client.get_messages()  # Works!

gmail_client = GmailClient()
process_client(gmail_client)  # ✅ MyPy accepts this
```

**Key Differences: ABC vs. Protocol**

| Aspect | ABC | Protocol |
|--------|-----|----------|
| **Inheritance Required** | Yes - must inherit from ABC | No - just needs matching methods |
| **Type Checking Style** | **Nominal** (by name) | **Structural** (by shape) |
| **Runtime Enforcement** | Yes - raises `TypeError` for incomplete implementations | No - only static type checking |
| **Instantiation Prevention** | Cannot instantiate abstract class | Can instantiate (just a regular class) |
| **Intent Communication** | Explicit: `class GmailClient(Client)` says "I **am** a Client" | Implicit: class just happens to match |
| **Backwards Compatibility** | Must modify existing classes to inherit | Can type-check existing code without changes |
| **Documentation Value** | High - inheritance visible in code | Lower - protocol conformance implicit |

**When to Use ABC (why this project uses it)**:

1. **Explicit contracts**: You want to make it clear that a class **intentionally** implements an interface:
   ```python
   class GmailClient(mail_client_api.Client):  # ← Clear intent
   ```

2. **Runtime safety**: You want Python to prevent incomplete implementations at runtime:
   ```python
   class BadClient(Client):
       def get_messages(self):
           pass
   # Missing 3 methods!
   client = BadClient()  # TypeError: Can't instantiate abstract class
   ```

3. **Framework design**: You're building a framework where implementations are plugins/extensions

4. **Documentation**: The inheritance relationship serves as living documentation

5. **IDE support**: Better autocomplete and navigation

**When to Use Protocol**:

1. **Retrofitting types**: Adding types to existing code you can't modify:
   ```python
   # Third-party library has no types
   class ThirdPartyMailClient:
       def get_messages(self): ...
   
   # You can type-check it against your Protocol
   def process(client: Client) -> None: ...  # Protocol
   process(ThirdPartyMailClient())  # Works!
   ```

2. **Duck typing**: Working in a codebase that relies on duck typing:
   ```python
   # Anything file-like works
   def write_data(file: SupportsWrite) -> None:
       file.write("data")
   ```

3. **No inheritance overhead**: When you don't want to modify existing class hierarchies

4. **Library code**: When you're writing a library that needs to work with many types

**Example: How Protocol Would Work in This Project**

If we used Protocol instead of ABC:

```python
# mail_client_api/client.py
from typing import Protocol, Iterator

class Client(Protocol):
    """Protocol defining mail client interface."""
    def get_messages(self, max_results: int = 10) -> Iterator[Message]: ...
    def get_message(self, message_id: str) -> Message: ...
    def delete_message(self, message_id: str) -> bool: ...
    def mark_as_read(self, message_id: str) -> bool: ...
```

```python
# gmail_client_impl/gmail_impl.py
class GmailClient:  # No inheritance!
    """Just happens to match the Client protocol."""
    def get_messages(self, max_results: int = 10) -> Iterator[Message]:
        # implementation
```

**What we'd lose**:
- No runtime enforcement (incomplete implementations wouldn't error at instantiation)
- Less clear intent (is `GmailClient` meant to be a `Client` or just coincidence?)
- Can't use `isinstance(gmail_client, Client)` checks
- Less explicit documentation

**What we'd gain**:
- Could type-check third-party mail clients without modifying them
- Slightly more flexible (no inheritance required)

**Conclusion**: For this project, **ABC is the right choice** because we're designing a framework with explicit plugin points, and we want runtime guarantees and clear contracts. Protocol would be more appropriate if we were trying to type-check existing codebases that we can't modify.

### Dependency Injection

This project uses a **function replacement pattern** for dependency injection. This pattern decouples the abstract interface from concrete implementations.

#### Where Injection Occurs

Dependency injection happens in **three steps**:

**Step 1: Abstract factory functions are defined as placeholders**

```python
# src/mail_client_api/src/mail_client_api/client.py

def get_client(*, interactive: bool = False) -> Client:
    """Return an instance of a Mail Client."""
    raise NotImplementedError
```

```python
# src/mail_client_api/src/mail_client_api/message.py

def get_message(msg_id: str, raw_data: str) -> Message:
    """Return an instance of a Message.
    
    Args:
        msg_id (str): The unique identifier for the message.
        raw_data (str): The raw data used to construct the message.
    
    Returns:
        Message: An instance conforming to the Message contract.
    
    Raises:
        NotImplementedError: If the function is not overridden by an implementation.
    """
    raise NotImplementedError
```

At this point, calling `mail_client_api.get_client()` would raise `NotImplementedError`.

**Step 2: Implementation provides concrete factory functions and registration**

```python
# src/gmail_client_impl/src/gmail_client_impl/gmail_impl.py

def get_client_impl(*, interactive: bool = False) -> mail_client_api.Client:
    """Return a configured :class:`GmailClient` instance."""
    return GmailClient(interactive=interactive)

def register() -> None:
    """Register the Gmail client implementation with the mail client API."""
    mail_client_api.get_client = get_client_impl  # ← INJECTION HAPPENS HERE
```

```python
# src/gmail_client_impl/src/gmail_client_impl/message_impl.py

def get_message_impl(msg_id: str, raw_data: str) -> message.Message:
    """Return an instance of the concrete GmailMessage implementation."""
    return GmailMessage(msg_id=msg_id, raw_data=raw_data)

def register() -> None:
    """Register the Gmail message implementation with the message abstraction."""
    message.get_message = get_message_impl  # ← INJECTION HAPPENS HERE
    mail_client_api.get_message = get_message_impl  # ← ALSO HERE (top-level export)
```

**Step 3: Registration is triggered automatically at import time**

```python
# src/gmail_client_impl/src/gmail_client_impl/__init__.py

from gmail_client_impl.gmail_impl import (
    GmailClient,
    get_client_impl,
)
from gmail_client_impl.gmail_impl import (
    register as _register_client,
)
from gmail_client_impl.message_impl import (
    GmailMessage,
    get_message_impl,
)
from gmail_client_impl.message_impl import (
    register as _register_message,
)

__all__ = [
    "GmailClient",
    "GmailMessage",
    "get_client_impl",
    "get_message_impl",
    "register",
]

def register() -> None:
    """Register the Gmail client and message implementations."""
    _register_client()  # Replaces mail_client_api.get_client
    _register_message()  # Replaces mail_client_api.get_message

# Dependency Injection happens at import time
register()  # ← AUTOMATIC REGISTRATION WHEN MODULE IS IMPORTED
```

**The moment you import `gmail_client_impl`, line 34 calls `register()`, which replaces the placeholder factory functions with concrete implementations.**

#### How It Works in Practice

```python
# main.py

import mail_client_api      # Step 1: Load abstract interface
                           # mail_client_api.get_client raises NotImplementedError

import gmail_client_impl    # Step 2: Load implementation
                           # __init__.py calls register()
                           # mail_client_api.get_client is NOW replaced

# Step 3: Use the client
client = mail_client_api.get_client(interactive=False)
# Returns: GmailClient instance

# Type: mail_client_api.Client (interface)
# Runtime: gmail_client_impl.GmailClient (implementation)

messages = list(client.get_messages(max_results=3))
# Behind the scenes: GmailClient talks to Gmail API
```

#### What This Pattern Enables

**1. Loose Coupling**

Application code never imports or references `GmailClient` directly:

```python
# Good: Depends only on abstraction
import mail_client_api
import gmail_client_impl  # Only this line mentions Gmail
client = mail_client_api.get_client()

# Bad: Tightly coupled to Gmail
from gmail_client_impl import GmailClient
client = GmailClient()
```

The application depends on the **stable interface**, not the **volatile implementation**.

**2. Easy Substitution**

Want to switch from Gmail to Outlook? Just:

```python
# Step 1: Create OutlookClient that implements Client ABC
class OutlookClient(mail_client_api.Client):
    def get_messages(self, max_results: int = 10):
        # Use Outlook API
        ...

# Step 2: Create registration function
def register():
    mail_client_api.get_client = lambda **kwargs: OutlookClient(**kwargs)

# Step 3: Change the import in main.py
import mail_client_api
import outlook_client_impl  # Changed from gmail_client_impl

# Everything else stays the same!
client = mail_client_api.get_client()
```

**3. Testability**

Tests can inject mocks without changing production code:

```python
# test_main_application.py

import mail_client_api
from unittest.mock import Mock

def test_main_logic():
    # Create mock client
    mock_client = Mock(spec=mail_client_api.Client)
    mock_message = Mock(spec=mail_client_api.Message)
    mock_message.id = "123"
    mock_message.subject = "Test"
    mock_client.get_messages.return_value = [mock_message]
    
    # Inject mock (replace the factory function)
    mail_client_api.get_client = lambda **kwargs: mock_client
    
    # Now any code calling mail_client_api.get_client() gets the mock
    client = mail_client_api.get_client()
    messages = list(client.get_messages())
    
    assert len(messages) == 1
    assert messages[0].id == "123"
```

**4. Configuration Over Code**

The choice of implementation is made through **imports**, not code changes:

```python
# Use Gmail
import gmail_client_impl

# Use Outlook
import outlook_client_impl

# Use Mock (for testing)
import mock_client_impl
```

No conditionals, no configuration files, no complex wiring - just change the import.

**5. Multiple Implementations Can Coexist**

You can have multiple implementations available and choose at runtime:

```python
import mail_client_api
import gmail_client_impl
import outlook_client_impl  # Both loaded

# Manually select implementation
if use_gmail:
    mail_client_api.get_client = gmail_client_impl.get_client_impl
else:
    mail_client_api.get_client = outlook_client_impl.get_client_impl

client = mail_client_api.get_client()
```

#### Why Import-Time Injection?

**Advantages**:
- **Simplicity**: No dependency injection frameworks or complex configuration needed
- **Explicitness**: Clear from imports which implementation is active
- **Python-idiomatic**: Leverages Python's dynamic nature and module system
- **Zero boilerplate**: No decorators, no configuration files, just imports
- **Automatic**: Happens transparently when you import the implementation

**Disadvantages**:
- **Import side effects**: Importing a module modifies global state (the factory function)
- **Testing complexity**: Tests must manage injection order carefully
- **Implicit**: May not be obvious that importing `gmail_client_impl` changes `mail_client_api`'s behavior

For this project, the advantages outweigh the disadvantages. The pattern keeps the codebase simple while maintaining flexibility.

---

## Repository Structure

### Project Organization

```
oss-taapp/
├── src/                            # Source packages (uv workspace members)
│   ├── mail_client_api/            # Abstract mail client interface
│   │   ├── src/
│   │   │   └── mail_client_api/    # Package source code
│   │   │       ├── __init__.py     # Public API exports
│   │   │       ├── client.py       # Client ABC and factory
│   │   │       └── message.py      # Message ABC and factory
│   │   ├── tests/                  # Unit tests
│   │   ├── pyproject.toml          # Package configuration
│   │   └── README.md
│   │
│   └── gmail_client_impl/          # Gmail implementation
│       ├── src/
│       │   └── gmail_client_impl/
│       │       ├── __init__.py     # Exports and DI registration
│       │       ├── gmail_impl.py   # GmailClient implementation
│       │       └── message_impl.py # GmailMessage implementation
│       ├── tests/                  # Unit tests
│       ├── pyproject.toml
│       └── README.md
│
├── tests/                          # Integration and E2E tests
│   ├── integration/                # Cross-component tests
│   └── e2e/                        # End-to-end tests
│
├── docs/                           # MkDocs documentation
├── main.py                         # Application entry point
├── pyproject.toml                  # Root project configuration
├── mkdocs.yml                      # Documentation configuration
└── uv.lock                         # Locked dependency versions
```

**Directory Purposes**:

- **`src/`**: Contains all source packages managed as a `uv` workspace. Each subdirectory is an independent package.
- **`src/<package>/src/<package>/`**: The actual source code. This nested "src layout" prevents accidental imports during development.
- **`src/<package>/tests/`**: Unit tests for the specific package, using mocks for external dependencies.
- **`tests/integration/`**: Integration tests that verify how multiple components work together.
- **`tests/e2e/`**: End-to-end tests that verify the entire application workflow.
- **`docs/`**: Documentation source files in Markdown format, processed by MkDocs.

### Configuration Files

#### Root `pyproject.toml`

**Location**: `pyproject.toml` (repository root)

**Purpose**: 
- Defines the overall project metadata and root-level dependencies
- Configures the `uv` workspace to manage multiple packages
- Sets up development tools (ruff, mypy, pytest, coverage) with consistent settings
- Defines optional development dependencies (`dev` extra)

**Key Sections**:

```toml
[tool.uv.workspace]
members = ["src/mail_client_api", "src/gmail_client_impl"]
```
Declares workspace members. `uv sync` installs all members together.

```toml
[project.optional-dependencies]
dev = ["pytest>=8.4.1", "pytest-cov>=6.2.1", "ruff>=0.12.7", ...]
```
Development dependencies installed with `uv sync --extra dev`.

```toml
[tool.pytest.ini_options]
pythonpath = [".", "src"]
testpaths = ["tests", "src/*/tests"]
```
Configures pytest to find tests in both root and component directories.

```toml
[tool.coverage.report]
fail_under = 85  # Minimum coverage threshold
```
Enforces 85% coverage standard.

#### Component `pyproject.toml`

**Location**: `src/<package>/pyproject.toml`

**Purpose**:
- Defines package-specific metadata (name, version, description)
- Declares package-specific runtime dependencies
- Configures workspace dependencies for local development

**Example** (`src/gmail_client_impl/pyproject.toml`):

```toml
[project]
name = "gmail-client-impl"
version = "0.1.0"
dependencies = [
    "mail-client-api",  # Depends on the API package
    "google-api-python-client>=2.177.0",
    "google-auth>=2.40.3",
]

[tool.uv.sources]
mail-client-api = { workspace = true }  # Use local workspace version
```

**Why Two Levels?**
- **Modularity**: Each package can be published independently
- **Clarity**: Runtime dependencies separate from development dependencies
- **Inheritance**: Common settings defined once in root

### Package Structure

#### Role of `__init__.py`

The `__init__.py` file serves multiple purposes:

1. **Package Marker**: Marks a directory as a Python package
2. **Public API Definition**: Controls what's exported when someone imports the package
3. **Initialization Code**: Executes when the package is imported (e.g., dependency injection)

**Example** (`mail_client_api/__init__.py`):

```python
"""Public export surface for mail_client_api."""

from mail_client_api import message
from mail_client_api.client import Client, get_client
from mail_client_api.message import Message, get_message

__all__ = ["Client", "Message", "get_client", "get_message", "message"]
```

This file imports key classes and exports them via `__all__` for clean imports.

**Keeping `__init__.py` Slim**:

A "slim" `__init__.py` means:
- Only public API exports - no business logic
- Minimal imports - only what you're re-exporting
- Fast to import - minimal side effects

**Why Keep It Slim?**
1. Import speed - complex initialization slows down every import
2. Circular import prevention - heavy imports can create dependency issues
3. Clarity - the public API should be immediately obvious
4. Testability - complex initialization makes testing harder

**Exception**: 

The `gmail_client_impl/__init__.py` breaks this rule by calling `register()`:

```python
def register() -> None:
    """Register the Gmail client and message implementations."""
    _register_client()
    _register_message()

# Dependency Injection happens at import time
register()
```

This is acceptable because it's the core purpose of the package.

**Contributor Guideline**: 

Keep `__init__.py` focused on exports and minimal setup  
Use `__all__` to define the public API  
Don't put complex business logic in `__init__.py`  
Exception: Dependency injection registration is acceptable

### Import Guidelines

#### Relative vs. Absolute Imports

**Within a Package**: Use **absolute imports**

```python
# In mail_client_api/client.py
from mail_client_api.message import Message  # ✅ Preferred
```

**Across Packages**: Use **absolute imports**

```python
# In gmail_client_impl/gmail_impl.py
import mail_client_api  # ✅ Correct
from mail_client_api import Message  # ✅ Also correct
```

**Why Prefer Absolute Imports?**
- Clarity - immediately obvious where imports come from
- Refactoring safety - moving files doesn't break imports
- IDE support - better autocomplete and type checking
- Src layout compatibility

**When to Use Relative Imports**:

Relative imports (e.g., `from . import client`) can be used within the same package for tightly coupled modules, but **this project prefers absolute imports** for consistency.

**Contributor Guideline**:

Use absolute imports: `from mail_client_api import Client`  
Don't use star imports: `from mail_client_api import *`  
Avoid relative imports unless within the same package

---

## Testing Strategy

### Testing Philosophy

This project follows principles from **Building Quality In** and **Effective Unit Testing**:

1. **Tests as Documentation**: Tests show how to use the API
2. **Fast Feedback Loops**: Unit tests run in milliseconds
3. **Isolation**: Each test should test one thing
4. **Comprehensive Coverage**: Aim for 85%+ coverage
5. **Test Behavior, Not Implementation**: Verify outcomes, not internal details
6. **Clear Test Names**: Names should describe what's being tested

**Key Principles**:

- **Arrange-Act-Assert (AAA) Pattern**:
  ```python
  def test_client_get_message() -> None:
      # ARRANGE: Set up test data and mocks
      mock_client = Mock(spec=Client)
      mock_client.get_message.return_value = mock_message
      
      # ACT: Execute the code under test
      retrieved_message = mock_client.get_message(message_id="test_id")
      
      # ASSERT: Verify the outcome
      assert retrieved_message.id == "test_id"
  ```

- **Use Mocks for External Dependencies**: Unit tests should not hit real APIs:
  ```python
  def test_authentication(monkeypatch: pytest.MonkeyPatch) -> None:
      monkeypatch.setenv("GMAIL_CLIENT_ID", "test_id")
      # Test uses environment variable without actually authenticating
  ```

### Test Organization

The project uses a three-tier testing structure:

```
Unit Tests          → Fast, isolated, mocked
  ↓
Integration Tests   → Medium speed, real dependencies
  ↓
E2E Tests          → Slow, full system
```

#### Directory Structure

```
src/<package>/tests/        # Unit tests (package-level)
tests/integration/          # Integration tests (cross-component)
tests/e2e/                  # End-to-end tests (full application)
```

**Unit Tests** (`src/*/tests/`)
- Location: Colocated with the package
- Scope: Test individual classes/functions
- Dependencies: Use mocks
- Speed: Very fast (milliseconds)
- Coverage: 85%+ of package code

**Integration Tests** (`tests/integration/`)
- Location: Root-level `tests/integration/`
- Scope: Test how components work together
- Dependencies: May use real services
- Speed: Medium (seconds)

**E2E Tests** (`tests/e2e/`)
- Location: Root-level `tests/e2e/`
- Scope: Test complete application workflow
- Dependencies: Real services, real authentication
- Speed: Slow (minutes)

#### `__init__.py` Convention in Tests

**This project does NOT include `__init__.py` files in test directories.**

**Reasoning**:
1. Tests are not packages - they're not meant to be imported
2. Avoids accidental imports of test code in production
3. Clearer separation between tests and application code
4. pytest best practice - modern pytest doesn't need `__init__.py`
5. The project uses `--import-mode=importlib` which works without `__init__.py`

**Exception**: If you need shared test utilities, create a `conftest.py` file instead.

**Contributor Guideline**:

Create test files like `test_feature.py` directly in test directories  
Use `conftest.py` for shared fixtures  
Don't create `__init__.py` in test directories  
Don't import test code in production

### Test Abstraction Levels

Tests operate at different levels to balance speed, coverage, and confidence:

#### Level 1: Unit Tests (Lowest Abstraction)

Test individual functions with mocks:

```python
def test_message_parsing() -> None:
    """Test that GmailMessage correctly parses email data."""
    raw_data = base64.urlsafe_b64encode(b"From: test@example.com\r\n\r\nBody").decode()
    message = GmailMessage(msg_id="123", raw_data=raw_data)
    
    assert message.from_ == "test@example.com"
    assert message.body == "Body"
```

**Characteristics**: Fast, pure logic, mocked dependencies

#### Level 2: Integration Tests (Medium Abstraction)

Test how components interact:

```python
def test_dependency_injection_works() -> None:
    """Test that importing gmail_client_impl registers the implementation."""
    import mail_client_api
    import gmail_client_impl
    
    client = mail_client_api.get_client(interactive=False)
    assert isinstance(client, gmail_client_impl.GmailClient)
```

**Characteristics**: Test component boundaries, real objects, medium speed

#### Level 3: E2E Tests (Highest Abstraction)

Test the entire application:

```python
def test_main_script_runs() -> None:
    """Test that main.py successfully runs."""
    result = subprocess.run(["python", "main.py"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Demo complete" in result.stdout
```

**Characteristics**: Test user workflows, real services, slow

**Choosing the Right Level**:
- **Unit Tests**: Business logic, parsing, algorithms, edge cases
- **Integration Tests**: Dependency injection, API authentication, cross-component flow
- **E2E Tests**: Critical user workflows, main application entry points

**Test Pyramid**:

```
       /\
      /E2E\         Few, slow, high confidence
     /------\
    /  INT   \      Some, medium speed
   /----------\
  /    UNIT    \    Many, fast, focused
 /--------------\
```

Most tests should be fast unit tests.

### Code Coverage

#### Coverage Tool

The project uses **`pytest-cov`**, a pytest plugin that integrates `coverage.py`.

**Installation**: Included in dev dependencies:
```toml
[project.optional-dependencies]
dev = ["pytest-cov>=6.2.1", ...]
```

#### Coverage Thresholds

**Minimum Coverage**: **85%**

Configured in root `pyproject.toml`:

```toml
[tool.coverage.report]
fail_under = 85
```

**What's Excluded**:

```toml
[tool.coverage.run]
omit = ["*/tests/*", "*/__main__.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
```

#### Running Tests with Coverage

**Run all tests with coverage**:
```bash
uv run pytest --cov=src --cov-report=term-missing
```

**Run unit tests only**:
```bash
uv run pytest src/ --cov=src
```

**Run specific test types**:
```bash
# Unit tests
uv run pytest src/ -m unit --cov=src

# Integration tests
uv run pytest -m integration --cov=src

# Exclude tests requiring local credentials
uv run pytest -m "not local_credentials" --cov=src
```

**Generate HTML coverage report**:
```bash
uv run pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

**Coverage Output Explained**:

```
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/mail_client_api/client.py        10      0   100%
src/gmail_client_impl/gmail.py      156     15    90%   45-52, 89-95
---------------------------------------------------------------
TOTAL                              1234     89    93%
```

- **Stmts**: Total executable statements
- **Miss**: Statements not executed by tests
- **Cover**: Percentage coverage
- **Missing**: Line numbers not covered

**Coverage Best Practices**:

Focus on testing meaningful behavior  
Use coverage to find untested code paths  
Don't write meaningless tests just for coverage  
Coverage measures execution, not correctness

---

## Development Tools

### Workspace Management

This project uses **`uv`** (Universal Virtualenv), a fast Python package manager.

#### What is a `uv` Workspace?

A **workspace** is a collection of related Python packages managed together:
- `mail_client_api` (interface)
- `gmail_client_impl` (implementation)
- Root project (dev tools, integration tests)

**Advantages**:
- Unified dependency management (one `uv.lock` file)
- Local development (packages reference each other via `{ workspace = true }`)
- Atomic installs (one command installs everything)

#### Essential `uv` Commands

**Initial Setup**:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv and install everything
uv sync --all-packages --extra dev
```

**Activate Virtual Environment**:

```bash
# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

**Run Commands Without Activating**:

```bash
uv run pytest
uv run python main.py
uv run ruff check .
```

**Add Dependencies**:

```bash
# Add runtime dependency to specific package
uv add requests --package gmail-client-impl

# Add dev dependency to root
uv add --extra dev black
```

**Update Dependencies**:

```bash
# Update all packages
uv sync --upgrade

# Update specific package
uv sync --upgrade-package requests
```

**Other Commands**:

```bash
# View dependency tree
uv tree

# Remove stale dependencies
uv sync --clean
```

#### Root vs Component `pyproject.toml`

**Root `pyproject.toml`** (`/pyproject.toml`):
- **Purpose**: Workspace configuration and development tools
- **Responsibilities**:
  - Declares workspace members
  - Installs development tools (pytest, ruff, mypy)
  - Configures tools
  - Defines root project metadata

**Component `pyproject.toml`** (`/src/<package>/pyproject.toml`):
- **Purpose**: Package-specific configuration
- **Responsibilities**:
  - Declares package metadata
  - Specifies runtime dependencies
  - Configures workspace sources

**Example Workflow**:

1. `uv sync --all-packages --extra dev` - Installs everything
2. `uv add google-auth --package gmail-client-impl` - Adds package dependency
3. `uv add --extra dev black` - Adds dev tool

**Why Separate Files?**
- Modularity - packages can be published independently
- Clarity - runtime vs development dependencies
- Reusability - packages can be used in other projects

### Static Analysis and Code Formatting

#### Tools Used

1. **Ruff**: Fast linter and formatter (replaces flake8, isort, black)
2. **MyPy**: Static type checker

#### Why These Tools Are Important

1. **Consistency**: Automated formatting ensures uniform code style
2. **Quality**: Linting catches bugs, anti-patterns, and security issues early
3. **Type Safety**: MyPy catches type errors before runtime
4. **Maintainability**: Consistent code is easier to read and maintain
5. **Collaboration**: Reduces style debates in code reviews

#### Configuration

**Ruff** (`pyproject.toml`):

```toml
[tool.ruff]
line-length = 130
target-version = "py311"

[tool.ruff.lint]
select = ["ALL"]  # Enable all rules
```

**MyPy** (`pyproject.toml`):

```toml
[tool.mypy]
strict = true
```

#### Running Static Analysis

**Ruff Linting**:

```bash
# Check for issues
uv run ruff check .

# Automatically fix issues
uv run ruff check . --fix
```

**Ruff Formatting**:

```bash
# Check formatting
uv run ruff format --check .

# Apply formatting
uv run ruff format .
```

**MyPy Type Checking**:

```bash
# Type check all code
uv run mypy src tests

# Type check specific package
uv run mypy src/gmail_client_impl/
```

**Run All Quality Checks**:

```bash
uv run ruff check . && \
uv run ruff format --check . && \
uv run mypy src tests
```

#### Integration with `uv`

These tools are **separate from `uv`** but installed through it:

```bash
# Tools are installed as dev dependencies
uv sync --extra dev

# Run tools using uv run
uv run ruff check .
uv run mypy src
```

**Why Not Integrated?**
- `uv` focuses on package management
- Ruff and MyPy are specialized tools
- Separation allows choosing different tools
- Tools can be updated independently

**Contributor Guideline**:

Run `ruff format .` before committing  
Fix errors from `ruff check .`  
Ensure `mypy src tests` passes  
Don't disable rules without documenting why

### Documentation Generation

#### Tool: MkDocs with Material Theme

The project uses **MkDocs** for documentation with the **Material** theme.

**Installation**:

```bash
uv sync --extra dev
```

This installs:
- `mkdocs`: Documentation generator
- `mkdocs-material`: Material Design theme
- `mkdocstrings-python`: Auto-generates API docs from docstrings

#### Configuration

Configured in `mkdocs.yml`:

```yaml
site_name: Mail Client Project
theme:
  name: material
  features:
    - navigation.tabs
    - content.code.copy

plugins:
  - mkdocstrings:
      handlers:
        python:
          options:
            search_paths: 
              - src/mail_client_api/src
              - src/gmail_client_impl/src
```

**Key Features**:
- Markdown-based documentation
- Automatic API docs from docstrings
- Live reloading dev server
- Dark mode support
- Code syntax highlighting

#### Using MkDocs

**Start development server**:

```bash
uv run mkdocs serve
```

Opens at `http://127.0.0.1:8000` with auto-reload.

**Build static HTML**:

```bash
uv run mkdocs build
```

Generates files in `site/` directory.

**Create new pages**:

1. Add Markdown file to `docs/`:
   ```bash
   touch docs/new-feature.md
   ```

2. Update `mkdocs.yml`:
   ```yaml
   nav:
     - 'New Feature': 'new-feature.md'
   ```

3. Write content with code examples

**Document API from docstrings**:

```markdown
# Client API

::: mail_client_api.Client
    options:
      show_source: false
```

**Contributor Guideline**:

Write clear documentation in Markdown  
Include copy-pastable code examples  
Use docstrings for API documentation  
Test locally with `mkdocs serve`  
Don't commit the `site/` directory (auto-generated)

### Continuous Integration (CI)

The project uses **CircleCI** for continuous integration.

#### CI Pipeline Jobs

1. **Build**
   - Sets up Python 3.11 environment
   - Installs `uv`
   - Runs `uv sync --all-packages --extra dev`

2. **Lint**
   - Runs `uv run ruff check .`
   - Runs `uv run ruff format --check .`
   - Runs `uv run mypy src tests`

3. **Unit Tests**
   - Runs `uv run pytest src/`
   - Requires 85% code coverage
   - Generates coverage reports

4. **CircleCI Tests**
   - Runs `uv run pytest -m circleci`
   - Tests that work without credentials
   - No local files required

5. **Integration Tests** (main/develop only)
   - Runs `uv run pytest -m integration`
   - Uses real Gmail API credentials
   - Environment variables from CircleCI context
   - Only on protected branches

6. **Report Summary**
   - Aggregates results and metrics
   - Uploads artifacts
   - Provides build status

#### What Triggers CI

- **Push to any branch**: build, lint, unit tests, CircleCI tests
- **Pull request**: same as push, plus integration tests if targeting main/develop
- **Scheduled builds**: periodic health checks

**Branch-Specific Behavior**:

| Branch | Build | Lint | Unit | CircleCI | Integration |
|--------|-------|------|------|----------|-------------|
| Feature | ✅ | ✅ | ✅ | ✅ | ❌ |
| main/develop | ✅ | ✅ | ✅ | ✅ | ✅ |

**Why Separate Test Jobs?**
- Speed: Unit tests fast; integration slow
- Security: Integration tests with credentials only on trusted branches
- Reliability: CircleCI tests pass without credentials

**Environment Variables Required**:

For integration tests (CircleCI context `gmail-client`):
- `GMAIL_CLIENT_ID`
- `GMAIL_CLIENT_SECRET`
- `GMAIL_REFRESH_TOKEN`
- `GMAIL_TOKEN_URI` (optional)

**Contributor Workflow**:

1. Develop on feature branch
2. Run tests locally: `uv run pytest -m "not local_credentials"`
3. Run quality checks
4. Push to trigger CI
5. Check CI status
6. Merge to main/develop (integration tests run automatically)

**Debugging CI Failures**:

- **Lint failures**: Run `uv run ruff check . --fix` locally
- **Type errors**: Run `uv run mypy src tests` locally
- **Test failures**: Run `uv run pytest -v` locally
- **Coverage failures**: Run `uv run pytest --cov=src --cov-report=html`

**Contributor Guideline**:

Run all checks locally before pushing  
Add `@pytest.mark.circleci` for CI-compatible tests  
Add `@pytest.mark.local_credentials` for tests requiring local auth  
Don't commit credentials  
Don't skip CI checks

---

## Getting Started

Ready to contribute? Here's the setup:

```bash
# 1. Clone the repository
git clone <repository-url>
cd oss-taapp

# 2. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Set up environment
uv sync --all-packages --extra dev

# 4. Set up Gmail credentials (see README.md)
# Place credentials.json in root

# 5. Run tests
uv run pytest src/ tests/ -m "not local_credentials" -v

# 6. Start documentation server
uv run mkdocs serve

# 7. Create feature branch
git checkout -b feature/my-contribution
```

**Before submitting a pull request**:

```bash
# Format code
uv run ruff format .

# Check linting
uv run ruff check . --fix

# Type check
uv run mypy src tests

# Run tests
uv run pytest --cov=src --cov-report=term-missing

# Ensure coverage ≥ 85%
```

---

## Questions?

- Check `docs/` for detailed documentation
- Look at existing tests for examples
- Run `uv run mkdocs serve` to browse docs
- Open an issue for clarification

Thanks for contributing!
