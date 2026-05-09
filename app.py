import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

DATA_FILE = "todo.json"
HOST = "0.0.0.0"
PORT = 8000


def load_tasks() -> list[dict]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []


def save_tasks(tasks: list[dict]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=2)


def render_page(tasks: list[dict], message: str = "") -> str:
    rows = []
    for index, task in enumerate(tasks, start=1):
        status = "checked" if task.get("done") else ""
        title = task.get("title", "")
        rows.append(
            f"<tr>"
            f"<td>{index}</td>"
            f"<td>{title}</td>"
            f"<td><input type=checkbox disabled {status}></td>"
            f"<td>"
            f"<button type=submit name=action value=toggle_{index}>Toggle</button> "
            f"<button type=submit name=action value=delete_{index}>Delete</button>"
            f"</td>"
            f"</tr>"
        )

    tasks_html = "\n".join(rows) if rows else "<tr><td colspan='4'>No tasks yet.</td></tr>"
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Todo List</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 640px; margin: 2rem auto; padding: 0 1rem; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
    th, td {{ padding: 0.75rem; border: 1px solid #ddd; text-align: left; }}
    th {{ background: #f9f9f9; }}
    button {{ margin-right: 0.5rem; }}
    .message {{ color: #2e7d32; margin-top: 1rem; }}
  </style>
</head>
<body>
  <h1>Todo List</h1>
  <form method="POST" action="/">
    <label>
      New task:
      <input type="text" name="title" placeholder="Buy groceries" style="width: 70%;" required />
    </label>
    <button type="submit" name="action" value="add">Add</button>
    <table>
      <thead>
        <tr><th>#</th><th>Task</th><th>Done</th><th>Actions</th></tr>
      </thead>
      <tbody>
        {tasks_html}
      </tbody>
    </table>
  </form>
  <p class="message">{message}</p>
</body>
</html>
"""


class TodoHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        tasks = load_tasks()
        content = render_page(tasks)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        data = parse_qs(body)
        action = data.get("action", [""])[0]
        title = data.get("title", [""])[0].strip()

        tasks = load_tasks()
        message = ""

        if action == "add":
            if title:
                tasks.append({"title": title, "done": False})
                message = f"Added task: {title}"
            else:
                message = "Task title cannot be empty."
        elif action.startswith("toggle_"):
            index = int(action.split("_", 1)[1]) - 1
            if 0 <= index < len(tasks):
                tasks[index]["done"] = not tasks[index].get("done", False)
                message = f"Toggled task: {tasks[index]['title']}"
        elif action.startswith("delete_"):
            index = int(action.split("_", 1)[1]) - 1
            if 0 <= index < len(tasks):
                removed = tasks.pop(index)
                message = f"Deleted task: {removed['title']}"

        save_tasks(tasks)
        content = render_page(tasks, message)
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def log_message(self, format: str, *args) -> None:
        return


def run_server() -> None:
    server = HTTPServer((HOST, PORT), TodoHandler)
    print(f"Serving todo list at http://{HOST}:{PORT}/")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
