# AI OS 状态层 Schema（MVP）

## 1) task_graph.json

```json
{
  "tasks": [
    {
      "task_id": "task-20260101010101",
      "instruction": "用户原始任务",
      "created_at": "ISO-8601",
      "status": "pending|running|done|failed",
      "steps": [
        {
          "step_id": "task-...-step-1",
          "name": "execute_instruction",
          "input": "step输入",
          "output": {},
          "depends_on": [],
          "status": "pending|running|done|failed",
          "started_at": "ISO-8601|null",
          "finished_at": "ISO-8601|null"
        }
      ]
    }
  ]
}
```

## 2) step_log.json

```json
{
  "logs": [
    {
      "timestamp": "ISO-8601",
      "task_id": "task id",
      "step_id": "step id",
      "event": "started|done|failed",
      "detail": "string"
    }
  ]
}
```

## 3) project_index.json

```json
{
  "generated_at": "ISO-8601|null",
  "tree": ["main.py", "shell/pyshell/ai_os.py"]
}
```

## 4) failure_patterns.json

```json
{
  "patterns": [
    {
      "signature": "missing_required_param",
      "reason": "调用工具时缺参数",
      "last_seen": "ISO-8601"
    }
  ]
}
```

## 5) memory_snapshot.json

```json
{
  "updated_at": "ISO-8601|null",
  "summary": "最近一次执行摘要",
  "recent_events": []
}
```

## Step 执行协议（结构化输出）

```json
{
  "analysis": "...",
  "decision": {
    "tool": "execute_command",
    "arguments": {
      "command": "python main.py --instruction ..."
    }
  }
}
```
