# Jibb

Jibb is a lightweight Python project-management automation toolkit with persistent SQLite storage, a command-line interface, spreadsheet export, and an agent-ready planning layer.

## Current capabilities

- Create structured projects and tasks
- Track `todo`, `in_progress`, `blocked`, and `done` states
- Assign owners, priorities, due dates, and notes
- Persist projects and tasks in SQLite
- Calculate project completion automatically
- Analyze blockers and recommend the next task
- Bootstrap a starter project plan from a goal
- Convert project data to pandas DataFrames
- Export task lists to Excel
- Use Jibb directly from the terminal
- Validate core behavior with pytest

## Install

```bash
git clone https://github.com/hakunaTgl/jibb.git
cd jibb
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Python API

```python
from datetime import date

from jibb import JibbStore, Project, Task, TaskStatus, analyze_project

project = Project("Jibb Launch")
project.add(Task("Design workflow", owner="Tyler", status=TaskStatus.DONE))
project.add(Task("Build automation", owner="Tyler", priority=1, due_date=date(2026, 9, 1)))

store = JibbStore("jibb.db")
store.save_project(project)

loaded = store.load_project("Jibb Launch")
print(loaded.summary())
print(analyze_project(loaded))
```

## CLI

Run Jibb with `python -m jibb`:

```bash
python -m jibb create "Empire OS"
python -m jibb add "Empire OS" "Build dashboard" --owner Tyler --priority 1
python -m jibb add "Empire OS" "Connect APIs" --status in_progress --priority 2
python -m jibb list
python -m jibb show "Empire OS"
python -m jibb export "Empire OS" output/empire-os.xlsx
```

Use a custom database:

```bash
python -m jibb --db data/projects.db list
```

## Agent-ready planning

Jibb's first planning layer is deterministic by design. It can already inspect a project, surface blockers and high-priority work, and choose a recommended next task.

```python
from jibb import analyze_project, bootstrap_project

project = bootstrap_project("Agent Platform", "build an autonomous project manager")
insight = analyze_project(project)
print(insight.recommended_next_task)
```

That interface is intentionally ready for a later LLM-backed planner without requiring the storage or project model to be rewritten.

## Tests

```bash
pytest -q
```

## Structure

```text
jibb/
├── jibb/
│   ├── __init__.py
│   ├── __main__.py
│   ├── agent.py
│   ├── cli.py
│   ├── core.py
│   ├── export.py
│   └── storage.py
├── tests/
│   ├── test_core.py
│   └── test_storage.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Roadmap

### v0.3
- CLI commands for updating and completing existing tasks
- Project deletion and task IDs
- JSON import/export
- Better error handling and terminal output

### v0.4
- Local REST API
- Web dashboard
- Scheduled jobs and reminders
- GitHub/project integration adapters

### v0.5
- Pluggable AI planner
- Tool/action registry
- Autonomous project review cycles
- Approval gates for write actions
- Project memory and execution history

## Status

**v0.2 foundation implemented:** core models, spreadsheet export, SQLite persistence, CLI, tests, and the first agent-ready analysis layer.
