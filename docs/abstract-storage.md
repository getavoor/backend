# Abstract Storage

Abstract Storage is a module that provides a unified interface for file storage operations. It allows the application to work with different storage backends (local folders, cloud storage) without changing the code that uses it.

## Why Use an Abstraction?

When building an application, you might want to:
- Store files locally during development (fast, no cloud costs)
- Store files in the cloud in production (scalable, accessible from anywhere)

Without an abstraction, you'd need different code for each environment:

```python
# Without abstraction - messy!
if environment == "development":
    shutil.copy(file, "/local/folder/" + filename)
    url = "http://localhost/files/" + filename
elif environment == "production":
    bucket.upload(file, filename)
    url = f"https://storage.cloud.com/{filename}"
```

With Abstract Storage, the same code works everywhere:

```python
# With abstraction - clean!
storage.upload(file, filename)
url = storage.get_url(filename)
```

## Available Implementations

### FolderStorage

Stores files in a local folder on the server's filesystem. Best for development and testing.

**Location:** `abstract_storage/folder.py`

```python
from abstract_storage.folder import FolderStorage

# Creates a folder called "my_files" if it doesn't exist
storage = FolderStorage("my_files")
```

### GoogleCloudStorage

Stores files in a Google Cloud Storage bucket. Best for production deployments.

**Location:** `abstract_storage/google.py`

```python
from abstract_storage.google import GoogleCloudStorage

# Uses the default App Engine bucket (project-id.appspot.com)
storage = GoogleCloudStorage()

# Or specify a custom bucket
storage = GoogleCloudStorage("my-custom-bucket")
```

**Requirements:**
- `google-cloud-storage` package installed
- Google Cloud credentials configured
- The `GOOGLE_CLOUD_PROJECT` environment variable set (automatic on App Engine)

## API Reference

All storage implementations share the same interface defined in the `AbstractStorage` base class.

### `upload(local_path, remote_path, overwrite=False)`

Uploads a file from the local filesystem to storage.

**Parameters:**
- `local_path` (str): Path to the file on the local disk
- `remote_path` (str): Destination path in storage
- `overwrite` (bool): If `True`, overwrites existing files. Default is `False`

**Example:**
```python
# Upload a user's profile picture
storage.upload("/tmp/photo.jpg", "profile/user_123/avatar.jpg")
```

### `upload_file_object(file, remote_path, overwrite=False)`

Uploads a file-like object (e.g., from a web request) directly to storage.

**Parameters:**
- `file`: A file-like object with a `read()` method
- `remote_path` (str): Destination path in storage
- `overwrite` (bool): If `True`, overwrites existing files. Default is `False`

**Example:**
```python
from flask import request

# Upload a file from a form submission
uploaded_file = request.files['picture']
storage.upload_file_object(uploaded_file, "uploads/document.pdf")
```

### `download(path) -> bytes`

Downloads a file from storage and returns its contents as bytes.

**Parameters:**
- `path` (str): Path to the file in storage

**Returns:** File contents as `bytes`

**Example:**
```python
# Download and process a file
content = storage.download("data/config.json")
config = json.loads(content.decode('utf-8'))
```

### `get_url(path) -> str`

Gets a web-accessible URL for a file in storage.

**Parameters:**
- `path` (str): Path to the file in storage

**Returns:** Public URL as a string

**Example:**
```python
# Get the URL to display in an <img> tag
url = storage.get_url("profile/user_123/avatar.jpg")
# FolderStorage: "profile/user_123/avatar.jpg" (relative path)
# GoogleCloudStorage: "https://storage.googleapis.com/bucket/static/profile/user_123/avatar.jpg"
```

### `delete(path)`

Deletes a file from storage.

**Parameters:**
- `path` (str): Path to the file in storage

**Example:**
```python
# Remove an old profile picture
storage.delete("profile/user_123/old_avatar.jpg")
```

### `web_to_absolute(url) -> str`

Converts a web URL back to a storage path. Useful when you have a URL stored in the database and need to perform operations on the file.

**Parameters:**
- `url` (str): The web-accessible URL

**Returns:** The storage path

**Example:**
```python
# User's photo URL is stored in the database
photo_url = "https://storage.googleapis.com/mybucket/static/profile/123/pic.jpg"

# Convert it back to a path to delete the file
path = storage.web_to_absolute(photo_url)
storage.delete(path)
```

## How Avoor Uses Abstract Storage

In Avoor, the storage backend is configured via the `AVR_FS` environment variable:

| Value | Storage Type |
|-------|--------------|
| `folder` | Local folder (`instance/storage/`) |
| `google_bucket` | Google Cloud Storage |

The storage instance is created in `server/__init__.py` and imported where needed:

```python
# In server/__init__.py
from server.env_vars import FILE_STORAGE

if FILE_STORAGE == "folder":
    from abstract_storage.folder import FolderStorage
    storage = FolderStorage("instance/storage")
elif FILE_STORAGE == "google_bucket":
    from abstract_storage.google import GoogleCloudStorage
    storage = GoogleCloudStorage()
```

```python
# In other files, import and use it
from server import storage

# Upload a profile picture
storage.upload_file_object(image_file, f"profile/{user_id}/avatar.jpg")
url = storage.get_url(f"profile/{user_id}/avatar.jpg")
```

## Creating a Custom Storage Backend

You can create your own storage backend by extending `AbstractStorage`:

```python
from abstract_storage import AbstractStorage
import boto3  # Example: AWS S3

class S3Storage(AbstractStorage):
    def __init__(self, bucket_name):
        self.s3 = boto3.client('s3')
        self.bucket = bucket_name

    def upload(self, local_path, remote_path, overwrite=False):
        self.s3.upload_file(local_path, self.bucket, remote_path)

    def upload_file_object(self, file, remote_path, overwrite=False):
        self.s3.upload_fileobj(file, self.bucket, remote_path)

    def download(self, path):
        response = self.s3.get_object(Bucket=self.bucket, Key=path)
        return response['Body'].read()

    def get_url(self, path):
        return f"https://{self.bucket}.s3.amazonaws.com/{path}"

    def delete(self, path):
        self.s3.delete_object(Bucket=self.bucket, Key=path)
```

## Further Reading

- [Google Cloud Storage Python Client](https://cloud.google.com/python/docs/reference/storage/latest)
- [Python pathlib module](https://docs.python.org/3/library/pathlib.html) (used by FolderStorage)
