# 医疗RAG系统 - 快速启动指南

> 面向转院场景的关键信息智能检索系统  
> **项目一**：基于 RAG（检索增强生成）架构的医疗信息系统

## 项目概述

本项目是一个完整的工程化系统，实现了：
- **智能检索**：基于 RAG 架构，结合向量检索（Milvus）和关键词检索（Elasticsearch）
- **时间语义对齐**：自研四层架构时间对齐模块，精准解析医疗记录中的复杂时间表达
- **结构化输出**：基于 LLM 生成标准化的转院摘要，输出 JSON 格式
- **完整前后端**：FastAPI 后端 + React 前端，支持 Docker Compose 一键部署

## 项目结构

```
medical-rag-system/
├── backend/                   # 后端（FastAPI）
│   ├── main.py                 # FastAPI 入口
│   ├── demo_server_simple.py  # 简化版演示服务（无需依赖）
│   ├── requirements.txt        # Python 依赖
│   ├── config.py              # 配置管理
│   ├── api/                   # API 路由
│   │   ├── routes_query.py    # 查询接口
│   │   ├── routes_patient.py # 患者信息接口
│   │   └── routes_summary.py # 摘要生成接口
│   ├── rag/                   # RAG 检索层
│   │   ├── query_rewriter.py # Query 改写
│   │   ├── hybrid_search.py  # 混合检索
│   │   ├── time_aligner.py   # 时间语义对齐（核心）
│   │   └── context_compressor.py # 上下文压缩
│   ├── llm/                   # LLM 生成层
│   │   ├── ner_extractor.py  # NER 抽取
│   │   ├── summary_generator.py # 摘要生成
│   │   └── output_validator.py # 输出校验
│   └── data/                  # 数据客户端
│       ├── milvus_client.py  # Milvus 客户端
│       ├── es_client.py      # Elasticsearch 客户端
│       ├── mysql_client.py   # MySQL 客户端
│       ├── redis_client.py   # Redis 客户端
│       └── in_memory_store.py # 内存存储（演示模式）
├── frontend/                  # 前端（React + TypeScript）
│   └── （待实现）
├── data/                      # 数据目录
│   ├── sample_records/        # 样本病历数据
│   ├── knowledge_base/        # 医学知识库
│   └── icd_mapping/         # ICD 编码映射
├── deploy/                    # 部署配置
│   └── docker-compose.yml    # 容器编排（待创建）
├── tests/                     # 测试
├── README.md
├── QUICKSTART.md             # 本文件
└── PROJECT_SUMMARY.md        # 项目总结（待创建）
```

## 快速启动（三种模式）

### 模式一：简化版演示（推荐，无需任何依赖）

**适用场景**：快速演示系统功能、API 接口测试、前端开发调试

**特点**：
- 使用 Python 内置模块（`http.server`）
- 无需安装任何外部依赖
- 使用内存存储的模拟数据（10 名患者，10 条病历记录）
- 可以直接运行

**启动步骤**：

```bash
# 1. 进入后端目录
cd medical-rag-system/backend

# 2. 运行简化版演示服务
python demo_server_simple.py

# 3. 访问 API 接口
# - 首页：http://localhost:8000
# - 搜索患者：http://localhost:8000/api/patient/search?keyword=P00001
# - 获取患者信息：http://localhost:8000/api/patient/P00001
# - 生成转院摘要：http://localhost:8000/api/summary/P00001
```

**可用 API 接口**：

| 接口 | 方法 | 说明 |
|---|---|---|
| `/` | GET | 首页（服务状态） |
| `/api/patient/search?keyword=xxx` | GET | 搜索患者 |
| `/api/patient/{patient_id}` | GET | 获取患者信息 |
| `/api/query/search` | POST | 检索查询 |
| `/api/summary/{patient_id}` | GET | 生成转院摘要 |

**示例请求**：

