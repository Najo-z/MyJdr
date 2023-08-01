#!/usr/bin/env python3
from pathlib import Path
from storage import StorageInterface
import pytest
import yaml
import shutil
import sys
sys.path.append('./')


table_dir = Path('./tests/tables')


def test_FileSystemStorage():
    if table_dir.exists():
        shutil.rmtree(table_dir.absolute())
    storage = StorageInterface.FileSystemStorage(table_dir)
    assert table_dir.exists()

    cols = ('a', 'b')
    storage.create_table('test', cols)
    table_path = table_dir / 'test.table'
    assert table_path.exists()

    expected_table = {
        'filename': table_path.name,
        'cols': [v for v in cols],
        'items': {},
    }
    with open(table_path, 'r') as f:
        assert yaml.safe_load(f) == expected_table

    with pytest.raises(ValueError):
        storage.create_table('test', cols)
