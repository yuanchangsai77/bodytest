# bodytest 项目概览

这是一个以 **多模型 LLM API 调用 + 多轮 Agent 执行** 为核心的 Python 项目。

## 新增：AI OS 状态驱动执行模式

项目已增加一个轻量 AI OS MVP，把无状态模型包装为「可持久执行闭环」：

- `shell/pyshell/ai_os.py`
  - `StateStore`：状态层 JSON 持久化
  - `AIOSRuntime`：任务创建、step 状态流转、上下文拼装、现实验证
- `state/*.json`
  - `task_graph.json`
  - `step_log.json`
  - `project_index.json`
  - `failure_patterns.json`
  - `memory_snapshot.json`
- `docs/ai_os/state_schema.md`
  - 状态结构与 step 协议示例

## 现在可跑通的最小链路

1. `main.py` 作为统一入口，接收 `--instruction`。
2. 默认 `--runtime ai_os`：
   - 生成 task graph
   - 构建上下文（project index + memory + failures）
   - 调用已有 `call_agent_multi_turn`
   - 写回 step 状态与执行日志
   - 做 git reality check
3. 通过 `llmapiconfig/` 调用选定的大模型。

## 目录结构（当前）

```text
bodytest/
├─ main.py
├─ state/
│  ├─ task_graph.json
│  ├─ step_log.json
│  ├─ project_index.json
│  ├─ failure_patterns.json
│  └─ memory_snapshot.json
├─ docs/
│  ├─ tools/
│  └─ ai_os/
│     └─ state_schema.md
├─ shell/pyshell/
│  ├─ agent_framework.py
│  └─ ai_os.py
└─ llmapiconfig/
   ├─ settings.py
   └─ llm_client.py
```

## 快速开始

### 1) 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2) 配置环境变量

```bash
cp llmapiconfig/.env.example .env
# 编辑 .env，至少填写一个可用 provider 的 API KEY
```

### 3) 运行（AI OS 模式）

```bash
python main.py --instruction "请帮我查看当前项目文件结构"
```

### 4) 运行（旧模式）

```bash
python main.py --runtime legacy --instruction "请帮我查看当前项目文件结构"
```

> 若未配置 API KEY，会在调用模型阶段失败；但 AI OS 状态目录与执行骨架已可用。