```bash
# 搜索患者
curl "http://localhost:8000/api/patient/search?keyword=P00001"

# 获取患者信息
curl "http://localhost:8000/api/patient/P00001"

# 检索查询
curl -X POST "http://localhost:8000/api/query/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "胸痛患者 P00001 的病历", "patient_id": "P00001"}'

# 生成转院摘要
curl "http://localhost:8000/api/summary/P00001"
```

---

### 模式二：完整后端服务（需要安装依赖）

**适用场景**：完整功能测试、生产环境部署

**特点**：
- 使用 FastAPI 框架
- 需要安装 Python 依赖（`requirements-core.txt`）
- 支持使用真实数据库（MySQL、Milvus、Elasticsearch）
- 支持使用 LLM API（OpenAI API）

**启动步骤**：

```bash
# 1. 进入后端目录
cd medical-rag-system/backend

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements-core.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 OpenAI API Key

# 5. 运行后端服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 6. 访问 API 文档
# http://localhost:8000/docs
```

---

### 模式三：Docker Compose 一键部署（完整系统）

**适用场景**：生产环境部署、团队协作开发

**特点**：
- 一键启动所有服务（FastAPI、React、MySQL、Milvus、Elasticsearch、Redis）
- 数据持久化
- 服务编排和监控

**启动步骤**：

```bash
# 1. 进入部署目录
cd medical-rag-system/deploy

# 2. 启动所有服务
docker-compose up -d

# 3. 访问应用
# 前端：http://localhost:3000
# 后端 API 文档：http://localhost:8000/docs

# 4. 停止所有服务
docker-compose down
```

---

## 核心功能演示

### 1. Query 理解与改写

**接口**：`POST /api/query/rewrite`

**示例请求**：
```json
{
  "query": "心肌梗死患者 P00001 的用药记录"
}
```

**预期响应**：
```json
{
  "original_query": "心肌梗死患者 P00001 的用药记录",
  "rewritten_query": "心肌梗死 急性心肌梗死 I21.0 患者 P00001 用药记录",
  "intent": "按疾病查",
  "entities": [
    {"name": "心肌梗死", "standard_name": "急性心肌梗死", "type": "disease"}
  ],
  "time_expressions": []
}
```

---

### 2. 混合检索

**接口**：`POST /api/query/search`

**示例请求**：
```json
{
  "query": "胸痛患者 P00001 的病历摘要",
  "patient_id": "P00001",
  "top_k": 20
}
```

**预期响应**：
```json
{
  "query": "胸痛患者 P00001 的病历摘要",
  "rewritten_query": {...},
  "results": [
    {
      "record_id": "P00001_REC_001",
      "patient_id": "P00001",
      "content": "入院记录\n患者 P00001，因"胸痛3天"...",
      "score": 0.95,
      "source": "mock_search"
    }
  ],
  "total": 1,
  "time_ms": 123.45,
  "trace_id": "trace_1234567890"
}
```

---

### 3. 时间语义对齐（核心技术亮点）

**模块**：`backend/rag/time_aligner.py`

**功能**：
- Layer 1: 时间实体抽取（正则 + 规则 + NLP）
- Layer 2: 时间归一化（相对时间转绝对时间）
- Layer 3: 时序排序 + 因果校验
- Layer 4: Cross-Encoder 精排

**测试方法**：
```bash
# 运行时间对齐模块测试
cd medical-rag-system/backend
python -c "
from rag.time_aligner import time_aligner

# 模拟查询
query = '患者 P00001 在 2024年1月15日 做的 CT 检查结果'

# 模拟患者时间线
patient_timeline = {
  'events': [
    {'event_type': '入院', 'date': '2024-01-10'},
    {'event_type': '检查', 'date': '2024-01-15', 'description': 'CT 检查'}
  ]
}

# 执行时间对齐
result = time_aligner.align_time(query, patient_timeline)
print(result)
"
```

---

### 4. 转院摘要生成

**接口**：`GET /api/summary/{patient_id}`

