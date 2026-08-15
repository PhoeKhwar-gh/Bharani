import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "contacts.db"


class ContactDB:
    def __init__(self, db_path=None):
        self.db_path = str(db_path or DB_PATH)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_table()

    def _create_table(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT DEFAULT '',
                email TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.commit()

    def add_contact(self, name, phone, email, notes):
        cur = self.conn.execute(
            "INSERT INTO contacts (name, phone, email, notes) VALUES (?, ?, ?, ?)",
            (name, phone, email, notes),
        )
        self.conn.commit()
        return cur.lastrowid

    def update_contact(self, contact_id, name, phone, email, notes):
        self.conn.execute(
            "UPDATE contacts SET name = ?, phone = ?, email = ?, notes = ? WHERE id = ?",
            (name, phone, email, notes, contact_id),
        )
        self.conn.commit()

    def delete_contact(self, contact_id):
        self.conn.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        self.conn.commit()

    def search_contacts(self, term=""):
        term = f"%{term.strip()}%"
        rows = self.conn.execute(
            """
            SELECT * FROM contacts
            WHERE name LIKE ? OR phone LIKE ? OR email LIKE ? OR notes LIKE ?
            ORDER BY name COLLATE NOCASE
            """,
            (term, term, term, term),
        ).fetchall()
        return [dict(row) for row in rows]

    def get_all_contacts(self):
        return self.search_contacts("")

    def get_contact(self, contact_id):
        row = self.conn.execute(
            "SELECT * FROM contacts WHERE id = ?", (contact_id,)
        ).fetchone()
        return dict(row) if row else None

    def close(self):
        self.conn.close()
