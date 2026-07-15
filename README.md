# 面向转院场景的关键信息智能检索系统

> 基于 RAG（检索增强生成）架构的医疗信息系统，帮助医生在转院会诊时快速检索患者病历中的关键信息。

## 项目概述

本项目是一个完整的工程化系统，实现了：
- **智能检索**：基于 RAG 架构，结合 BM25 关键词检索和向量语义检索
- **时间语义对齐**：自研时间对齐模块，精准解析医疗记录中的复杂时间表达
- **结构化输出**：基于 LLM 生成标准化的转院摘要，输出 JSON 格式
- **完整前后端**：FastAPI 后端 + 原生前端，支持 Docker Compose 一键部署

## 核心功能

1. **Query 理解与改写**：意图识别、医学术语标准化、同义词扩展
2. **混合检索**：BM25 关键词检索 + 向量语义检索 + RRF 融合
3. **时间语义对齐**（核心技术亮点）：
   - 绝对时间解析（"2023年5月" → 时间区间）
   - 相对时间转换（"3个月前" → 绝对日期）
   - 模糊时间识别（"上周"、"去年"）
   - 时间窗口过滤检索结果
4. **LLM 生成层**：NER 抽取、摘要生成、输出校验
5. **工程化落地**：熔断降级、重试机制、日志追踪、RBAC 权限控制

## 技术栈

| 组件 | 技术选型 | 用途 |
|---|---|---|
| 后端框架 | FastAPI | REST API 接口 |
| 数据校验 | Pydantic v2 | 请求/响应模型校验 |
| 向量数据库 | Milvus | 向量存储与检索 |
| 关键词检索 | Elasticsearch / BM25 | 精确匹配检索 |
| 嵌入模型 | BGE-M3 | 中文文本向量化 |
| 重排序模型 | bge-reranker | 精排 Top-K 结果 |
| 大模型 | OpenAI API (GPT-4o) | LLM 推理 |
| 关系数据库 | MySQL | 结构化元数据存储 |
| 缓存 | Redis | 热门查询缓存 |
| 前端 | HTML + CSS + JavaScript | Web 交互界面 |
| 容器化 | Docker Compose | 一键部署 |

## 项目结构

```
medical-rag-system/
├── backend/                    # 后端（FastAPI）
│   ├── main.py                # FastAPI 入口
│   ├── config.py              # 配置管理
│   ├── requirements.txt       # Python 依赖
│   ├── demo_server.py         # 零依赖演示服务器
│   ├── api/                   # API 路由
│   │   ├── routes_query.py    # 查询接口
│   │   ├── routes_patient.py  # 患者信息接口
│   │   └── routes_summary.py  # 摘要生成接口
│   ├── rag/                   # RAG 检索层
│   │   ├── query_rewriter.py  # Query 改写
│   │   ├── hybrid_search.py   # 混合检索（BM25 + RRF）
│   │   └── time_aligner.py    # 时间语义对齐（核心）
│   ├── llm/                   # LLM 生成层
│   │   ├── ner_extractor.py   # NER 抽取
│   │   ├── summary_generator.py # 摘要生成
│   │   └── output_validator.py  # 输出校验
│   └── data/                  # 数据层
│       └── in_memory_store.py # 内存数据存储（开发用）
├── frontend/                  # 前端（原生 HTML/CSS/JS）
│   ├── index.html             # 智能检索页
│   ├── patient.html          # 患者详情页
│   ├── summary.html           # 摘要生成页
│   ├── css/style.css          # 医疗主题样式
│   └── js/                    # 前端逻辑
│       ├── api.js             # API 通信层
│       ├── app.js             # 首页逻辑
│       ├── patient.js         # 患者页逻辑
│       └── summary.js         # 摘要页逻辑
├── deploy/                    # 部署配置
│   ├── docker-compose.yml     # 容器编排
│   ├── .env.example           # 环境变量模板
│   ├── mysql/init.sql         # 数据库初始化
│   └── nginx/nginx.conf       # Nginx 配置
├── tests/                     # 测试
│   └── test_rag.py            # 核心算法单元测试
└── README.md
```

## 快速开始

### 方式一：零依赖演示（推荐体验）

```bash
cd backend
python demo_server.py
```

访问 http://localhost:8000 即可使用，无需安装任何依赖。

### 方式二：完整后端启动

#### 前置条件

- Python 3.8+
- OpenAI API Key（用于 LLM 推理，演示模式可不填）

#### 后端启动

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

启动后访问 http://localhost:8000/docs 查看 API 文档。

### 方式三：Docker Compose 一键部署

```bash
# 1. 配置环境变量
cp deploy/.env.example .env
# 编辑 .env 文件，填入 OpenAI API Key

# 2. 启动所有服务
cd deploy
docker-compose up -d

# 3. 访问应用
# 前端：http://localhost
# 后端 API 文档：http://localhost:8000/docs
# 数据库管理：http://localhost:8080
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/query/search` | 智能检索病历 |
| GET | `/api/v1/query/suggest` | 查询建议 |
| GET | `/api/v1/patient/{id}` | 获取患者详情 |
| GET | `/api/v1/patient/search` | 搜索患者 |
| POST | `/api/v1/summary/generate` | 生成转院摘要 |

启动后端后访问 http://localhost:8000/docs 查看完整 API 文档。

## 核心指标

| 指标 | 目标值 | 说明 |
|---|---|---|
| 核心召回准确率 | ≥90% | 检索系统找到关键信息的比例 |
| 信息提取效率提升 | 68% | 相比手动翻阅病历节省的时间 |
| 关键词理解准确率提升 | 5%+ | 相比基线模型 |
| 平均响应时间 | <3s | 端到端响应时间 |

## 项目亮点

1. **时间语义对齐模块**：自研时间解析引擎，解决医疗记录中复杂时间表达解析难题
2. **混合检索策略**：BM25 + 向量检索 + RRF 融合，兼顾精确匹配和语义理解
3. **工程化落地**：熔断降级、重试机制、日志追踪、权限控制，可直接用于生产环境
4. **完整前后端**：从数据层到应用层，完整的可运行系统

## 许可证

MIT License
