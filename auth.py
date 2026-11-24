"""Local account storage for TOME."""

from __future__ import annotations

import hashlib
import hmac
import os
import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).with_name("tome_users.db")


def _connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.commit()
    return connection


def _hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return digest.hex(), salt.hex()


def create_user(name: str, email: str, password: str) -> tuple[bool, str]:
    """Create an account, returning success and a user-facing message."""
    password_hash, salt = _hash_password(password)
    try:
        with _connection() as connection:
            connection.execute(
                "INSERT INTO users (name, email, password_hash, salt) VALUES (?, ?, ?, ?)",
                (name.strip(), email.strip().lower(), password_hash, salt),
            )
    except sqlite3.IntegrityError:
        return False, "An account with that email already exists."
    return True, "Account created. You can now sign in."


def authenticate(email: str, password: str) -> tuple[bool, str, str]:
    """Validate credentials and return success, message, and display name."""
    with _connection() as connection:
        row = connection.execute(
            "SELECT name, password_hash, salt FROM users WHERE email = ?",
            (email.strip().lower(),),
        ).fetchone()
    if not row:
        return False, "Email or password is incorrect.", ""
    expected_hash, _ = _hash_password(password, bytes.fromhex(row[2]))
    if not hmac.compare_digest(expected_hash, row[1]):
        return False, "Email or password is incorrect.", ""
    return True, "Welcome back.", row[0]


def save_document(email: str, name: str, text: str, summary: str, page_count: int) -> int:
    """Save or refresh a PDF in the user's local library."""
    with _connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS pdf_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                name TEXT NOT NULL,
                text TEXT NOT NULL,
                summary TEXT NOT NULL,
                page_count INTEGER NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(email, name)
            )
            """
        )
        connection.execute(
            """
            INSERT INTO pdf_documents (email, name, text, summary, page_count)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(email, name) DO UPDATE SET
                text = excluded.text,
                summary = excluded.summary,
                page_count = excluded.page_count,
                updated_at = CURRENT_TIMESTAMP
            """,
            (email.strip().lower(), name, text, summary, page_count),
        )
        row = connection.execute(
            "SELECT id FROM pdf_documents WHERE email = ? AND name = ?",
            (email.strip().lower(), name),
        ).fetchone()
        return int(row[0])


def list_documents(email: str) -> list[tuple[int, str, str, int, str]]:
    """Return saved document metadata for a user's library."""
    with _connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS pdf_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                name TEXT NOT NULL,
                text TEXT NOT NULL,
                summary TEXT NOT NULL,
                page_count INTEGER NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(email, name)
            )
            """
        )
        rows = connection.execute(
            """
            SELECT id, name, summary, page_count, updated_at
            FROM pdf_documents
            WHERE email = ?
            ORDER BY updated_at DESC
            """,
            (email.strip().lower(),),
        ).fetchall()
    return [(int(row[0]), row[1], row[2], int(row[3]), row[4]) for row in rows]


def get_document(email: str, document_id: int) -> tuple[str, str, str, int] | None:
    """Load one PDF document for its owner."""
    with _connection() as connection:
        row = connection.execute(
            """
            SELECT name, text, summary, page_count
            FROM pdf_documents
            WHERE email = ? AND id = ?
            """,
            (email.strip().lower(), document_id),
        ).fetchone()
    return (row[0], row[1], row[2], int(row[3])) if row else None
