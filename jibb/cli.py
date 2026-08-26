"""Command-line interface for Jibb."""

from __future__ import annotations

import argparse
from datetime import date

from .core import Project, Task, TaskStatus
from .export import to_excel
from .storage import JibbStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jibb", description="Lightweight project-management automation")
    parser.add_argument("--db", default="jibb.db", help="SQLite database path")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="Create a project")
    create.add_argument("name")

    add = sub.add_parser("add", help="Add a task to a project")
    add.add_argument("project")
    add.add_argument("title")
    add.add_argument("--owner", default="")
    add.add_argument("--status", choices=[s.value for s in TaskStatus], default="todo")
    add.add_argument("--priority", type=int, default=3)
    add.add_argument("--due")
    add.add_argument("--notes", default="")

    edit = sub.add_parser("edit", help="Edit a task by ID")
    edit.add_argument("task_id", type=int)
    edit.add_argument("--title")
    edit.add_argument("--owner")
    edit.add_argument("--status", choices=[s.value for s in TaskStatus])
    edit.add_argument("--priority", type=int)
    edit.add_argument("--due")
    edit.add_argument("--notes")

    done = sub.add_parser("done", help="Mark a task complete")
    done.add_argument("task_id", type=int)

    remove = sub.add_parser("remove", help="Delete a task")
    remove.add_argument("task_id", type=int)

    sub.add_parser("list", help="List projects")

    show = sub.add_parser("show", help="Show a project")
    show.add_argument("project")

    export = sub.add_parser("export", help="Export a project to Excel")
    export.add_argument("project")
    export.add_argument("path")

    serve = sub.add_parser("serve", help="Run the local Jibb dashboard/API")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)

    github = sub.add_parser("github-import", help="Import open GitHub issues as tasks")
    github.add_argument("project")
    github.add_argument("repo", help="owner/repo")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = JibbStore(args.db)

    if args.command == "create":
        store.save_project(Project(args.name))
        print(f"Created project: {args.name}")
        return 0

    if args.command == "list":
        for name in store.list_projects():
            print(name)
        return 0

    if args.command == "add":
        task = Task(
            args.title,
            owner=args.owner,
            status=TaskStatus(args.status),
            priority=args.priority,
            due_date=date.fromisoformat(args.due) if args.due else None,
            notes=args.notes,
        )
        task_id = store.add_task(args.project, task)
        print(f"Added task #{task_id} to {args.project}: {args.title}")
        return 0

    if args.command == "edit":
        changes = {
            key: value
            for key, value in {
                "title": args.title,
                "owner": args.owner,
                "status": TaskStatus(args.status) if args.status else None,
                "priority": args.priority,
                "due_date": date.fromisoformat(args.due) if args.due else None,
                "notes": args.notes,
            }.items()
            if value is not None
        }
        store.update_task(args.task_id, **changes)
        print(f"Updated task #{args.task_id}")
        return 0

    if args.command == "done":
        store.complete_task(args.task_id)
        print(f"Completed task #{args.task_id}")
        return 0

    if args.command == "remove":
        store.delete_task(args.task_id)
        print(f"Deleted task #{args.task_id}")
        return 0

    if args.command == "show":
        project = store.load_project(args.project)
        print(f"{project.name} — {project.completion_percent}% complete")
        for task in project.tasks:
            owner = f" @{task.owner}" if task.owner else ""
            due = f" due:{task.due_date}" if task.due_date else ""
            print(f"#{task.id} [{task.status.value}] P{task.priority} {task.title}{owner}{due}")
        return 0

    if args.command == "export":
        project = store.load_project(args.project)
        output = to_excel(project, args.path)
        print(output)
        return 0

    if args.command == "serve":
        from .server import serve
        serve(store, host=args.host, port=args.port)
        return 0

    if args.command == "github-import":
        from .github import GitHubClient
        client = GitHubClient()
        issues = client.open_issues(args.repo)
        imported = 0
        for issue in issues:
            store.add_task(
                args.project,
                Task(
                    title=f"GH#{issue['number']} {issue['title']}",
                    notes=issue.get("html_url", ""),
                    priority=2,
                ),
            )
            imported += 1
        print(f"Imported {imported} GitHub issues into {args.project}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
