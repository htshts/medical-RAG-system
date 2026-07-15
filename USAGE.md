# Medical RAG System - 完整使用指南

## 目录
1. [系统概述](#系统概述)
2. [快速开始](#快速开始)
3. [安装方式](#安装方式)
4. [配置指南](#配置指南)
5. [API 文档](#api-文档)
6. [前端使用](#前端使用)
7. [Docker 部署](#docker-部署)
8. [故障排查](#故障排查)

---

## 系统概述

**Medical RAG System** 是一个面向转院场景的关键信息智能检索系统，基于 RAG（检索增强生成）架构，帮助医生快速从海量病历中检索关键信息并生成结构化的转院摘要。

### 核心功能
- **智能检索**：支持自然语言查询，自动理解医学术语
- **时间语义对齐**：处理复杂的时间表达式（如"3个月前"、"上周"）
- **混合检索**：结合 BM25 关键词检索和向量语义检索
- **实体提取**：自动识别疾病、症状、药物等关键实体
- **摘要生成**：一键生成结构化的转院摘要

### 技术架构
```
┌─────────────────────────────────────────────┐
│         应用层 (Frontend)                   │
│    React + TypeScript + Tailwind CSS       │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         API 层 (Backend)                   │
│      FastAPI + Uvicorn                     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│       RAG 检索层                           │
│   Query Rewrite + Hybrid Search + Rerank   │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│       数据层                                │
│  MySQL + Milvus + Elasticsearch + Redis    │
└─────────────────────────────────────────────┘
```

---

## 快速开始

### 方式一：简化演示（推荐，无需依赖）

**适用场景**：快速体验系统功能，无需安装任何依赖

**步骤**：
1. 确保已安装 Python 3.8+
2. 进入项目目录
3. 运行演示服务器：
   ```bash
   cd backend
   python demo_server_simple.py
   ```
4. 打开浏览器访问：`http://localhost:8000`

**特点**：
- ✅ 无需安装依赖
- ✅ 自动生成模拟数据
- ✅ 包含完整的前端界面
- ⚠️ 使用内存数据存储（重启后数据丢失）

---

### 方式二：完整后端（需要安装依赖）

**适用场景**：开发测试，使用完整的后端功能

**步骤**：
1. 创建虚拟环境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate  # Windows
   ```

2. 安装依赖：
   ```bash
   pip install -r backend/requirements.txt
   ```

3. 配置环境变量：
   ```bash
   cp deploy/.env.example .env
   # 编辑 .env 文件，填入你的配置
   ```

4. 启动后端服务：
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. 访问 API 文档：`http://localhost:8000/docs`

---

### 方式三：Docker 部署（生产环境）

**适用场景**：生产部署，完整的功能和数据持久化

**步骤**：
1. 确保已安装 Docker 和 Docker Compose
2. 配置环境变量：
   ```bash
   cp deploy/.env.example deploy/.env
   # 编辑 deploy/.env 文件
   ```
3. 启动所有服务：
   ```bash
   cd deploy
   docker-compose up -d
   ```
4. 访问前端：`http://localhost`
5. 访问后端 API：`http://localhost:8000`

**服务列表**：
- **Frontend**: `http://localhost` (Nginx)
- **Backend API**: `http://localhost:8000`
- **MySQL**: `localhost:3306`
- **Milvus**: `localhost:19530`
- **Elasticsearch**: `localhost:9200`
- **Redis**: `localhost:6379`
- **Adminer** (数据库管理): `http://localhost:8080`

---

## 安装方式

### 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| Python | 3.8+ | 3.11+ |
| Node.js | 16+ | 20+ |
| Docker | 20.10+ | 24.0+ |
| Docker Compose | 2.0+ | 2.20+ |
| 内存 | 8GB | 16GB+ |
| 存储 | 20GB | 50GB+ |

### 依赖安装

#### Python 依赖
```bash
pip install -r backend/requirements.txt
```

**主要依赖**：
- `fastapi` - Web 框架
- `uvicorn` - ASGI 服务器
- `langchain` - LLM 应用框架
- `pymilvus` - Milvus 客户端
- `elasticsearch` - Elasticsearch 客户端
- `pymysql` - MySQL 客户端
- `redis` - Redis 客户端
- `openai` - OpenAI API 客户端
- `pydantic` - 数据验证

#### 前端依赖（可选，使用纯 HTML/JS 无需安装）
```bash
cd frontend
npm install
npm run build
```

---

## 配置指南

### 环境变量说明

创建 `.env` 文件并配置以下变量：

#### 必需配置
```bash
# OpenAI API Key（必需，用于 LLM 功能）
OPENAI_API_KEY=sk-your-key

# 或使用 Azure OpenAI
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
```

#### 数据库配置
```bash
# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=rag_user
MYSQL_PASSWORD=rag_password
MYSQL_DATABASE=medical_rag

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530

# Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
```

#### 模型配置
```bash
# Embedding 模型
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DIMENSION=1024

# Reranker 模型
RERANKER_MODEL=BAAI/bge-reranker-large
```

### 数据目录结构
```
data/
├── uploads/        # 上传的原始文件
├── processed/      # 处理后的数据
├── cache/          # 缓存文件
└── models/         # 本地模型文件
```

---

## API 文档

### 基础信息
- **Base URL**: `http://localhost:8000/api/v1`
- **认证方式**: API Key（可选）
- **响应格式**: JSON

### 端点列表

#### 1. 查询搜索
**POST** `/query/search`

**请求体**：
```json
{
  "query": "患者张三在2023年5月的糖尿病就诊记录",
  "patient_id": "P00001",
  "top_k": 10,
  "enable_time_align": true
}
```

**响应**：
```json
{
  "query": "患者张三在2023年5月的糖尿病就诊记录",
  "query_info": {
    "processed_query": "患者张三 2023年5月 糖尿病 就诊记录",
    "intent": "search_by_patient"
  },
  "results": [
    {
      "document": {
        "record_id": "P00001_REC_001",
        "patient_id": "P00001",
        "title": "门诊病历",
        "content": "...",
        "department": "内分泌科",
        "visit_time": "2023-05-10T09:00:00"
      },
      "score": 0.95,
      "source": "hybrid_search"
    }
  ],
  "total": 5,
  "time_ms": 1250
}
```

#### 2. 查询建议
**GET** `/query/suggest?query=糖尿病`

**响应**：
```json
{
  "suggestions": [
    {"text": "糖尿病 在2023年1月", "score": 0.9},
    {"text": "糖尿病 的诊断记录", "score": 0.85}
  ]
}
```

#### 3. 获取患者信息
**GET** `/patient/{patient_id}`

**响应**：
```json
{
  "patient": {
    "patient_id": "P00001",
    "name": "张三",
    "gender": "Male",
    "age": 45
  },
  "timeline": [
    {
      "date": "2023-05-10T09:00:00",
      "type": "门诊病历",
      "department": "内分泌科"
    }
  ],
  "entities": {
    "diseases": [{"name": "糖尿病"}],
    "medications": [{"name": "二甲双胍"}]
  }
}
```

#### 4. 生成摘要
**POST** `/summary/generate`

**请求体**：
```json
{
  "patient_id": "P00001",
  "summary_type": "transfer",
  "include_sections": [
    "chief_complaint",
    "history",
    "examination",
    "diagnosis",
    "treatment"
  ],
  "time_window_days": 30
}
```

**响应**：
```json
{
  "summary_id": "SUM_P00001_001",
  "patient_id": "P00001",
  "summary_type": "transfer",
  "sections": {
    "chief_complaint": {
      "title": "主诉",
      "text": "患者因血糖升高伴多饮、多尿3年入院"
    },
    "diagnosis": {
      "title": "诊断",
      "text": "1. 2型糖尿病\n2. 糖尿病肾病"
    }
  },
  "entities": {
    "diseases": [{"name": "2型糖尿病"}],
    "medications": [{"name": "二甲双胍"}]
  },
  "metadata": {
    "generated_at": "2024-01-10T10:30:00",
    "model": "gpt-4o",
    "processing_time_ms": 1250
  }
}
```

---

## 前端使用

### 首页（查询界面）

**访问地址**：`http://localhost:8000/`

**功能**：
1. **智能检索**：在搜索框输入自然语言查询
   - 示例：`患者张三在2023年5月的糖尿病就诊记录`
   - 示例：`李四的高血压用药情况`
   
2. **搜索选项**：
   - 患者 ID（可选）：缩小检索范围
   - 返回结果数量：1-50
   - 时间语义对齐：启用/禁用时间理解功能

3. **检索结果**：
   - 显示相关度评分
   - 高亮显示匹配内容
   - 时间对齐分数（如果启用）
   - 操作按钮：查看患者详情、生成摘要

### 患者详情页

**访问地址**：`http://localhost:8000/patient.html?id=P00001`

**功能**：
1. **患者信息**：姓名、性别、年龄等
2. **时间轴**：按时间顺序展示就诊历史
3. **就诊记录**：详细的病历列表
4. **关键实体**：疾病、症状、药物等
5. **摘要**：已生成的摘要列表

### 摘要生成页

**访问地址**：`http://localhost:8000/summary.html?patient_id=P00001`

**功能**：
1. **输入患者 ID**
2. **选择摘要类型**：
   - 转院摘要
   - 出院小结
   - 入院记录
   - 病程记录
3. **选择包含章节**：主诉、现病史、体格检查等
4. **设置时间窗口**：仅包含最近 N 天的数据
5. **生成摘要**：点击按钮，等待 AI 生成
6. **查看结果**：结构化的摘要内容，可打印或导出

---

## Docker 部署

### 快速部署

1. **克隆项目**：
   ```bash
   git clone <repo-url>
   cd medical-rag-system
   ```

2. **配置环境**：
   ```bash
   cd deploy
   cp .env.example .env
   # 编辑 .env 文件，填入 API Key 等配置
   ```

3. **启动服务**：
   ```bash
   docker-compose up -d
   ```

4. **查看日志**：
   ```bash
   docker-compose logs -f
   ```

5. **停止服务**：
   ```bash
   docker-compose down
   ```

### 服务管理

#### 查看服务状态
```bash
docker-compose ps
```

#### 查看特定服务日志
```bash
docker-compose logs -f backend
docker-compose logs -f mysql
```

#### 重启服务
```bash
docker-compose restart backend
```

#### 停止并删除容器
```bash
docker-compose down -v  # -v 会删除数据卷
```

### 数据持久化

Docker Compose 配置了以下数据卷：
- `mysql_data`: MySQL 数据
- `milvus_data`: Milvus 向量数据
- `elasticsearch_data`: Elasticsearch 索引
- `redis_data`: Redis 缓存

**备份数据**：
```bash
# 备份 MySQL
docker-compose exec mysql mysqldump -u root -p medical_rag > backup.sql

# 备份数据卷
docker run --rm -v medical-rag_mysql_data:/data -v $(pwd):/backup ubuntu tar czf /backup/mysql_backup.tar.gz /data
```

---

## 故障排查

### 常见问题

#### 1. 后端无法启动

**症状**：运行 `python demo_server_simple.py` 报错

**解决方案**：
- 检查 Python 版本（需要 3.8+）
- 检查端口是否被占用：`netstat -an | grep 8000`
- 尝试更换端口：修改 `demo_server_simple.py` 中的 `port=8000`

#### 2. 前端无法访问

**症状**：浏览器显示"无法访问此网站"

**解决方案**：
- 确保后端已启动
- 检查浏览器控制台是否有错误
- 尝试直接访问 API：`http://localhost:8000/api/health`

#### 3. Docker 服务启动失败

**症状**：`docker-compose up` 报错

**解决方案**：
- 检查 Docker 是否运行：`docker ps`
- 检查端口占用：确保 80、3306、8000 等端口未被占用
- 查看日志：`docker-compose logs`
- 清理并重启：
  ```bash
  docker-compose down -v
  docker system prune -a
  docker-compose up -d
  ```

#### 4. LLM API 调用失败

**症状**：摘要生成失败，报错"OpenAI API error"

**解决方案**：
- 检查 `OPENAI_API_KEY` 是否正确
- 检查网络连接（是否需要代理）
- 检查 API 额度是否充足
- 尝试使用模拟模式（Demo 服务器默认使用模拟数据）

#### 5. 数据库连接失败

**症状**：Backend 无法连接到 MySQL/Redis/Milvus

**解决方案**：
- 检查数据库服务是否运行：`docker-compose ps`
- 检查连接配置（host、port、password）
- 检查防火墙设置
- 查看数据库日志：`docker-compose logs mysql`

### 日志文件

- **Backend 日志**：`logs/app.log`
- **Docker 日志**：`docker-compose logs -f`
- **Nginx 日志**：`deploy/nginx/logs/`

### 获取帮助

如遇其他问题，请：
1. 查看项目 GitHub Issues
2. 查看日志文件
3. 联系项目维护者

---

## 附录

### A. 模拟数据说明

Demo 服务器会自动生成 20 个模拟患者和 60 条就诊记录，包含：
- 患者 ID：P00001 - P00020
- 疾病：糖尿病、高血压、冠心病等
- 科室：心内科、内分泌科、神经内科等

**测试查询示例**：
- `P00001 的就诊记录`
- `糖尿病 患者的用药情况`
- `2024年1月 高血压 就诊记录`

### B. API 速率限制

- 默认限制：60 次/分钟
- 可在 `.env` 中修改 `RATE_LIMIT_PER_MINUTE`

### C. 安全建议

**生产环境部署前**：
1. 修改所有默认密码
2. 启用 HTTPS（配置 SSL 证书）
3. 配置防火墙规则
4. 启用 API 认证
5. 定期备份数据
6. 更新依赖包（安全补丁）

---

**文档版本**：1.0.0  
**最后更新**：2024-01-10  
**作者**：Medical RAG Team
