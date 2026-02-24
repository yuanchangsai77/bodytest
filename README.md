# bodytest 项目概览

这是一个以 **多模型 LLM API 调用** 为核心的 Python 项目，目前包含：

- `llmapiconfig/`：统一封装 OpenAI / Claude / Gemini / 通义千问 / 智谱 的配置与客户端。
- `shell/pyshell/`：在 shell 场景中调用 LLM 的示例与 Agent 框架。
- `prompt/`：用于 Agent 的系统提示词目录（当前文件存在，但内容尚未完善）。
- `API_SETUP.md`：API 密钥申请与 `.env` 配置说明。

## 当前完整度（简评）

项目处于 **“基础能力可用、工程化未完成”** 阶段：

- ✅ 已有可复用的配置加载与多厂商 API 调用逻辑。
- ✅ 已有 shell 示例和 agent 执行框架雏形。
- ⚠️ 顶层入口 `main.py` 仍为占位示例。
- ⚠️ `prompt/*.md` 当前为空，Agent 依赖的提示词尚未落地。
- ⚠️ 框架代码引用了 `cli-lib/agents.json`、`cli-lib/main.json` 等文件，仓库中暂未提供。

## 快速使用

### 1) 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2) 配置环境变量

```bash
cp llmapiconfig/.env.example .env
# 编辑 .env，至少填写一个可用提供商的 API KEY（推荐 Gemini）
```

可参考：`API_SETUP.md`。

### 3) 直接调用 LLM 客户端

```python
import asyncio
from llmapiconfig.llm_client import simple_chat

async def run():
    print(await simple_chat("你好，请做个自我介绍"))

asyncio.run(run())
```

### 4) 运行 shell 示例

```bash
python shell/pyshell/llm_example_optimized.py
```

> 说明：如果要跑 `agent_framework.py` 的完整多轮流程，需要补齐 prompt 内容与 `cli-lib` 配置文件。
