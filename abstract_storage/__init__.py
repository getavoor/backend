"""
Abstract Storage
Base class
(c) 2023 githubcatw
(c) 2024 Cat Aspect
"""

import tempfile

class AbstractStorage():
    """
    Abstract storage provides a way for a Python app to upload and download
    files to some kind of storage - be it a local folder, a file server or
    cloud storage - using standardized APIs. The idea is to make it so a
    storage implementation can be swapped for another with minimal changes
    required.
    """

    def upload(self, local_path: str, remote_path: str, overwrite: bool = False):
        """
        Upload a file.

        Argument:
        - local_path - the path to the file on the local disk.
        - remote_path - the path the file needs to be uploaded to.
        - overwrite - should the file be overwritten if it already exists? Optional, defaults to False.
        """
        print(f"Uploading file {local_path} to {remote_path}")

    def upload_file_object(self, file, remote_path: str, overwrite: bool = False):
        """
        Upload a file.

        Argument:
        - file - a file-like object.
        - remote_path - the path the file needs to be uploaded to.
        - overwrite - should the file be overwritten if it already exists? Optional, defaults to False.
        """
        print(f"Stub: uploading file to {remote_path}")

    def download(self, path: str) -> bytes:
        """
        Download a file.

        Argument: path - the path to the file on remote storage.
        """
        print("Downloading file " + path)
        #return []

    def get_url(self, path: str) -> str:
        """
        Gets the full, web-accessible URL of a given absolute path on remote storage.
        """
        return path

    def delete(self, path: str):
        """
        Delete a file.

        Argument: path - the path to the file on remote storage.
        """
        print("Stub: deleting file " + path)
        #return []

    def web_to_absolute(self, url: str) -> str:
        """
        Converts a web URL to an absolute path.

        Argument: url - full, web-accessible URL of a given absolute path on remote storage.
        """
        return url
