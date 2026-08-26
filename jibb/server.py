"""Zero-dependency local REST API and dashboard for Jibb."""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

from .core import Task, TaskStatus
from .storage import JibbStore


DASHBOARD = """<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Jibb Dashboard</title>
<style>
body{font-family:system-ui,sans-serif;margin:0;background:#0f1115;color:#f5f7fb}main{max-width:1050px;margin:auto;padding:32px}h1{font-size:42px;margin-bottom:6px}.muted{color:#a8b0bd}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}.card{background:#181c23;border:1px solid #2a313c;border-radius:18px;padding:18px}button{background:#fff;border:0;border-radius:10px;padding:8px 12px;font-weight:700;cursor:pointer}.task{padding:9px 0;border-top:1px solid #2a313c}.done{text-decoration:line-through;color:#7e8794}</style>
</head>
<body><main><h1>Jibb</h1><div class='muted'>Project command center</div><p><button onclick='load()'>Refresh</button></p><div id='projects' class='grid'></div></main>
<script>
async function load(){const names=await (await fetch('/api/projects')).json();const root=document.getElementById('projects');root.innerHTML='';for(const name of names){const p=await (await fetch('/api/projects/'+encodeURIComponent(name))).json();const el=document.createElement('section');el.className='card';el.innerHTML=`<h2>${escapeHtml(p.name)}</h2><div class='muted'>${p.completion_percent}% complete · ${p.tasks.length} tasks</div>`+p.tasks.map(t=>`<div class='task ${t.status==='done'?'done':''}'>#${t.id} · P${t.priority} · ${escapeHtml(t.title)} <span class='muted'>${t.status}</span></div>`).join('');root.appendChild(el)}}
function escapeHtml(s){return String(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}load();
</script></body></html>"""


def make_handler(store: JibbStore):
    class Handler(BaseHTTPRequestHandler):
        def _json(self, payload, status=HTTPStatus.OK):
            body = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _body(self):
            length = int(self.headers.get("Content-Length", "0"))
            if not length:
                return {}
            return json.loads(self.rfile.read(length))

        def do_GET(self):
            if self.path == "/":
                body = DASHBOARD.encode()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if self.path == "/api/projects":
                self._json(store.list_projects())
                return
            if self.path.startswith("/api/projects/"):
                name = unquote(self.path.removeprefix("/api/projects/"))
                try:
                    project = store.load_project(name)
                except KeyError as exc:
                    self._json({"error": str(exc)}, HTTPStatus.NOT_FOUND)
                    return
                payload = project.summary() | {"tasks": [task.to_dict() for task in project.tasks]}
                self._json(payload)
                return
            self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)

        def do_POST(self):
            try:
                data = self._body()
                if self.path == "/api/projects":
                    name = str(data["name"]).strip()
                    store.ensure_project(name)
                    self._json({"name": name}, HTTPStatus.CREATED)
                    return
                if self.path.startswith("/api/projects/") and self.path.endswith("/tasks"):
                    name = unquote(self.path[len("/api/projects/"):-len("/tasks")])
                    task = Task(
                        title=data["title"],
                        owner=data.get("owner", ""),
                        status=TaskStatus(data.get("status", "todo")),
                        priority=int(data.get("priority", 3)),
                        notes=data.get("notes", ""),
                    )
                    task_id = store.add_task(name, task)
                    self._json({"id": task_id}, HTTPStatus.CREATED)
                    return
                if self.path.startswith("/api/tasks/") and self.path.endswith("/complete"):
                    task_id = int(self.path.split("/")[3])
                    store.complete_task(task_id)
                    self._json({"id": task_id, "status": "done"})
                    return
            except (KeyError, ValueError, json.JSONDecodeError) as exc:
                self._json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)

        def do_PATCH(self):
            if not self.path.startswith("/api/tasks/"):
                self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)
                return
            try:
                task_id = int(self.path.split("/")[3])
                data = self._body()
                if "status" in data:
                    data["status"] = TaskStatus(data["status"])
                store.update_task(task_id, **data)
                self._json({"id": task_id, "updated": sorted(data)})
            except (KeyError, ValueError, json.JSONDecodeError) as exc:
                self._json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)

        def log_message(self, format, *args):
            return

    return Handler


def serve(store: JibbStore, host: str = "127.0.0.1", port: int = 8765) -> None:
    server = ThreadingHTTPServer((host, port), make_handler(store))
    print(f"Jibb dashboard: http://{host}:{port}")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
