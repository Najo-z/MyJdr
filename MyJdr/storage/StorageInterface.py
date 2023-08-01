#!/usr/bin/env python3

from abc import ABC, abstractmethod
from pathlib import Path
from logging import getLogger
import yaml
import os

LOGGER = getLogger(__name__)


class StorageInterface(ABC):

    @abstractmethod
    def create_table(self, name: str, cols: tuple[str]):
        pass


class FileSystemStorage(StorageInterface):
    def __init__(self, dir: Path | str, load_tables: bool = False) -> None:
        super().__init__()
        self.dir = Path(dir) if isinstance(dir, str) else dir
        if not self.dir.exists():
            self.dir.mkdir()
        self.tables = {}
        if load_tables:
            self.load_tables()

    def create_table(self, name: str, cols: tuple[str]):
        if name in self.tables:
            LOGGER.warning(f'create_table():\tTable {name} already exists.')
            return
        filename = self.dir / f'{name}.table'
        if filename.exists():
            LOGGER.warning(
                f'create_table():\tTable {filename} already exists.')
            return
        filename.touch()
        table = {
            'name': name,
            'cols': [v for v in cols],
            'items': [],
        }
        self.tables[name] = table
        with open(filename, 'w') as f:
            yaml.safe_dump(table, f, sort_keys=False)

    def delete_table(self, name: str):
        if name not in self.tables:
            LOGGER.warning(f'delete_table():\tTable {name} doesn\'t exists.')
            return
        del self.tables[name]
        filename = self.dir / f'{name}.table'
        filename.unlink(missing_ok=True)

    def load_tables(self):
        for file in os.listdir(self.dir):
            if file.endswith('.table'):
                self.load_table(file)

    def load_table(self, filename: Path | str):
        filename = self.dir / filename
        with open(filename, 'r') as file:
            table = yaml.safe_load(file)
        self.tables[table['name']] = table

    def save_tables(self):
        for table_name in self.tables:
            self.save_table(table_name)

    def save_table(self, table_name: str):
        if table_name not in self.tables:
            LOGGER.warning(
                f'save_table():\tTable {table_name} doesn\'t exists.')
            return
        filename = self.dir / f'{table_name}.table'
        with open(filename, 'w') as file:
            yaml.safe_dump(self.tables[table_name], file, sort_keys=False)

    def print_tables(self):
        for table in self.tables:
            print(f'{table}: {self.tables[table]}')

    def print_tables(self):
        for table in self.tables:
            print(f'{table}: {self.tables[table]}')

    def add_row(self, table_name: str, values: dict):
        if table_name not in self.tables:
            LOGGER.warning(f'add_row():\tTable {table_name} doesn\'t exists.')
            return
        if list(values.keys()) != self.tables[table_name]['cols']:
            LOGGER.warning(
                f'add_row():\tvalues keys {values.keys()} not correct for columns {self.tables[table_name]["cols"]}.')
            return
        self.tables[table_name]['items'].append(values)
        self.save_table(table_name)
