"""
Abstract Storage
Folder based storage
(c) 2023 githubcatw
"""

from . import AbstractStorage

# used for creating a folder
from pathlib import Path
import os

# used for copying
import shutil

class FolderStorage(AbstractStorage):
    """
    Abstract storage implementation using a local folder.
    """

    def __init__(self, folder: str = "abstract_storage") -> None:
        super().__init__()
        # Create a folder if it doesn't exist.
        Path(folder).mkdir(parents=True, exist_ok=True)
        # Save the folder's path.
        self.folder = folder

    def upload(self, local_path: str, remote_path: str):
        """
        Upload a file.

        Argument: 
        - local_path - the path to the file on the local disk.
        - remote_path - the path the file needs to be uploaded to.
        """
        full_remote_path = os.path.join(self.folder, remote_path)
        shutil.copy(local_path, full_remote_path)

    def download(self, path: str) -> bytes:
        """
        Download a file.

        Argument: path - the path to the file on remote storage.
        """
        print("Reading file " + path)
        bts = []
        full_remote_path = os.path.join(self.folder, path)
        with open(full_remote_path, "rb") as f:
            bts = f.read()
        return bts
