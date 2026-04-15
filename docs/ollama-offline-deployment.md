# Ollama 离线部署指南

本文档说明如何在无法联网的机器上部署 Ollama 模型，用于 GitNexus Wiki 生成。

---

## 概述

Ollama 模型可以完全离线使用。你需要在一台**联网机器**上下载模型，然后将模型文件传输到**离线机器**上。

---

## 步骤 1：在联网机器上下载模型

### 1.1 安装 Ollama

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama

# Windows
# 从 https://ollama.com/download 下载安装包
```

### 1.2 下载推荐模型

根据你的大内存机器配置，选择合适的模型：

| 模型 | 参数量 | 内存需求 | 上下文窗口 | 推荐场景 |
|------|--------|---------|-----------|---------|
| `qwen2.5:3b` | 3B | ~2GB | 4096 tokens | 小型机器，快速测试 |
| `qwen2.5:7b` | 7B | ~4GB | 8192 tokens | **推荐**，平衡性能和速度 |
| `qwen2.5:14b` | 14B | ~8GB | 8192 tokens | 大内存机器，更高质量 |
| `qwen2.5-coder:7b` | 7B | ~4GB | 8192 tokens | 代码专用，更适合技术文档 |

```bash
# 下载推荐模型（7B 版本）
ollama pull qwen2.5:7b

# 或下载代码专用模型
ollama pull qwen2.5-coder:7b

# 验证模型已下载
ollama list
```

**输出示例**：
```
NAME                ID              SIZE    MODIFIED
qwen2.5:7b          abc123def456    4.7 GB  2 minutes ago
```

---

## 步骤 2：导出模型文件

### 2.1 查找模型存储位置

Ollama 模型存储在以下位置：

- **Linux**: `~/.ollama/models/`
- **macOS**: `~/.ollama/models/`
- **Windows**: `C:\Users\<username>\.ollama\models\`

### 2.2 打包模型目录

```bash
# 打包整个模型目录
cd ~
tar -czf ollama-models.tar.gz .ollama/models/

# 查看打包文件大小
ls -lh ollama-models.tar.gz
```

**注意**：
- 7B 模型打包后约 **4-5 GB**
- 14B 模型打包后约 **8-9 GB**
- 确保有足够的磁盘空间和传输带宽

---

## 步骤 3：传输到离线机器

使用 U 盘、移动硬盘或内网文件传输工具将 `ollama-models.tar.gz` 复制到离线机器。

```bash
# 示例：使用 scp（如果内网可达）
scp ollama-models.tar.gz user@offline-machine:/tmp/

# 示例：使用 U 盘
cp ollama-models.tar.gz /media/usb-drive/
```

---

## 步骤 4：在离线机器上安装 Ollama

### 4.1 离线安装 Ollama

**方法 1：使用预编译二进制（推荐）**

在联网机器上下载 Ollama 二进制文件：

```bash
# Linux x86_64
wget https://github.com/ollama/ollama/releases/latest/download/ollama-linux-amd64 -O ollama
chmod +x ollama

# 传输到离线机器
scp ollama user@offline-machine:/usr/local/bin/
```

**方法 2：使用 Docker（推荐用于生产环境）**

在联网机器上拉取镜像：

```bash
# 拉取 Ollama 镜像
docker pull ollama/ollama:latest

# 保存为 tar 文件
docker save ollama/ollama:latest -o ollama-docker.tar

# 传输到离线机器
scp ollama-docker.tar user@offline-machine:/tmp/
```

在离线机器上加载镜像：

```bash
docker load -i /tmp/ollama-docker.tar
```

### 4.2 导入模型文件

```bash
# 解压模型文件到用户目录
cd ~
tar -xzf /tmp/ollama-models.tar.gz

# 验证模型目录结构
ls -la ~/.ollama/models/
```

---

## 步骤 5：启动 Ollama 服务

### 方法 1：直接运行（开发环境）

```bash
# 启动 Ollama 服务
ollama serve

