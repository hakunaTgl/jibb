"""Simple agent-ready planning helpers for Jibb.

This module intentionally keeps the first agent layer deterministic. Future LLM or
API-backed planners can plug into the same interface without changing storage or CLI.
"""

from __future__ import annotations

from dataclasses import dataclass

from .core import Project, Task, TaskStatus


@dataclass
class ProjectInsight:
    project: str
    completion_percent: float
    blocked_tasks: list[str]
    high_priority_open_tasks: list[str]
    recommended_next_task: str | None


def analyze_project(project: Project) -> ProjectInsight:
    blocked = [task.title for task in project.tasks if task.status is TaskStatus.BLOCKED]
    open_tasks = [task for task in project.tasks if not task.complete]
    high_priority = [task.title for task in open_tasks if task.priority <= 2]

    ranked = sorted(
        open_tasks,
        key=lambda task: (
            task.status is TaskStatus.BLOCKED,
            task.priority,
            task.due_date is None,
            task.due_date or __import__("datetime").date.max,
        ),
    )
    next_task = ranked[0].title if ranked else None

    return ProjectInsight(
        project=project.name,
        completion_percent=project.completion_percent,
        blocked_tasks=blocked,
        high_priority_open_tasks=high_priority,
        recommended_next_task=next_task,
    )


def bootstrap_project(name: str, goal: str) -> Project:
    """Create a sensible starter plan from a project name and goal."""
    goal = goal.strip()
    project = Project(name)
    project.extend(
        [
            Task(f"Define success criteria for: {goal}", priority=1),
            Task("Break work into milestones", priority=1),
            Task("Identify dependencies and blockers", priority=2),
            Task("Build first working version", priority=1),
            Task("Test and review results", priority=2),
            Task("Document next iteration", priority=3),
        ]
    )
    return project
