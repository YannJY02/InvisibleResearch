# 🔐 Security Guide: API Key Management

本指南说明如何安全地管理和使用API密钥，特别是在使用LLM处理脚本时。

## 🚨 重要安全原则

### 1. 永远不要硬编码敏感信息
- ❌ **错误做法**：直接在代码中写入API密钥
- ✅ **正确做法**：使用环境变量或配置文件

### 2. 使用环境变量管理配置
- 所有敏感配置都通过环境变量传递
- 使用 `.env` 文件进行本地开发
- 确保 `.env` 文件在 `.gitignore` 中被忽略

## 📋 配置步骤

### 步骤 1: 复制配置模板
```bash
cp config/env.template .env
```

### 步骤 2: 编辑配置文件
在 `.env` 文件中填入真实的配置信息：
```bash
# 必需配置
OPENAI_API_KEY=sk-your-actual-api-key-here

# 可选配置
OPENAI_BASE_URL=https://your-proxy.com/v1  # 如使用代理
OPENAI_MODEL=gpt-4o                        # 使用的模型
BATCH_SIZE=20                              # 批处理大小
```

### 步骤 3: 验证配置
```bash
python scripts/04_processing/LLM_name_detect.py
```

## 🔒 安全特性

### API密钥验证
- 基本格式检查
- 长度验证
- 自动屏蔽日志中的敏感信息

### 环境隔离
- 开发、测试、生产环境使用不同的API密钥
- 定期轮换API密钥

## 📁 文件安全

### 受保护的文件类型
以下文件类型已在 `.gitignore` 中被自动忽略：
- `.env` 文件
- `*_api_key*` 文件
- `*.key` 文件

### 检查命令
确认敏感文件不会被意外提交：
```bash
git status --ignored
git check-ignore .env
```

## 🚫 常见错误

### ❌ 错误示例：硬编码密钥
```python
# 危险！不要这样做
api_key = "sk-12345abcdef..."
client = openai.OpenAI(api_key=api_key)
```

### ✅ 正确示例：环境变量
```python
# 安全做法
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("API key not found")
client = openai.OpenAI(api_key=api_key)
```

## 🔧 生产环境部署

### 服务器环境变量
```bash
# 在服务器上设置环境变量
export OPENAI_API_KEY="your-production-key"
export OPENAI_BASE_URL="your-production-endpoint"
```

### Docker环境
```dockerfile
# Dockerfile
ENV OPENAI_API_KEY=""
ENV OPENAI_BASE_URL="https://api.openai.com/v1"
```

```bash
# 运行时传递环境变量
docker run -e OPENAI_API_KEY="your-key" your-image
```

## 📝 最佳实践

1. **密钥轮换**：定期更新API密钥
2. **权限最小化**：为不同环境使用不同权限的密钥
3. **监控使用**：跟踪API使用情况和异常访问
4. **备份策略**：安全地备份和恢复配置信息
5. **审计日志**：记录API调用但不记录敏感信息

## 🆘 应急响应

### 如果API密钥泄露：
1. 立即在OpenAI平台撤销泄露的密钥
2. 生成新的API密钥
3. 更新所有使用该密钥的环境
4. 检查API使用日志，确认是否有异常访问
5. 通知相关团队成员

### 联系信息
如有安全相关问题，请联系项目维护者。

---
**记住**：安全是每个人的责任。当有疑问时，选择更安全的做法。
