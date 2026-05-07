# Long-running tasks (LRT)

> **Note:** The Long-running tasks system was primarily used in the project that this codebase originated from. The current Avoor implementation has minimal use of LRTs. This documentation explains the system for reference and potential future use.

Long-running tasks (LRT) is a system for executing asynchronous operations that take too long to complete within a normal HTTP request/response cycle.

## The Problem LRT Solves

In a typical web request:
1. Client sends a request
2. Server processes it
3. Server sends a response

This works fine for quick operations (milliseconds to a few seconds). But what about operations that take longer?

- Processing large images
- Sending batch emails
- Calling slow external APIs
- Running AI inference
- Generating reports

If these run in the request handler, the client waits (and might time out). LRT solves this by running these operations in a background thread.

## How It Works

Avoor creates a separate [asyncio event loop](https://docs.python.org/3/library/asyncio-eventloop.html) in a background thread when the application starts:

```
Main Thread                    Background Thread
┌──────────────────┐          ┌──────────────────┐
│  Flask App       │          │  LRT Event Loop  │
│  (HTTP requests) │          │  (Async tasks)   │
│                  │          │                  │
│  - Receives      │  ─────>  │  - Runs slow     │
│    requests      │  submit  │    operations    │
│  - Returns       │   task   │  - Processes     │
│    immediately   │          │    in background │
└──────────────────┘          └──────────────────┘
```

## Architecture

### Event Loop Setup

The LRT event loop is created in `server/__init__.py`:

```python
import asyncio
from threading import Thread

def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    print("Starting event loop...")
    loop.run_forever()

def lrt_exception_handler(loop, context):
    """Handles exceptions in background tasks"""
    print('===== Exception in long running task =====')
    print(context)
    traceback.print_exception(context["exception"])
    print("===== End exception =====")

# Create a new event loop for background tasks
lrtEventLoop = asyncio.new_event_loop()
lrtEventLoop.set_exception_handler(lrt_exception_handler)

# Run it in a separate daemon thread
t = Thread(target=start_background_loop, args=(lrtEventLoop,), daemon=True)
t.start()
```

Key points:
- **Daemon thread**: Automatically stops when the main program exits
- **Custom exception handler**: Logs errors instead of crashing silently
- **Separate event loop**: Doesn't block the main Flask thread

### Task Module

Long running task functions are defined in `server/longRunningTasks.py`:

```python
from server import ai, db, storage
from server.models import User

flask_app = None

def set_flask_app(app):
    """Called during app initialization to provide Flask context"""
    global flask_app
    flask_app = app

# Define your async tasks here
async def process_something(user_id, data):
    # Access Flask app context if needed
    with flask_app.app_context():
        user = User.query.get(user_id)
        # ... do slow processing ...
```

## Usage Examples

### Submitting a Task

To run a function in the background:

```python
import asyncio
from server import lrtEventLoop

# Define an async function
async def send_welcome_email(user_email, user_name):
    # Simulate slow email sending
    await asyncio.sleep(2)
    print(f"Email sent to {user_email}")

# Submit it to the background loop
asyncio.run_coroutine_threadsafe(
    send_welcome_email("user@example.com", "John"),
    lrtEventLoop
)
# Returns immediately - task runs in background
```

### With Flask Context

If your task needs database access, wrap it in the app context:

```python
from server import lrtEventLoop
from server.longRunningTasks import flask_app
from server.models import User, db

async def update_user_stats(user_id):
    # Need Flask context for database operations
    with flask_app.app_context():
        user = User.query.get(user_id)
        if user:
            # ... calculate stats ...
            user.some_stat = calculated_value
            db.session.commit()

# Submit the task
asyncio.run_coroutine_threadsafe(
    update_user_stats(123),
    lrtEventLoop
)
```

### Getting Results (If Needed)

If you need the result of a background task:

```python
import asyncio
from server import lrtEventLoop

async def expensive_calculation(data):
    await asyncio.sleep(5)  # Simulate slow work
    return data * 2

# Submit and get a Future object
future = asyncio.run_coroutine_threadsafe(
    expensive_calculation(21),
    lrtEventLoop
)

# Option 1: Block and wait for result (defeats the purpose!)
result = future.result(timeout=10)  # 42

# Option 2: Check if done later
if future.done():
    result = future.result()
```

### Fire and Forget Pattern

Most LRT use cases are "fire and forget" - you don't need the result:

```python
from server import lrtEventLoop

@app.route('/api/register', methods=['POST'])
def register():
    # Create user...
    user = create_user(request.json)

    # Send welcome email in background (don't wait)
    asyncio.run_coroutine_threadsafe(
        send_welcome_email(user.email),
        lrtEventLoop
    )

    # Return immediately
    return jsonify({"msg": "Registration successful"})
```

## Practical Use Cases

While the Gemifood-specific tasks have been removed, here are scenarios where LRT is useful:

### Sending Emails

```python
async def send_confirmation_email(user_email, token):
    """Send email without blocking the request"""
    # Email sending can be slow (network latency)
    await send_email(
        to=user_email,
        subject="Confirm your account",
        body=f"Click here: /confirm?token={token}"
    )
```

### Processing Uploaded Images

```python
async def process_profile_picture(user_id, image_path):
    """Generate thumbnails in the background"""
    with flask_app.app_context():
        # Create multiple sizes
        for size in [(100, 100), (200, 200), (500, 500)]:
            thumbnail = create_thumbnail(image_path, size)
            storage.upload(thumbnail, f"profile/{user_id}/thumb_{size[0]}.jpg")
```

### Batch Operations

```python
async def send_daily_reminders():
    """Send reminders to all users with tasks due today"""
    with flask_app.app_context():
        users = User.query.filter(User.has_tasks_due_today).all()
        for user in users:
            await send_reminder_email(user)
            await asyncio.sleep(0.1)  # Rate limiting
```

### Cleanup Tasks

```python
async def cleanup_old_files():
    """Remove temporary files older than 24 hours"""
    with flask_app.app_context():
        old_files = TempFile.query.filter(
            TempFile.created_at < datetime.now() - timedelta(hours=24)
        ).all()
        for file in old_files:
            storage.delete(file.path)
            db.session.delete(file)
        db.session.commit()
```

## Python Concepts Explained

### asyncio Event Loop

An event loop runs async functions. Think of it as a manager that:
- Keeps track of tasks that are waiting (for I/O, timers, etc.)
- Runs tasks when they're ready
- Switches between tasks efficiently

```python
import asyncio

async def say_hello():
    print("Hello")
    await asyncio.sleep(1)  # Yield control, come back in 1 second
    print("World")

# Run in the event loop
asyncio.run(say_hello())
```

### Daemon Threads

A daemon thread is a background thread that:
- Runs independently of the main program
- Automatically stops when the main program exits
- Doesn't prevent the program from closing

```python
from threading import Thread

t = Thread(target=my_function, daemon=True)
t.start()
# Program can exit even if thread is still running
```

### run_coroutine_threadsafe

This function safely submits an async function to an event loop running in a different thread:

```python
# From the main thread, submit to the background loop
future = asyncio.run_coroutine_threadsafe(
    my_async_function(),  # The coroutine to run
    lrtEventLoop          # The event loop to run it in
)
```

## Further Reading

- [Python asyncio documentation](https://docs.python.org/3/library/asyncio.html)
- [Real Python: Async IO in Python](https://realpython.com/async-io-python/)
- [Threading in Python](https://docs.python.org/3/library/threading.html)
