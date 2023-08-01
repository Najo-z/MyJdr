#!/usr/bin/env python3

from storage import StorageInterface
from pathlib import Path

storage = StorageInterface.FileSystemStorage(
    Path('./tables'), load_tables=True)

storage.print_tables()
