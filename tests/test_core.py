from datetime import date

import pytest

from jibb import Project, Task, TaskStatus


def test_project_completion():
    project = Project("Launch")
    project.add(Task("Plan", status=TaskStatus.DONE))
    project.add(Task("Build", status=TaskStatus.IN_PROGRESS))
    assert project.completion_percent == 50.0


def test_task_serialization():
    task = Task("Ship", owner="team", due_date=date(2026, 9, 1))
    assert task.to_dict()["due_date"] == "2026-09-01"
    assert task.to_dict()["status"] == "todo"


def test_invalid_priority():
    with pytest.raises(ValueError):
        Task("Bad", priority=10)