**示例请求**：
```bash
curl "http://localhost:8000/api/summary/P00001"
```

**预期响应**：
```json
{
  "patient_id": "P00001",
  "summary": {
    "patient_summary": {
      "chief_complaint": "胸痛3天",
      "diagnosis": [
        {"name": "急性心肌梗死", "icd_code": "I21.0", "confidence": 0.95}
      ],
      "key_events": [...],
      "medications": [...],
      "examinations": [...],
      "transfer_recommendation": "建议转心血管内科CCU进一步治疗"
    }
  },
  "ner_entities": {...},
  "confidence_scores": {...},
  "retrieved_docs_count": 5,
  "trace_id": "trace_1234567890",
  "time_ms": 456.78
}
```

---

## 技术架构

### 系统架构（四层设计）

```
┌─────────────────────────────────────────────────────────┐
│  Layer 4: 应用层 Application                     │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ │
│  │转院申请│ │病历摘要│ │信息面板│ │审批流程│ │
│  └────────┘ └────────┘ └────────┘ └────────┘ │
├─────────────────────────────────────────────────────────┤
│  Layer 3: LLM生成层 Generation                   │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ │
│  │NER抽取 │ │摘要生成 │ │实体链接 │ │质量评估 │ │
│  └────────┘ └────────┘ └────────┘ └────────┘ │
├─────────────────────────────────────────────────────────┤
│  Layer 2: RAG检索层 Retrieval                    │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ │
│  │Query │ │混合  │ │重排  │ │时间  │ │上下文│ │
│  │改写  │ │检索  │ │模块  │ │对齐  │ │压缩  │ │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ │
├─────────────────────────────────────────────────────────┤
│  Layer 1: 数据层 Data                            │
│  ┌──────┐ ┌────────┐ ┌──────┐ ┌──────┐        │
│  │HIS/  │ │医学知识 │ │向量库 │ │时序  │        │
│  │EMR   │ │图谱    │ │Milvus│ │数据  │        │
│  └──────┘ └────────┘ └──────┘ └──────┘        │
└─────────────────────────────────────────────────────────┘
```

### 技术栈

| 组件 | 技术选型 | 用途 |
|---|---|---|
| 后端框架 | FastAPI | REST API 接口 |
| RAG 编排 | LangChain | RAG 链路编排 |
| 向量数据库 | Milvus | 向量存储与检索 |
| 关键词检索 | Elasticsearch / BM25 | 精确匹配检索 |
| 嵌入模型 | BGE-M3 | 中文文本向量化 |
| 重排序模型 | bge-reranker | 精排 Top-K 结果 |
| 大模型 | OpenAI API (GPT-4o) | LLM 推理 |
| 关系数据库 | MySQL | 结构化元数据存储 |
| 缓存 | Redis | 热门查询缓存 |
| 前端 | React + TypeScript | Web 交互界面 |
| 状态管理 | Zustand | 前端状态管理 |
| 容器化 | Docker Compose | 一键部署 |

---

## 下一步计划

### 已完成

- [x] 项目目录结构创建
- [x] 后端基础框架搭建（FastAPI）
- [x] 数据层实现（样本数据生成、数据库初始化脚本）
- [x] RAG 检索层实现（Query 改写、混合检索、时间对齐）
- [x] LLM 生成层实现（NER 抽取、摘要生成、输出校验）
- [x] 应用层与 API 接口实现
- [x] 简化版演示服务创建（`demo_server_simple.py`）

### 待完成

- [ ] 前端实现（React + TypeScript）
- [ ] Docker Compose 一键部署配置
- [ ] 系统测试与评估
- [ ] 完整文档编写（使用说明、API 文档、项目总结）

---

## 联系方式

如有问题，请参考：
- **README.md**：项目概述和快速开始指南
- **PROJECT_SUMMARY.md**：项目总结（待创建）
- **API 文档**：启动后端服务后访问 http://localhost:8000/docs

---

**最后更新时间**：2026-06-29
