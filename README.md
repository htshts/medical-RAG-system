# 面向转院场景的关键信息智能检索系统

> 基于 RAG（检索增强生成）架构的医疗信息系统，帮助医生在转院会诊时快速检索患者病历中的关键信息。

## 项目概述

本项目是一个完整的工程化系统，实现了：
- **智能检索**：基于 RAG 架构，结合向量检索（Milvus）和关键词检索（Elasticsearch）
- **时间语义对齐**：自研四层架构时间对齐模块，精准解析医疗记录中的复杂时间表达
- **结构化输出**：基于 LLM 生成标准化的转院摘要，输出 JSON 格式
- **完整前后端**：FastAPI 后端 + React 前端，支持 Docker Compose 一键部署

## 核心功能

1. **Query 理解与改写**：意图识别、医学术语标准化、同义词扩展
2. **混合检索**：BM25 关键词检索 + 向量语义检索 + RRF 融合
3. **时间语义对齐**（核心技术亮点）：
   - Layer 1: 时间实体抽取（正则 + 规则 + NLP）
   - Layer 2: 时间归一化（相对时间转绝对时间）
   - Layer 3: 时序排序 + 因果校验
   - Layer 4: Cross-Encoder 精排
4. **LLM 生成层**：NER 抽取、摘要生成、实体链接、质量评估
5. **工程化落地**：熔断降级、重试机制、日志追踪、RBAC 权限控制

## 技术栈

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

## 项目结构

```
medical-rag-system/
├── backend/                    # 后端（FastAPI）
│   ├── main.py                # FastAPI 入口
│   ├── requirements.txt       # Python 依赖
│   ├── config.py              # 配置管理
│   ├── api/                  # API 路由
│   │   ├── routes_query.py   # 查询接口
│   │   ├── routes_patient.py # 患者信息接口
│   │   └── routes_summary.py # 摘要生成接口
│   ├── rag/                  # RAG 检索层
│   │   ├── query_rewriter.py # Query 改写
│   │   ├── hybrid_search.py  # 混合检索
│   │   ├── time_aligner.py   # 时间语义对齐（核心）
│   │   ├── reranker.py       # Cross-Encoder 精排
│   │   └── context_compressor.py # 上下文压缩
│   ├── llm/                  # LLM 生成层
│   │   ├── ner_extractor.py  # NER 抽取
│   │   ├── summary_generator.py # 摘要生成
│   │   └── output_validator.py # 输出校验
│   └── data/                 # 数据客户端
│       ├── milvus_client.py  # Milvus 客户端
│       ├── es_client.py      # Elasticsearch 客户端
│       ├── mysql_client.py   # MySQL 客户端
│       └── redis_client.py   # Redis 客户端
├── frontend/                  # 前端（React + TypeScript）
│   ├── src/
│   │   ├── components/       # React 组件
│   │   ├── pages/            # 页面
│   │   ├── store/            # Zustand 状态管理
│   │   └── api/             # API 请求
│   └── package.json
├── data/                      # 数据目录
│   ├── sample_records/        # 样本病历数据
│   ├── knowledge_base/        # 医学知识库
│   └── icd_mapping/         # ICD 编码映射
├── deploy/                    # 部署配置
│   ├── docker-compose.yml    # 容器编排
│   ├── Dockerfile.backend     # 后端镜像
│   └── Dockerfile.frontend   # 前端镜像
├── tests/                     # 测试
│   ├── test_retrieval.py     # 检索模块测试
│   ├── test_time_aligner.py  # 时间对齐测试
│   └── test_e2e.py          # 端到端测试
├── README.md
├── USAGE.md                  # 使用说明
└── PROJECT_SUMMARY.md       # 项目总结
```

## 快速开始

### 前置条件

- Docker & Docker Compose 已安装
- OpenAI API Key（用于 LLM 推理）

### 一键启动

```bash
# 1. 克隆项目
git clone <repo-url>
cd medical-rag-system

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 OpenAI API Key

# 3. 启动所有服务
cd deploy
docker-compose up -d

# 4. 访问应用
# 前端：http://localhost:3000
# 后端 API 文档：http://localhost:8000/docs
```

### 手动启动（开发模式）

#### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端

```bash
cd frontend
npm install
npm run dev
```

## 核心指标

| 指标 | 目标值 | 说明 |
|---|---|---|
| 核心召回准确率 | ≥90% | 检索系统找到关键信息的比例 |
| 信息提取效率提升 | 68% | 相比手动翻阅病历节省的时间 |
| 关键词理解准确率提升 | 5%+ | 相比基线模型 |
| 平均响应时间 | <3s | 端到端响应时间 |

## 项目亮点

1. **时间语义对齐模块**：自研四层架构，解决医疗记录中复杂时间表达解析难题
2. **混合检索策略**：BM25 + 向量检索 + RRF 融合，兼顾精确匹配和语义理解
3. **工程化落地**：熔断降级、重试机制、日志追踪、权限控制，可直接用于生产环境
4. **完整前后端**：从数据层到应用层，完整的可运行系统

## 文档

- **使用说明**：参见 [USAGE.md](./USAGE.md)
- **API 文档**：启动后端后访问 http://localhost:8000/docs
- **项目总结**：参见 [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)

## 许可证

MIT License
