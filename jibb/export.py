"""DataFrame and Excel export helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .core import Project


def to_dataframe(project: Project) -> pd.DataFrame:
    """Convert a project's tasks into a DataFrame."""
    return pd.DataFrame([task.to_dict() for task in project.tasks])


def to_excel(project: Project, path: str | Path) -> Path:
    """Export project tasks to an .xlsx workbook."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    to_dataframe(project).to_excel(output, index=False, engine="openpyxl")
    return output
