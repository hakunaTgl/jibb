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
        connection.execute("PRAGMA foreign_keys = ON")
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

    def ensure_project(self, name: str) -> int:
        with self._connect() as conn:
            conn.execute("INSERT OR IGNORE INTO projects(name) VALUES (?)", (name,))
            row = conn.execute("SELECT id FROM projects WHERE name = ?", (name,)).fetchone()
            assert row is not None
            return int(row["id"])

    def save_project(self, project: Project) -> int:
        project_id = self.ensure_project(project.name)
        project.id = project_id
        for task in project.tasks:
            if task.id is None:
                task.id = self.add_task(project.name, task)
            else:
                self.update_task(task.id, title=task.title, owner=task.owner, status=task.status,
                                 priority=task.priority, due_date=task.due_date, notes=task.notes)
        return project_id

    def add_task(self, project_name: str, task: Task) -> int:
        project_id = self.ensure_project(project_name)
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO tasks(project_id, title, owner, status, priority, due_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    task.title,
                    task.owner,
                    task.status.value,
                    task.priority,
                    task.due_date.isoformat() if task.due_date else None,
                    task.notes,
                ),
            )
            task.id = int(cursor.lastrowid)
            return task.id

    def update_task(self, task_id: int, **changes) -> None:
        allowed = {"title", "owner", "status", "priority", "due_date", "notes"}
        unknown = set(changes) - allowed
        if unknown:
            raise ValueError(f"Unsupported task fields: {', '.join(sorted(unknown))}")
        if not changes:
            return
        normalized = {}
        for key, value in changes.items():
            if key == "status" and isinstance(value, TaskStatus):
                value = value.value
            if key == "due_date" and isinstance(value, date):
                value = value.isoformat()
            normalized[key] = value
        assignments = ", ".join(f"{key} = ?" for key in normalized)
        values = list(normalized.values()) + [task_id]
        with self._connect() as conn:
            cursor = conn.execute(f"UPDATE tasks SET {assignments} WHERE id = ?", values)
            if cursor.rowcount == 0:
                raise KeyError(f"Task not found: {task_id}")

    def complete_task(self, task_id: int) -> None:
        self.update_task(task_id, status=TaskStatus.DONE)

    def delete_task(self, task_id: int) -> None:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            if cursor.rowcount == 0:
                raise KeyError(f"Task not found: {task_id}")

    def load_project(self, name: str) -> Project:
        with self._connect() as conn:
            project_row = conn.execute("SELECT id, name FROM projects WHERE name = ?", (name,)).fetchone()
            if project_row is None:
                raise KeyError(f"Project not found: {name}")
            rows = conn.execute(
                "SELECT id, title, owner, status, priority, due_date, notes FROM tasks WHERE project_id = ? ORDER BY id",
                (project_row["id"],),
            ).fetchall()

        project = Project(project_row["name"], id=int(project_row["id"]))
        for row in rows:
            project.add(
                Task(
                    id=int(row["id"]),
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
