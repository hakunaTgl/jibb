"""Jibb project-management automation toolkit."""

from .agent import ProjectInsight, analyze_project, bootstrap_project
from .core import Project, Task, TaskStatus
from .storage import JibbStore

__all__ = [
    "Project",
    "Task",
    "TaskStatus",
    "JibbStore",
    "ProjectInsight",
    "analyze_project",
    "bootstrap_project",
]
__version__ = "0.3.0"
