# Jibb

Jibb is a lightweight Python toolkit for project-management automation: model tasks and projects, calculate progress, move task data into pandas, and export clean Excel workbooks.

## What it does

- Create structured projects and tasks
- Track `todo`, `in_progress`, `blocked`, and `done` states
- Assign owners, priorities, due dates, and notes
- Calculate project completion automatically
- Convert project data to pandas DataFrames
- Export task lists to Excel
- Validate the core behavior with pytest

## Quick start

```bash
git clone https://github.com/hakunaTgl/jibb.git
cd jibb
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```python
from datetime import date

from jibb import Project, Task, TaskStatus
from jibb.export import to_excel

project = Project("Jibb Launch")
project.add(Task("Design workflow", owner="Tyler", status=TaskStatus.DONE))
project.add(Task("Build automation", owner="Tyler", priority=1, due_date=date(2026, 9, 1)))

print(project.summary())
to_excel(project, "output/jibb-launch.xlsx")
```

## Tests

```bash
pytest -q
```

## Structure

```text
jibb/
├── jibb/
│   ├── __init__.py
│   ├── core.py
│   └── export.py
├── tests/
│   └── test_core.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Roadmap

Next layers can include a CLI, persistent JSON/SQLite storage, API integrations, dashboards, scheduling, and agent-driven project automation.

## Status

Early development — core project/task models and spreadsheet export are implemented.
