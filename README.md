# bodytest 项目概览

这是一个以 **多模型 LLM API 调用 + 多轮 Agent 执行** 为核心的 Python 项目。

## 现在可跑通的最小链路

1. `main.py` 作为统一入口，接收 `--instruction`。
2. `shell/pyshell/agent_framework.py` 读取：
   - `cli-lib/agents.json`（agent 注册）
   - `cli-lib/main.json`（工具注册）
   - `prompt/*.md`（系统提示词）
3. 通过 `llmapiconfig/` 调用选定的大模型。
4. 模型返回 JSON 命令后由执行器执行并返回结果。

## 目录结构（建议/当前）

```text
bodytest/
├─ main.py                       # CLI统一入口
├─ cli-lib/
│  ├─ agents.json                # agent注册
│  └─ main.json                  # 工具注册
├─ prompt/
│  ├─ 任务规划师.md
│  ├─ CLI命令生成器.md
│  ├─ CLI工具执行引擎.md
│  ├─ 交互与意图分析师.md
│  └─ 状态监控反馈机.md
├─ docs/tools/
│  ├─ project_scaffold.md
│  └─ list_files.md
├─ shell/pyshell/
│  ├─ agent_framework.py
│  └─ api_client.py
└─ llmapiconfig/
   ├─ settings.py
   └─ llm_client.py
```

## 哪些是“必须”的

- `llmapiconfig/`：API 配置与请求封装（必须）
- `shell/pyshell/agent_framework.py`：多轮调度与执行（必须）
- `cli-lib/*.json`：agent/tool 注册（必须）
- `prompt/*.md`：约束 LLM 返回结构化 JSON（必须）
- `docs/tools/*.md`：给命令生成器提供工具细节（建议必须）
- `main.py`：可执行入口（必须）

## 哪些在最小可跑通链路里可暂缓

- 复杂的多 Agent 编排（可先只保留 `task_planner`）
- 前端界面（当前无需）
- 数据库存储、消息队列（当前无需）

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

### 3) 运行最小链路

```bash
python main.py --instruction "请帮我查看当前项目文件结构"
```

> 若未配置 API KEY，会在调用模型阶段失败；但项目结构与调用链路已完整。