# 在另一个终端验证
ollama list
```

### 方法 2：使用 Docker（生产环境）

```bash
# 启动 Ollama 容器
docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ~/.ollama:/root/.ollama \
  --restart always \
  ollama/ollama:latest

# 验证服务运行
docker logs ollama
curl http://localhost:11434/api/tags
```

---

## 步骤 6：配置 GitNexus 使用离线模型

### 6.1 更新 docker-compose.yml

编辑 `scripts/docker/gitnexus/docker-compose.yml`：

```yaml
environment:
  # 启用 Ollama Wiki 生成
  - OLLAMA_URL=http://172.17.0.1:11434/api/generate
  - LLM_MODEL=qwen2.5:7b  # 或 qwen2.5-coder:7b
```

**注意**：
- `172.17.0.1` 是 Docker 容器访问宿主机的默认 IP
- 如果使用 Docker Desktop（macOS/Windows），改为 `host.docker.internal`

### 6.2 重启 GitNexus 服务

```bash
cd scripts/docker/gitnexus
docker-compose down
docker-compose up -d
```

### 6.3 验证集成

```bash
# 查看 GitNexus 日志
docker logs -f gitnexus-central

# 测试 Wiki 生成
docker exec gitnexus-central gitnexus wiki /repos/<project-name> \
  --model qwen2.5:7b \
  --base-url http://172.17.0.1:11434
```

---

## 故障排查

### 问题 1：模型未找到

**症状**：`Error: model 'qwen2.5:7b' not found`

**解决方案**：
```bash
# 检查模型目录
ls -la ~/.ollama/models/manifests/registry.ollama.ai/library/

# 重新导入模型
ollama list
```

### 问题 2：Ollama 服务无法访问

**症状**：`Connection refused` 或 `timeout`

**解决方案**：
```bash
# 检查 Ollama 服务状态
curl http://localhost:11434/api/tags

# 检查防火墙
sudo ufw allow 11434/tcp

# 检查 Docker 网络（如果使用容器）
docker network inspect bridge | grep -A 10 gitnexus-central
```

### 问题 3：Prompt 截断警告

**症状**：`prompt truncated to fit context window`

**解决方案**：
- 升级到更大的模型（7B → 14B）
- 或使用代码专用模型 `qwen2.5-coder:7b`（更高效）

---

## 性能优化建议

### 1. 使用 GPU 加速（可选）

如果离线机器有 NVIDIA GPU：

```bash
# Docker 方式
docker run -d \
  --name ollama \
  --gpus all \
  -p 11434:11434 \
  -v ~/.ollama:/root/.ollama \
  --restart always \
  ollama/ollama:latest
```

### 2. 调整并发设置

编辑 `mcp_server_wrapper.py`，添加超时和重试：

```python
# 在 analyze_repo 函数中
proc = await asyncio.create_subprocess_shell(
    f"gitnexus wiki . --model {model} --base-url {base_url}",
    cwd=project_path,
    env=env,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE
)

# 设置超时（10 分钟）
try:
    await asyncio.wait_for(proc.communicate(), timeout=600)
except asyncio.TimeoutError:
    proc.kill()
    raise Exception("Wiki generation timeout")
```

### 3. 批量预热模型

在首次使用前预热模型，避免冷启动延迟：

```bash
# 预热模型
ollama run qwen2.5:7b "Hello, test prompt"
```

---

## 总结

✅ **完成步骤**：
1. 在联网机器下载模型
2. 打包并传输到离线机器
3. 安装 Ollama 并导入模型
4. 配置 GitNexus 使用离线模型
5. 验证 Wiki 生成功能

✅ **推荐配置**：
- 模型：`qwen2.5:7b` 或 `qwen2.5-coder:7b`
- 内存：至少 8GB RAM
- 存储：至少 10GB 可用空间

✅ **下一步**：
- 参考 `docs/gitnexus-centralized-service.md` 了解完整架构
- 使用 `scripts/docker/gitnexus/test_e2e.py` 测试端到端流程
