# storage.py
#
# MIT License
#
# Copyright (c) 2020 Andrey Maksimov <meamka@ya.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import os
import sqlite3

from gi.repository import GLib, Gio

from norka.define import APP_TITLE
from norka.models.document import Document


class Storage(object):
    def __init__(self):
        self.base_path = os.path.join(GLib.get_user_config_dir(), APP_TITLE)
        self.file_path = os.path.join(self.base_path, 'storage.db')
        self.conn = None

    def init(self):
        if not os.path.exists(self.base_path):
            os.mkdir(self.base_path)
            print(f'Storage folder created at {self.base_path}')

        print(f'Storage located at {self.file_path}')

        self.conn = sqlite3.connect(self.file_path)

        self.conn.execute("""
                CREATE TABLE IF NOT EXISTS `documents` (
                    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                    `title` TEXT NOT NULL,
                    `content` TEXT,
                    `archived` INTEGER NOT NULL DEFAULT 0 
                )
            """)

    def count(self, with_archived: bool = False) -> int:
        query = 'SELECT COUNT (1) AS count FROM documents'
        if not with_archived:
            query += " WHERE archived=0"
        cursor = self.conn.cursor().execute(query)
        row = cursor.fetchone()
        return row[0]

    def add(self, document: Document) -> int:
        cursor = self.conn.cursor().execute("INSERT INTO documents(title, content, archived) VALUES (?, ?, ?)",
                                            (document.title, document.content, document.archived,), )
        self.conn.commit()
        return cursor.lastrowid

    def all(self, with_archived: bool = False) -> list:
        query = "SELECT * FROM documents"
        if not with_archived:
            query += " WHERE archived=0"

        print(f'> ALL QUERY: {query}')

        cursor = self.conn.cursor().execute(query)
        rows = cursor.fetchall()

        docs = []
        for row in rows:
            docs.append(Document.new_with_row(row))

        return docs

    def get(self, doc_id: int) -> Document:
        query = "SELECT * FROM documents WHERE id=?"
        cursor = self.conn.cursor().execute(query, (doc_id,))
        row = cursor.fetchone()

        return Document.new_with_row(row)

    def save(self, document: Document) -> bool:
        query = "UPDATE documents SET title=?, content=?, archived=? WHERE id=?"

        try:
            self.conn.execute(query, (document.title, document.content, document.archived,))
            self.conn.commit()
        except Exception as e:
            print(e)
            return False

        return True

    def update(self, doc_id: int, data: dict) -> bool:
        fields = {field: value for field, value in data.items()}

        query = f"UPDATE documents SET {','.join(f'{key}=?' for key in fields.keys())} WHERE id=?"

        try:
            self.conn.execute(query, tuple(fields.values()) + (doc_id,))
            self.conn.commit()
        except Exception as e:
            print(e)
            return False

        return True


storage = Storage()
