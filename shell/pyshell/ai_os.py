import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


class StateStore:
    """Persistent JSON-backed state store for AI OS."""

    DEFAULTS: dict[str, Any] = {
        "task_graph.json": {"tasks": []},
        "step_log.json": {"logs": []},
        "project_index.json": {"generated_at": None, "tree": []},
        "failure_patterns.json": {"patterns": []},
        "memory_snapshot.json": {"updated_at": None, "summary": "", "recent_events": []},
    }

    def __init__(self, workspace_root: str) -> None:
        self.workspace_root = Path(workspace_root)
        self.state_dir = self.workspace_root / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self._bootstrap()

    def _bootstrap(self) -> None:
        for filename, default_data in self.DEFAULTS.items():
            path = self.state_dir / filename
            if not path.exists():
                self._write_json(path, default_data)

    def _read_json(self, path: Path) -> Any:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _write_json(self, path: Path, data: Any) -> None:
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def load(self, filename: str) -> Any:
        return self._read_json(self.state_dir / filename)

    def save(self, filename: str, data: Any) -> None:
        self._write_json(self.state_dir / filename, data)


class AIOSRuntime:
    """State-driven runtime that wraps stateless model execution into a durable loop."""

    def __init__(self, workspace_root: str) -> None:
        self.workspace_root = workspace_root
        self.state = StateStore(workspace_root)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _scan_project_tree(self) -> list[str]:
        entries: list[str] = []
        for root, dirs, files in os.walk(self.workspace_root):
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", ".venv"}]
            rel_root = os.path.relpath(root, self.workspace_root)
            depth = rel_root.count(os.sep)
            if depth > 2:
                continue
            if rel_root == ".":
                rel_root = ""
            for name in sorted(files):
                if name.endswith((".py", ".md", ".json", ".toml")):
                    rel_path = os.path.join(rel_root, name).strip(os.sep)
                    entries.append(rel_path)
        return entries[:200]

    def refresh_project_index(self) -> None:
        snapshot = {
            "generated_at": self._now(),
            "tree": self._scan_project_tree(),
        }
        self.state.save("project_index.json", snapshot)

    def create_task(self, instruction: str) -> dict[str, Any]:
        graph = self.state.load("task_graph.json")
        task_id = f"task-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        step_id = f"{task_id}-step-1"
        task = {
            "task_id": task_id,
            "instruction": instruction,
            "created_at": self._now(),
            "status": "pending",
            "steps": [
                {
                    "step_id": step_id,
                    "name": "execute_instruction",
                    "input": instruction,
                    "output": None,
                    "depends_on": [],
                    "status": "pending",
                    "started_at": None,
                    "finished_at": None,
                }
            ],
        }
        graph["tasks"].append(task)
        self.state.save("task_graph.json", graph)
        return task

    def _append_step_log(self, task_id: str, step_id: str, event: str, detail: str) -> None:
        step_log = self.state.load("step_log.json")
        step_log["logs"].append(
            {
                "timestamp": self._now(),
                "task_id": task_id,
                "step_id": step_id,
                "event": event,
                "detail": detail,
            }
        )
        self.state.save("step_log.json", step_log)

    def _update_step(self, task_id: str, step_id: str, **updates: Any) -> None:
        graph = self.state.load("task_graph.json")
        for task in graph["tasks"]:
            if task["task_id"] != task_id:
                continue
            for step in task["steps"]:
                if step["step_id"] == step_id:
                    step.update(updates)
            if all(step["status"] == "done" for step in task["steps"]):
                task["status"] = "done"
            elif any(step["status"] == "failed" for step in task["steps"]):
                task["status"] = "failed"
            elif any(step["status"] == "running" for step in task["steps"]):
                task["status"] = "running"
        self.state.save("task_graph.json", graph)

    def _build_context(self, task: dict[str, Any], step: dict[str, Any]) -> dict[str, Any]:
        memory = self.state.load("memory_snapshot.json")
        failures = self.state.load("failure_patterns.json")
        index = self.state.load("project_index.json")
        return {
            "task": {"task_id": task["task_id"], "instruction": task["instruction"], "status": task["status"]},
            "step": {"step_id": step["step_id"], "name": step["name"], "input": step["input"]},
            "memory_summary": memory.get("summary", ""),
            "recent_failures": failures.get("patterns", [])[-3:],
            "project_tree_excerpt": index.get("tree", [])[:40],
        }

    def _verify_reality(self) -> dict[str, Any]:
        git_result = subprocess.run(
            ["git", "status", "--short"],
            cwd=self.workspace_root,
            capture_output=True,
            text=True,
            check=False,
        )
        return {
            "git_status": git_result.stdout.strip().splitlines() if git_result.stdout else [],
            "git_status_rc": git_result.returncode,
        }

    def run_once(self, agent_name: str, instruction: str, executor: Callable[[str, str], str]) -> str:
        self.refresh_project_index()
        task = self.create_task(instruction)
        step = task["steps"][0]

        self._update_step(task["task_id"], step["step_id"], status="running", started_at=self._now())
        self._append_step_log(task["task_id"], step["step_id"], "started", "step execution started")

        context = self._build_context(task, step)
        model_input = (
            f"{instruction}\n\n"
            "[AI_OS_CONTEXT]\n"
            f"{json.dumps(context, ensure_ascii=False, indent=2)}\n"
            "请继续输出结构化 JSON。"
        )

        raw_result = executor(agent_name, model_input)
        parsed_result: dict[str, Any]
        try:
            parsed_result = json.loads(raw_result)
        except json.JSONDecodeError:
            parsed_result = {"status": "failure", "error": "non_json_output", "raw": raw_result}

        ok = parsed_result.get("status") in {"success", "done"}
        final_status = "done" if ok else "failed"
        reality = self._verify_reality()

        self._update_step(
            task["task_id"],
            step["step_id"],
            status=final_status,
            output=parsed_result,
            finished_at=self._now(),
        )
        self._append_step_log(task["task_id"], step["step_id"], final_status, json.dumps(parsed_result, ensure_ascii=False))

        memory = {
            "updated_at": self._now(),
            "summary": f"last_task={task['task_id']}, step={step['step_id']}, status={final_status}",
            "recent_events": [
                {"task_id": task["task_id"], "step_id": step["step_id"], "status": final_status},
                {"reality": reality},
            ],
        }
        self.state.save("memory_snapshot.json", memory)

        return json.dumps(
            {
                "status": final_status,
                "task_id": task["task_id"],
                "step_id": step["step_id"],
                "result": parsed_result,
                "reality_check": reality,
            },
            ensure_ascii=False,
            indent=2,
        )
