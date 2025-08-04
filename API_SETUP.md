# API密钥配置指导

## 🔑 如何获取和配置API密钥

### 1. Gemini API
1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 登录Google账号
3. 点击"Create API Key"
4. 复制生成的API密钥

### 2. OpenAI API
1. 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
2. 登录OpenAI账号
3. 点击"Create new secret key"
4. 复制生成的API密钥

### 3. Claude API (Anthropic)
1. 访问 [Anthropic Console](https://console.anthropic.com/)
2. 登录账号
3. 在API Keys页面创建新密钥
4. 复制生成的API密钥

### 4. 通义千问 (Qwen)
1. 访问 [阿里云百炼](https://bailian.console.aliyun.com/)
2. 登录阿里云账号
3. 获取API密钥

### 5. 智谱AI (Zhipu)
1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册并登录
3. 获取API密钥

## ⚙️ 配置步骤

1. **复制环境变量模板**:
   ```bash
   cp llmapiconfig/.env.example .env
   ```

2. **编辑.env文件**:
   ```bash
   # 使用你喜欢的编辑器
   nano .env
   # 或者
   vim .env
   # 或者
   code .env
   ```

3. **填入你的API密钥**:
   ```env
   # 设置默认提供商 (推荐使用gemini)
   DEFAULT_LLM_PROVIDER=gemini
   
   # Gemini配置 (推荐)
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
   GEMINI_MODEL=gemini-1.5-flash
   
   # 其他提供商配置 (可选)
   OPENAI_API_KEY=your_openai_api_key_here
   CLAUDE_API_KEY=your_claude_api_key_here
   # ... 其他配置
   ```

4. **测试配置**:
   ```bash
   uv run python test_llm_api.py
   ```

## 💡 快速开始建议

1. **推荐从Gemini开始** - 免费额度高,性能好
2. **只配置一个API密钥** - 先测试一个提供商
3. **保护你的密钥** - 不要提交到版本控制

## 🔒 安全提醒

- ✅ .env文件已添加到.gitignore
- ✅ 不要在代码中硬编码API密钥
- ✅ 不要分享包含API密钥的.env文件
- ✅ 定期轮换API密钥