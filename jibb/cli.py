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

    sub.add_parser("list", help="List projects")

    show = sub.add_parser("show", help="Show a project")
    show.add_argument("project")

    export = sub.add_parser("export", help="Export a project to Excel")
    export.add_argument("project")
    export.add_argument("path")

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
        try:
            project = store.load_project(args.project)
        except KeyError:
            project = Project(args.project)
        project.add(
            Task(
                args.title,
                owner=args.owner,
                status=TaskStatus(args.status),
                priority=args.priority,
                due_date=date.fromisoformat(args.due) if args.due else None,
                notes=args.notes,
            )
        )
        store.save_project(project)
        print(f"Added task to {project.name}: {args.title}")
        return 0

    if args.command == "show":
        project = store.load_project(args.project)
        print(f"{project.name} — {project.completion_percent}% complete")
        for task in project.tasks:
            owner = f" @{task.owner}" if task.owner else ""
            print(f"[{task.status.value}] P{task.priority} {task.title}{owner}")
        return 0

    if args.command == "export":
        project = store.load_project(args.project)
        output = to_excel(project, args.path)
        print(output)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
