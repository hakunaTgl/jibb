"""Core models for lightweight project and task management."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from enum import Enum
from typing import Iterable


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"


@dataclass
class Task:
    title: str
    owner: str = ""
    status: TaskStatus = TaskStatus.TODO
    priority: int = 3
    due_date: date | None = None
    notes: str = ""
    id: int | None = None

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("Task title cannot be empty")
        if not 1 <= self.priority <= 5:
            raise ValueError("priority must be between 1 and 5")

    @property
    def complete(self) -> bool:
        return self.status is TaskStatus.DONE

    def to_dict(self) -> dict:
        data = asdict(self)
        data["status"] = self.status.value
        data["due_date"] = self.due_date.isoformat() if self.due_date else None
        return data


@dataclass
class Project:
    name: str
    tasks: list[Task] = field(default_factory=list)
    id: int | None = None

    def add(self, task: Task) -> Task:
        self.tasks.append(task)
        return task

    def extend(self, tasks: Iterable[Task]) -> None:
        self.tasks.extend(tasks)

    def task(self, task_id: int) -> Task:
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise KeyError(f"Task not found: {task_id}")

    @property
    def completion_percent(self) -> float:
        if not self.tasks:
            return 0.0
        return round(sum(task.complete for task in self.tasks) / len(self.tasks) * 100, 1)

    def summary(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "tasks": len(self.tasks),
            "completed": sum(task.complete for task in self.tasks),
            "completion_percent": self.completion_percent,
        }
