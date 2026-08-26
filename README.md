# Jibb

Jibb is a lightweight Python project-management automation toolkit with persistent SQLite storage, a command-line interface, spreadsheet export, a local REST API/dashboard, GitHub issue import, and an agent-ready planning layer.

## Current capabilities

- Create structured projects and tasks
- Stable project/task IDs
- Track `todo`, `in_progress`, `blocked`, and `done` states
- Assign owners, priorities, due dates, and notes
- Edit, complete, and remove tasks by ID
- Persist everything in SQLite
- Calculate project completion automatically
- Analyze blockers and recommend the next task
- Bootstrap a starter project plan from a goal
- Convert project data to pandas DataFrames
- Export task lists to Excel
- Run a local REST API and web dashboard
- Import open GitHub issues into a Jibb project
- Validate core/storage behavior with pytest

## Install

```bash
git clone https://github.com/hakunaTgl/jibb.git
cd jibb
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## CLI

```bash
python -m jibb create "Empire OS"
python -m jibb add "Empire OS" "Build dashboard" --owner Tyler --priority 1
python -m jibb add "Empire OS" "Connect APIs" --status in_progress --priority 2
python -m jibb show "Empire OS"
python -m jibb done 1
python -m jibb edit 2 --priority 1 --owner Tyler
python -m jibb remove 2
python -m jibb export "Empire OS" output/empire-os.xlsx
```

Use a custom database:

```bash
python -m jibb --db data/projects.db list
```

## Dashboard + REST API

Start Jibb's local command center:

```bash
python -m jibb serve
```

Then open:

```text
http://127.0.0.1:8765
```

Available API routes include:

```text
GET    /api/projects
GET    /api/projects/{name}
POST   /api/projects
POST   /api/projects/{name}/tasks
PATCH  /api/tasks/{id}
POST   /api/tasks/{id}/complete
```

The dashboard intentionally uses Python's standard-library HTTP server so Jibb does not need a heavy web framework just to run locally.

## GitHub integration

Set an optional GitHub token for private repositories or higher API limits:

```bash
export GITHUB_TOKEN=your_token_here
```

Import open issues from a repository into a Jibb project:

```bash
python -m jibb github-import "Jibb Dev" hakunaTgl/jibb
```

The GitHub adapter can also be used directly:

```python
from jibb.github import GitHubClient

client = GitHubClient()
print(client.summary("hakunaTgl/jibb"))
```

## Python API

```python
from datetime import date

from jibb import JibbStore, Task, TaskStatus, analyze_project

store = JibbStore("jibb.db")
task_id = store.add_task(
    "Jibb Launch",
    Task("Build automation", owner="Tyler", priority=1, due_date=date(2026, 9, 1)),
)

store.update_task(task_id, status=TaskStatus.IN_PROGRESS)
project = store.load_project("Jibb Launch")
print(project.summary())
print(analyze_project(project))
```

## Agent-ready planning

Jibb's planning layer is deterministic by design. It can inspect a project, surface blockers and high-priority work, and choose a recommended next task.

```python
from jibb import analyze_project, bootstrap_project

project = bootstrap_project("Agent Platform", "build an autonomous project manager")
insight = analyze_project(project)
print(insight.recommended_next_task)
```

This interface is ready for a later LLM-backed planner without requiring storage, CLI, or project models to be rewritten.

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
│   ├── github.py
│   ├── server.py
│   └── storage.py
├── tests/
│   ├── test_core.py
│   ├── test_crud.py
│   └── test_storage.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Roadmap

### v0.4
- JSON import/export
- Project deletion/rename
- API authentication option
- Dashboard task creation/editing controls
- GitHub two-way issue sync
- Execution/event history

### v0.5
- Pluggable AI planner
- Tool/action registry
- Autonomous project review cycles
- Approval gates for write actions
- Project memory
- Scheduled jobs and reminders

### v1.0 direction
- Multi-project autonomous command center
- GitHub + local workflow orchestration
- Human approval policies
- Agent execution history and rollback support
- Extensible adapters for external services

## Status

**v0.3 implemented:** stable task IDs, full task CRUD, SQLite persistence, CLI, REST API, local dashboard, GitHub issue import, spreadsheet export, tests, and the deterministic agent-ready planning layer.
