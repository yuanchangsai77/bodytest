# LLM API Config 文件夹

这个文件夹包含了大模型API的配置和客户端代码,支持多种主流大模型服务.

## 文件说明

- `settings.py` - 配置管理,支持从环境变量加载API密钥和参数
- `llm_client.py` - 大模型客户端封装,提供统一的API调用接口
- `example_usage.py` - 使用示例,展示各种调用场景
- `.env.example` - 环境变量配置示例

## 支持的大模型服务

- **Gemini** (Google, 默认推荐) - Gemini 1.5 Flash
- **OpenAI** (GPT-3.5, GPT-4等)
- **Claude** (Anthropic)
- **通义千问** (阿里云)
- **智谱AI** (GLM-4等)

## 快速开始

1. 复制环境变量配置文件:
   ```bash
   cp llmapiconfig/.env.example .env
   ```

2. 编辑 `.env` 文件,填入你的API密钥:
   ```bash
   # 默认使用Gemini (推荐)
   DEFAULT_LLM_PROVIDER=gemini
   
   # 填入Gemini API密钥
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. 安装依赖:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

4. 运行示例:
   ```python
   from llmapiconfig.llm_client import simple_chat
   import asyncio
   
   async def test():
       response = await simple_chat("你好,世界！")
       print(response)
   
   asyncio.run(test())
   ```

## 使用方法

### 基础聊天
```python
from llmapiconfig.llm_client import simple_chat

# 简单对话
response = await simple_chat("请介绍一下Python")
print(response)
```

### 多轮对话
```python
from llmapiconfig.llm_client import chat

messages = [
    {"role": "system", "content": "你是一个编程助手"},
    {"role": "user", "content": "如何学习Python？"},
    {"role": "assistant", "content": "建议从基础语法开始..."},
    {"role": "user", "content": "有什么好的学习资源？"}
]

response = await chat(messages)
```

### 指定提供商
```python
# 使用Claude
response = await simple_chat("写一首诗", provider="claude")

# 使用OpenAI
response = await simple_chat("翻译这段文字", provider="openai")

# 使用Gemini (默认)
response = await simple_chat("解释量子计算", provider="gemini")
```

### 流式输出
```python
from llmapiconfig.llm_client import LLMClient

async with LLMClient() as client:
    stream = await client.chat_completion(messages, stream=True)
    async for chunk in stream:
        # 处理流式数据
        pass
```

## 配置说明

每个提供商都支持以下配置项:
- `API_KEY` - API密钥
- `BASE_URL` - API基础URL
- `MODEL` - 使用的模型名称
- `MAX_TOKENS` - 最大token数
- `TEMPERATURE` - 温度参数(控制随机性)

## 注意事项

1. 请妥善保管API密钥,不要提交到版本控制系统
2. 不同提供商的API格式略有差异,客户端已做统一处理
3. 流式输出的格式因提供商而异,请参考示例代码
4. 建议在生产环境中添加重试机制和错误处理