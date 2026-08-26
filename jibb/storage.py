"""SQLite persistence for Jibb projects and tasks."""

from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

from .core import Project, Task, TaskStatus


class JibbStore:
    def __init__(self, path: str | Path = "jibb.db") -> None:
        self.path = Path(path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    owner TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'todo',
                    priority INTEGER NOT NULL DEFAULT 3,
                    due_date TEXT,
                    notes TEXT NOT NULL DEFAULT '',
                    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
                )
                """
            )

    def save_project(self, project: Project) -> int:
        with self._connect() as conn:
            conn.execute("INSERT OR IGNORE INTO projects(name) VALUES (?)", (project.name,))
            row = conn.execute("SELECT id FROM projects WHERE name = ?", (project.name,)).fetchone()
            assert row is not None
            project_id = int(row["id"])
            conn.execute("DELETE FROM tasks WHERE project_id = ?", (project_id,))
            conn.executemany(
                """
                INSERT INTO tasks(project_id, title, owner, status, priority, due_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        project_id,
                        task.title,
                        task.owner,
                        task.status.value,
                        task.priority,
                        task.due_date.isoformat() if task.due_date else None,
                        task.notes,
                    )
                    for task in project.tasks
                ],
            )
            return project_id

    def load_project(self, name: str) -> Project:
        with self._connect() as conn:
            project_row = conn.execute("SELECT id, name FROM projects WHERE name = ?", (name,)).fetchone()
            if project_row is None:
                raise KeyError(f"Project not found: {name}")
            rows = conn.execute(
                "SELECT title, owner, status, priority, due_date, notes FROM tasks WHERE project_id = ? ORDER BY id",
                (project_row["id"],),
            ).fetchall()

        project = Project(project_row["name"])
        for row in rows:
            project.add(
                Task(
                    title=row["title"],
                    owner=row["owner"],
                    status=TaskStatus(row["status"]),
                    priority=row["priority"],
                    due_date=date.fromisoformat(row["due_date"]) if row["due_date"] else None,
                    notes=row["notes"],
                )
            )
        return project

    def list_projects(self) -> list[str]:
        with self._connect() as conn:
            return [row["name"] for row in conn.execute("SELECT name FROM projects ORDER BY name")]
