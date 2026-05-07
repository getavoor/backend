"""
Abstract Storage
Google Cloud storage
(c) 2023 githubcatw
"""

from . import AbstractStorage

# used for connecting to Google Cloud
from google.cloud import storage

# used for accessing the system environment variables
import os

class GoogleCloudStorage(AbstractStorage):
    """
    Abstract storage implementation using Google Cloud.
    """

    def __init__(self, bucket_name: str = None) -> None:
        super().__init__()
        # Update the bucket URL if it wasn't changed.
        if bucket_name == None:
            bucket_name = os.environ.get("GOOGLE_CLOUD_PROJECT","") + ".appspot.com"
        self.bucket_name = bucket_name
        # Connect to the bucket.
        storage_client = storage.Client()
        self.bucket = storage_client.bucket(bucket_name)

    def upload(self, local_path: str, remote_path: str, overwrite: bool = False):
        """
        Upload a file.

        Argument:
        - local_path - the path to the file on the local disk.
        - remote_path - the path the file needs to be uploaded to.
        - overwrite - should the file be overwritten if it already exists? Optional, defaults to False.
        """
        print("Uploading file " + local_path)
        # Create a new blob.
        # "static/" is added to the path because Google Cloud can be configured to host that folder publicly,
        # which removes the need to download a file used by an experience just to send it to the app.
        blob = self.bucket.blob("static/"+remote_path)

        if overwrite:
            blob.upload_from_filename(local_path)
        else:
            # Set a generation-match precondition to avoid potential data corruptions.
            generation_match_precondition = 0
            # Upload the file.
            blob.upload_from_filename(local_path, if_generation_match=generation_match_precondition)

        print(
            f"File {local_path} uploaded to {remote_path}."
        )

    def upload_file_object(self, file, remote_path: str, overwrite: bool = False):
        """
        Upload a file.

        Argument:
        - file - a file-like object.
        - remote_path - the path the file needs to be uploaded to.
        - overwrite - should the file be overwritten if it already exists? Optional, defaults to False.
        """
        print(f"Uploading file to {remote_path}")
        # Create a new blob.
        # "static/" is added to the path because Google Cloud can be configured to host that folder publicly,
        # which removes the need to download a file used by an experience just to send it to the app.
        blob = self.bucket.blob("static/"+remote_path)

        if overwrite:
            blob.upload_from_file(file, rewind=True)
        else:
            # Set a generation-match precondition to avoid potential data corruptions.
            generation_match_precondition = 0
            # Upload the file.
            blob.upload_from_file(file, if_generation_match=generation_match_precondition, rewind=True)

        print(
            f"File uploaded to {remote_path}."
        )

    def download(self, path: str) -> bytes:
        """
        Download a file.

        Argument: path - the path to the file on model storage.
        """
        print("Downloading file " + path)
        return []

    def get_url(self, path: str) -> str:
        """
        Gets the full, web-accessible URL of a given absolute path.
        """
        return f"https://storage.googleapis.com/{self.bucket_name}/static/{path}"

    def delete(self, path: str):
        """
        Delete a file.

        Argument: path - the path to the file on remote storage.
        """
        blob = self.bucket.blob("static/" + path)
        generation_match_precondition = None

        # Set a generation-match precondition to avoid potential race conditions
        # and data corruptions. The request to delete is aborted if the object's
        # generation number does not match your precondition.
        blob.reload()  # Fetch blob metadata to use in generation_match_precondition.
        generation_match_precondition = blob.generation

        blob.delete(if_generation_match=generation_match_precondition)

    def web_to_absolute(self, url: str) -> str:
        """
        Converts a web URL to an absolute path.

        Argument: url - full, web-accessible URL of a given absolute path on remote storage.
        """
        path_start = f"https://storage.googleapis.com/{self.bucket_name}/static/"
        if not url.startswith(path_start):
            raise ValueError("Unrecognized URL")
        return url.replace(path_start, "")