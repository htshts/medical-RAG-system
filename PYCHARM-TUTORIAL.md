# 用 PyCharm 从零搭建智能病历检索系统 — 实操教学

> **IDE**：PyCharm Professional 2024+（Community 亦可，部分功能受限）  
> **预计耗时**：6-8 小时（可分多次完成）  
> **适用对象**：有 Python 基础，想用 PyCharm 完整走一遍项目开发流程

---

## 目录

- [阶段一：需求分析与技术选型](#阶段一需求分析与技术选型)
- [阶段二：PyCharm 项目初始化](#阶段二pycharm-项目初始化)
- [阶段三：数据库与数据层开发](#阶段三数据库与数据层开发)
- [阶段四：后端 API 开发](#阶段四后端-api-开发)
- [阶段五：核心算法实现](#阶段五核心算法实现)
- [阶段六：前端界面开发](#阶段六前端界面开发)
- [阶段七：前后端联调测试](#阶段七前后端联调测试)
- [阶段八：Docker 容器化部署](#阶段八docker-容器化部署)

---

## 阶段一：需求分析与技术选型

### 1.1 需求分析

**项目背景**：医院转院场景中，医生需要快速了解患者既往病史，手工翻阅病历耗时且容易遗漏关键信息。

**核心需求**：

| 编号 | 需求 | 优先级 |
|------|------|--------|
| R1 | 自然语言检索病历 | P0 |
| R2 | 理解复杂时间表达（"3个月前"、"上周"） | P0 |
| R3 | 自动生成结构化转院摘要 | P0 |
| R4 | 患者时间轴展示 | P1 |
| R5 | 关键实体高亮（疾病/药物/症状） | P1 |

### 1.2 技术选型

| 层级 | 选型 | 选型理由 |
|------|------|----------|
| 后端框架 | FastAPI | 异步高性能、自动生成 API 文档、类型安全 |
| 数据校验 | Pydantic v2 | 与 FastAPI 深度集成、性能优秀 |
| 向量检索 | Milvus | 开源、专为向量检索优化 |
| 全文检索 | Elasticsearch | BM25 算法、中文分词支持好 |
| 缓存 | Redis | 查询结果缓存、会话管理 |
| 数据库 | MySQL 8.0 | 成度成熟、事务支持、团队熟悉 |
| 前端 | 原生 HTML/CSS/JS | 无构建步骤、适合教学演示 |
| 部署 | Docker Compose | 一键编排多服务、环境隔离 |
| IDE | PyCharm Professional | 智能补全、数据库工具、HTTP Client、Docker 集成 |

### 1.3 系统架构设计

```
┌─────────────────────────────────────────────────┐
│ 浏览器（前端 HTML/CSS/JS）                      │
└──────────────────────┬──────────────────────────┘
                       │ HTTP
┌──────────────────────▼──────────────────────────┐
│ FastAPI 后端 (:8000)                            │
│  ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │ 患者API  │ │ 检索API  │ │ 摘要生成API   │  │
│  └────┬─────┘ └────┬─────┘ └───────┬───────┘  │
│       │            │               │            │
│  ┌────▼────────────▼───────────────▼───────┐  │
│  │         RAG 核心引擎                    │  │
│  │  Query改写 → 时间对齐 → 混合检索 → LLM  │  │
│  └────────────────────────────────────────┘  │
└──────┬──────────┬──────────┬──────────┬───────┘
       │          │          │          │
   ┌───▼──┐  ┌───▼───┐  ┌───▼──┐  ┌───▼───┐
   │MySQL │  │Milvus │  │ ES   │  │ Redis │
   └──────┘  └───────┘  └──────┘  └───────┘
```

---

## 阶段二：PyCharm 项目初始化

### Step 1：安装 PyCharm

1. 访问 https://www.jetbrains.com/pycharm/download/
2. 下载 **Professional** 版（有 30 天试用，或用学生邮箱免费）
3. 安装时勾选：
   - ✅ Add launchers dir to the PATH
   - ✅ Add "Open Folder as Project"
   - ✅ .py 关联

> **Community 版差异**：无 Database 工具、无 HTTP Client、无 Docker 集成。本教程会标注哪些步骤需要 Professional。

### Step 2：在 PyCharm 中创建项目

1. 启动 PyCharm → **New Project**
2. 填写配置：

```
Location:    C:\Users\你的用户名\Desktop\medical-rag-system
Interpreter: New environment using Virtualenv
Base interpreter: Python 3.11 (或你安装的版本)
Location:    C:\Users\你的用户名\Desktop\medical-rag-system\venv
```

3. 点击 **Create**

PyCharm 会自动：
- 创建项目目录
- 创建虚拟环境 `venv/`
- 生成 `.idea/` 配置目录
- 打开项目窗口

> 💡 **PyCharm 技巧**：左侧 **Project** 面板可看到文件树。按 `Alt+1` 可快速切换面板。

### Step 3：创建项目目录结构

在 PyCharm 的 **Project** 面板中，右键项目根目录 → **New → Directory**，依次创建：

```
medical-rag-system/
├── backend/
│   ├── api/           # API 路由
│   ├── rag/           # RAG 检索引擎
│   ├── llm/           # LLM 生成模块
│   └── data/          # 数据层
├── frontend/
│   ├── css/
│   └── js/
├── deploy/
├── tests/
└── data/
```

**操作步骤**：

1. 右键 `medical-rag-system` → New → Directory → 输入 `backend`
2. 右键 `backend` → New → Directory → 输入 `api`
3. 右键 `backend` → New → Directory → 输入 `rag`
4. 右键 `backend` → New → Directory → 输入 `llm`
5. 右键 `backend` → New → Directory → 输入 `data`
6. 同理创建 `frontend`、`frontend/css`、`frontend/js`、`deploy`、`tests`、`data`

> 💡 **快捷方式**：也可以直接在 PyCharm 底部的 **Terminal**（`Alt+F12`）中用命令创建：
> ```bash
> mkdir -p backend/api backend/rag backend/llm backend/data
> mkdir -p frontend/css frontend/js deploy tests data
> ```

### Step 4：创建 Python 包标记

Python 包目录需要 `__init__.py` 文件：

1. 右键 `backend/api` → New → Python Package（PyCharm 会自动创建 `__init__.py`）
2. 对 `backend/rag`、`backend/llm`、`backend/data` 重复此操作

> 💡 如果菜单没有 "Python Package"，选 New → File，手动创建 `__init__.py`（空文件即可）。

### Step 5：配置 Git 版本控制

1. 菜单 **VCS → Enable Version Control Integration**
2. 选择 **Git** → OK
3. 创建 `.gitignore` 文件

右键项目根目录 → New → File → 输入 `.gitignore`：

```gitignore
# Python
__pycache__/
*.py[cod]
venv/
.env

# PyCharm
.idea/

# 数据
data/uploads/
data/cache/
*.db
*.log
```

4. 按 `Ctrl+K`（Mac: `Cmd+K`）打开 Commit 窗口
5. 输入 commit message: `初始化项目结构`
6. 点击 **Commit**

### Step 6：安装项目依赖

#### 6.1 创建 requirements.txt

右键项目根目录 → New → File → `requirements.txt`：

```txt
# Web 框架
fastapi==0.109.0
uvicorn[standard]==0.27.0

# 数据校验
pydantic==2.5.3
pydantic-settings==2.1.0

# 数据库
pymysql==1.1.0
sqlalchemy==2.0.25

# 向量库
pymilvus==2.3.4

# 搜索引擎
elasticsearch==8.11.0

# 缓存
redis==5.0.1

# LLM
openai==1.6.1

# 工具
python-dotenv==1.0.0
```

#### 6.2 在 PyCharm 中安装依赖

**方法一：用 PyCharm Terminal（推荐）**

1. 按 `Alt+F12` 打开 Terminal（底部）
2. 确认提示符前有 `(venv)` — 说明虚拟环境已激活
3. 执行：

```bash
pip install -r requirements.txt
```

**方法二：用 PyCharm Settings**

1. `Ctrl+Alt+S` 打开 Settings
2. **Project: medical-rag-system → Python Interpreter**
3. 点 **+** 号，搜索包名逐个安装

> 💡 **推荐方法一**，批量安装更快。安装过程可能需要 1-3 分钟。

#### 6.3 验证安装

在 Terminal 中执行：

```bash
python -c "import fastapi; import pydantic; print('依赖安装成功！')"
```

看到 `依赖安装成功！` 即为通过。

### Step 7：创建环境变量文件

右键项目根目录 → New → File → `.env`：

```env
# 应用配置
DEBUG=True

# LLM API Key（先留空，后面用模拟模式）
OPENAI_API_KEY=

# 数据库（本地开发默认值）
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=medical_rag

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
```

> ⚠️ `.env` 已在 `.gitignore` 中，不会被提交到 Git。

### Step 8：配置 PyCharm 运行环境

1. 菜单 **Run → Edit Configurations**
2. 点 **+** → 选择 **Python**
3. 配置：

```
Name:           Medical RAG Server
Script path:    C:\...\medical-rag-system\backend\main.py
Parameters:     (留空)
Working dir:    C:\...\medical-rag-system\backend
Environment variables: (留空，会自动读 .env)
```

4. 点 OK 保存

> 💡 这样以后直接点绿色三角形 ▶ 就能启动服务器，不需要每次手动输命令。

---

## 阶段三：数据库与数据层开发

### Step 9：创建配置模块

右键 `backend` → New → Python File → `config.py`：

```python
# backend/config.py

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置 — 自动从 .env 文件加载"""

    # 应用
    APP_NAME: str = "Medical RAG System"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    # 服务器
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 数据库
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "medical_rag"

    # LLM
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"

    # 向量库
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
```

> 💡 **PyCharm 技巧**：输入 `from pydantic_settings import` 时 PyCharm 会自动补全。如果没有提示，检查 Python Interpreter 是否正确配置。

### Step 10：创建数据模型

右键 `backend` → New → Python File → `models.py`：

```python
# backend/models.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"


class RecordType(str, Enum):
    OUTPATIENT = "门诊病历"
    INPATIENT = "住院记录"


class SummaryType(str, Enum):
    TRANSFER = "transfer"
    DISCHARGE = "discharge"


# --- 请求/响应模型 ---

class PatientResponse(BaseModel):
    patient_id: str
    name: str
    gender: Gender
    age: Optional[int] = None
    phone: Optional[str] = None


class SearchQuery(BaseModel):
    query: str = Field(..., min_length=1, description="查询内容")
    patient_id: Optional[str] = None
    top_k: int = Field(10, ge=1, le=50)
    enable_time_align: bool = True


class SearchResult(BaseModel):
    document: Dict
    score: float = Field(..., ge=0, le=1)
    source: str


class SearchResponse(BaseModel):
    query: str
    query_info: Dict
    results: List[SearchResult]
    total: int
    time_ms: float


class SummaryRequest(BaseModel):
    patient_id: str
    summary_type: SummaryType = SummaryType.TRANSFER
    include_sections: List[str] = Field(
        ["chief_complaint", "history", "diagnosis", "treatment"]
    )
    time_window_days: int = 30


class SummarySection(BaseModel):
    title: str
    text: str


class SummaryResponse(BaseModel):
    summary_id: str
    patient_id: str
    summary_type: SummaryType
    sections: Dict[str, SummarySection]
    entities: Optional[Dict] = None
    metadata: Optional[Dict] = None
```

> 💡 **PyCharm 技巧**：按 `Ctrl+点击`（Mac: `Cmd+点击`）可以跳转到类/函数定义。按 `Ctrl+B` 可以查看用法。

### Step 11：实现内存数据存储

右键 `backend/data` → New → Python File → `in_memory_store.py`：

```python
# backend/data/in_memory_store.py

"""
内存数据存储 — 开发阶段使用，无需安装数据库
"""

from typing import List, Dict, Optional

patients_db: Dict[str, Dict] = {}
records_db: Dict[str, Dict] = {}
summaries_db: Dict[str, Dict] = {}


def init_mock_data():
    """初始化模拟数据"""
    mock_patients = [
        {"patient_id": "P00001", "name": "张三", "gender": "Male", "age": 45,
         "phone": "13800138001"},
        {"patient_id": "P00002", "name": "李四", "gender": "Female", "age": 52,
         "phone": "13800138002"},
        {"patient_id": "P00003", "name": "王五", "gender": "Male", "age": 38,
         "phone": "13800138003"},
    ]

    mock_records = [
        {"record_id": "P00001_REC_001", "patient_id": "P00001",
         "record_type": "门诊病历", "department": "内分泌科", "doctor": "王医生",
         "visit_time": "2023-05-10T09:00:00",
         "content": "患者张三，45岁，因糖尿病复诊。确诊糖尿病5年，使用二甲双胍0.5g tid。"
                    "空腹血糖7.5-8.5mmol/L。诊断：2型糖尿病。处理：加用恩格列净10mg qd。"},
        {"record_id": "P00001_REC_002", "patient_id": "P00001",
         "record_type": "住院记录", "department": "心内科", "doctor": "李医生",
         "visit_time": "2023-08-15T14:00:00",
         "content": "患者张三，因胸痛3天入院。3天前出现胸骨后压榨样疼痛。"
                    "既往2型糖尿病5年、高血压3年。心电图V1-V4 ST段压低。"
                    "诊断：急性非ST段抬高型心肌梗死。行冠脉造影+支架植入术。"},
        {"record_id": "P00002_REC_001", "patient_id": "P00002",
         "record_type": "门诊病历", "department": "神经内科", "doctor": "赵医生",
         "visit_time": "2023-06-20T10:30:00",
         "content": "患者李四，52岁，头晕头痛2周。既往高血压10年。"
                    "BP 155/98mmHg。诊断：原发性高血压3级。"
                    "处理：氨氯地平加量至5mg bid，加用缬沙坦80mg qd。"},
    ]

    for p in mock_patients:
        patients_db[p["patient_id"]] = p
    for r in mock_records:
        records_db[r["record_id"]] = r

    print(f"[OK] 模拟数据：{len(patients_db)}患者，{len(records_db)}条病历")


def get_patient(patient_id: str) -> Optional[Dict]:
    return patients_db.get(patient_id)


def search_patients(keyword: str, limit: int = 10) -> List[Dict]:
    results = []
    for p in patients_db.values():
        if keyword.lower() in p["name"].lower() or keyword in p["patient_id"]:
            results.append(p)
            if len(results) >= limit:
                break
    return results


def get_patient_records(patient_id: str) -> List[Dict]:
    results = [r for r in records_db.values() if r["patient_id"] == patient_id]
    results.sort(key=lambda x: x["visit_time"])
    return results


def search_records(query: str, patient_id: Optional[str] = None, top_k: int = 10) -> List[Dict]:
    """关键词检索"""
    results = []
    query_lower = query.lower()
    for record in records_db.values():
        if patient_id and record["patient_id"] != patient_id:
            continue
        if query_lower in record.get("content", "").lower():
            score = min(record["content"].lower().count(query_lower) / 10, 1.0)
            results.append({"document": record, "score": score, "source": "keyword"})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def save_summary(summary: Dict) -> str:
    summary_id = f"SUM_{summary['patient_id']}_{len(summaries_db) + 1:03d}"
    summary["summary_id"] = summary_id
    summaries_db[summary_id] = summary
    return summary_id
```

> 💡 **PyCharm 调试技巧**：在任意行号左侧点击可设置**断点**（红点），然后点 Debug 按钮（绿色虫子图标 🐛）以调试模式运行，程序会在断点处暂停，你可以查看变量值。

---

## 阶段四：后端 API 开发

### Step 12：创建 FastAPI 应用入口

右键 `backend` → New → Python File → `main.py`：

```python
# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from data.in_memory_store import init_mock_data

app = FastAPI(
    title=settings.APP_NAME,
    description="面向转院场景的关键信息智能检索系统",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    print("=" * 50)
    print(f"  {settings.APP_NAME} 启动中...")
    print("=" * 50)
    init_mock_data()
    print("  启动完成！")


@app.get("/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
def root():
    return {"app": settings.APP_NAME, "docs": "/docs"}


# 注册路由（后面会创建这些模块）
# from api.routes_patient import router as patient_router
# from api.routes_query import router as query_router
# from api.routes_summary import router as summary_router
# app.include_router(patient_router, prefix=f"{settings.API_PREFIX}/patient", tags=["患者管理"])
# app.include_router(query_router, prefix=f"{settings.API_PREFIX}/query", tags=["智能检索"])
# app.include_router(summary_router, prefix=f"{settings.API_PREFIX}/summary", tags=["摘要生成"])
```

### Step 13：首次运行验证

1. 右键 `main.py` → **Run 'main'**（或用之前配置的 Run Configuration）
2. 查看 **Run 窗口**（底部）输出：

```
==================================================
  Medical RAG System 启动中...
==================================================
[OK] 模拟数据：3患者，3条病历
  启动完成！
INFO:     Uvicorn running on http://127.0.0.1:8000
```

3. 打开浏览器访问 http://localhost:8000/docs
4. 看到 Swagger UI 界面 → ✅ 验证通过

> 💡 **PyCharm 技巧**：按 `Ctrl+Shift+F10` 可快速运行当前文件。按 `Shift+F9` 以 Debug 模式运行。

### Step 14：实现患者管理 API

右键 `backend/api` → New → Python File → `routes_patient.py`：

```python
# backend/api/routes_patient.py

from fastapi import APIRouter, HTTPException, Query
from data.in_memory_store import get_patient, search_patients, get_patient_records

router = APIRouter()


@router.get("/{patient_id}")
async def get_patient_detail(patient_id: str):
    """获取患者详情 + 时间轴 + 关键实体"""
    patient = get_patient(patient_id)
    if not patient:
        raise HTTPException(404, f"患者 {patient_id} 不存在")

    records = get_patient_records(patient_id)
    timeline = [{
        "date": r.get("visit_time"),
        "type": r.get("record_type"),
        "department": r.get("department"),
        "description": r.get("content", "")[:200],
    } for r in records]

    return {
        "patient": patient,
        "timeline": timeline,
        "entities": {
            "diseases": [{"name": "2型糖尿病"}, {"name": "高血压"}],
            "medications": [{"name": "二甲双胍"}, {"name": "阿司匹林"}],
        }
    }


@router.get("/search")
async def search_patients_api(keyword: str = Query(...), limit: int = Query(10, ge=1, le=50)):
    """搜索患者"""
    results = search_patients(keyword, limit)
    return {"patients": results, "total": len(results)}
```

### Step 15：实现查询搜索 API

#### 15.1 创建 Query 改写模块

右键 `backend/rag` → New → Python File → `query_rewriter.py`：

```python
# backend/rag/query_rewriter.py

import re
from typing import Dict


def rewrite_query(query: str) -> Dict:
    """Query 改写：识别意图 + 术语标准化"""
    intent = "comprehensive_search"
    if "患者" in query or re.search(r'P\d{5}', query):
        intent = "search_by_patient"
    elif "诊断" in query or "疾病" in query:
        intent = "search_by_disease"
    elif "用药" in query or "药物" in query:
        intent = "search_by_medication"

    # 术语标准化
    synonyms = {"血糖高": "糖尿病", "血压高": "高血压", "心梗": "心肌梗死"}
    rewritten = query
    for k, v in synonyms.items():
        rewritten = rewritten.replace(k, v)

    return {"original_query": query, "rewritten_query": rewritten, "intent": intent}
```

#### 15.2 创建时间语义对齐模块（核心创新）

右键 `backend/rag` → New → Python File → `time_aligner.py`：

```python
# backend/rag/time_aligner.py

"""
时间语义对齐 — 系统核心创新
处理医学场景中的复杂时间表达式
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Dict


class TimeAligner:
    def __init__(self):
        self.now = datetime.now()

    def extract_time_constraint(self, query: str) -> Optional[Dict]:
        """从查询中提取时间约束"""

        # 1. 绝对时间：2023年5月
        match = re.search(r'(\d{4})年(\d{1,2})月', query)
        if match:
            y, m = int(match.group(1)), int(match.group(2))
            start = datetime(y, m, 1)
            end = datetime(y + 1, 1, 1) if m == 12 else datetime(y, m + 1, 1)
            return {"type": "absolute", "start": start.isoformat(),
                    "end": end.isoformat(), "raw": match.group(0)}

        # 2. 相对时间：N个月前 / N天前
        match = re.search(r'(\d+)\s*(个月|天|周|年)前', query)
        if match:
            num, unit = int(match.group(1)), match.group(2)
            delta_map = {"个月": 30, "天": 1, "周": 7, "年": 365}
            delta = timedelta(days=num * delta_map[unit])
            return {"type": "relative", "start": (self.now - delta).isoformat(),
                    "end": self.now.isoformat(), "raw": match.group(0)}

        # 3. 模糊相对：上周、上月、去年
        fuzzy = {"上周": 7, "上个月": 30, "去年": 365, "昨天": 1, "前天": 2}
        for kw, days in fuzzy.items():
            if kw in query:
                start = self.now - timedelta(days=days)
                return {"type": "fuzzy", "start": start.isoformat(),
                        "end": self.now.isoformat(), "raw": kw}

        return None
```

> 💡 **PyCharm 技巧**：在 `TimeAligner` 类名上按 `Ctrl+Shift+T` 可快速创建/跳转到测试文件。

#### 15.3 创建混合检索模块

右键 `backend/rag` → New → Python File → `hybrid_search.py`：

```python
# backend/rag/hybrid_search.py

"""
混合检索：BM25 关键词检索 + 向量语义检索 + RRF 融合
"""

import math
from typing import List, Dict, Optional


def bm25_score(query_terms: List[str], document: str, k1=1.5, b=0.75) -> float:
    """BM25 算法"""
    doc_len = len(document)
    score = 0.0
    for term in query_terms:
        tf = document.lower().count(term.lower())
        if tf == 0:
            continue
        idf = math.log((100 - 10 + 0.5) / (10 + 0.5) + 1)
        score += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len / 200))
    return score


def vector_search_sim(query: str, document: str) -> float:
    """模拟向量检索（Jaccard 相似度）"""
    q_words = set(query.lower().split())
    d_words = set(document.lower().split())
    if not q_words or not d_words:
        return 0.0
    return len(q_words & d_words) / len(q_words | d_words)


def rrf_fusion(results_lists: List[List[Dict]], k=60) -> List[Dict]:
    """RRF 融合：score = sum(1 / (k + rank))"""
    fused = {}
    for results in results_lists:
        for rank, item in enumerate(results):
            doc_id = item["document"].get("record_id", str(item))
            if doc_id not in fused:
                fused[doc_id] = item
                fused[doc_id]["_rrf_score"] = 0.0
            fused[doc_id]["_rrf_score"] += 1.0 / (k + rank + 1)

    sorted_items = sorted(fused.values(), key=lambda x: x["_rrf_score"], reverse=True)
    for item in sorted_items:
        item["score"] = item.pop("_rrf_score")
    return sorted_items


def hybrid_search(query: str, patient_id: Optional[str] = None, top_k: int = 10,
                  enable_time_align: bool = True,
                  time_constraint: Optional[Dict] = None) -> List[Dict]:
    """混合检索主函数"""
    from data.in_memory_store import records_db
    documents = list(records_db.values())

    if patient_id:
        documents = [d for d in documents if d.get("patient_id") == patient_id]

    # 时间过滤
    if enable_time_align and time_constraint:
        start = time_constraint.get("start", "")
        end = time_constraint.get("end", "")
        if start and end:
            filtered = []
            for d in documents:
                vt = d.get("visit_time", "")
                if start <= vt <= end:
                    filtered.append(d)
            documents = filtered if filtered else documents

    if not documents:
        return []

    # BM25 检索
    bm25_results = []
    for doc in documents:
        s = bm25_score(query.split(), doc.get("content", ""))
        if s > 0:
            bm25_results.append({"document": doc, "score": s, "source": "bm25"})
    bm25_results.sort(key=lambda x: x["score"], reverse=True)

    # 向量检索（模拟）
    vec_results = []
    for doc in documents:
        s = vector_search_sim(query, doc.get("content", ""))
        if s > 0:
            vec_results.append({"document": doc, "score": s, "source": "vector"})
    vec_results.sort(key=lambda x: x["score"], reverse=True)

    # RRF 融合
    return rrf_fusion([bm25_results, vec_results])[:top_k]
```

#### 15.4 创建查询路由

右键 `backend/api` → New → Python File → `routes_query.py`：

```python
# backend/api/routes_query.py

from fastapi import APIRouter
from models import SearchQuery, SearchResponse, SearchResult
from rag.query_rewriter import rewrite_query
from rag.time_aligner import TimeAligner
from rag.hybrid_search import hybrid_search

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search(query: SearchQuery):
    """智能检索：Query改写 → 时间对齐 → 混合检索"""
    rewritten = rewrite_query(query.query)
    aligner = TimeAligner()
    time_constraint = aligner.extract_time_constraint(query.query)

    raw_results = hybrid_search(
        query=rewritten["rewritten_query"],
        patient_id=query.patient_id,
        top_k=query.top_k,
        enable_time_align=query.enable_time_align,
        time_constraint=time_constraint,
    )

    results = [SearchResult(**r) for r in raw_results]

    return SearchResponse(
        query=query.query,
        query_info={
            "processed_query": rewritten["rewritten_query"],
            "intent": rewritten["intent"],
            "time_constraint": time_constraint,
        },
        results=results,
        total=len(results),
        time_ms=0.0,
    )


@router.get("/suggest")
async def suggest(query: str, limit: int = 5):
    """查询建议"""
    suggestions = []
    if len(query) >= 2:
        suggestions = [
            {"text": f"{query} 在2023年", "score": 0.9},
            {"text": f"{query} 的诊断记录", "score": 0.85},
        ]
    return {"suggestions": suggestions[:limit]}
```

### Step 16：实现摘要生成 API

#### 16.1 创建摘要生成模块

右键 `backend/llm` → New → Python File → `summary_generator.py`：

```python
# backend/llm/summary_generator.py

"""
摘要生成模块
演示版使用模拟数据，生产环境替换为 OpenAI API 调用
"""

import time
from models import SummaryRequest, SummaryResponse, SummarySection
from data.in_memory_store import get_patient_records, save_summary


def generate_summary(request: SummaryRequest) -> SummaryResponse:
    """生成结构化摘要"""
    records = get_patient_records(request.patient_id)

    # 模拟 LLM 生成的摘要（真实环境调用 OpenAI API）
    mock_data = {
        "chief_complaint": ("主诉", "患者因胸痛3天入院，伴出汗、气短。"),
        "history": ("现病史", "患者3天前出现胸骨后压榨样疼痛，持续5-10分钟。"
                              "既往2型糖尿病5年、高血压3年。"),
        "examination": ("体格检查", "BP 160/100mmHg，HR 88次/分，律齐。"
                                     "双肺呼吸音清。"),
        "diagnosis": ("诊断", "1. 急性非ST段抬高型心肌梗死\n2. 2型糖尿病\n3. 高血压3级"),
        "treatment": ("治疗方案", "1. 阿司匹林100mg qd + 氯吡格雷75mg qd\n"
                                   "2. 阿托伐他汀40mg qn\n3. 冠脉支架植入术"),
    }

    sections = {}
    for key, (title, text) in mock_data.items():
        if key in request.include_sections:
            sections[key] = SummarySection(title=title, text=text)

    summary = SummaryResponse(
        summary_id=f"SUM_{request.patient_id}_{int(time.time())}",
        patient_id=request.patient_id,
        summary_type=request.summary_type,
        sections=sections,
        entities={
            "diseases": [{"name": "急性心肌梗死"}, {"name": "2型糖尿病"}],
            "medications": [{"name": "阿司匹林"}, {"name": "氯吡格雷"}],
        },
        metadata={
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model": "demo-model",
            "processing_time_ms": 1500,
        },
    )

    save_summary(summary.dict())
    return summary
```

#### 16.2 创建摘要路由

右键 `backend/api` → New → Python File → `routes_summary.py`：

```python
# backend/api/routes_summary.py

from fastapi import APIRouter
from models import SummaryRequest, SummaryResponse
from llm.summary_generator import generate_summary

router = APIRouter()


@router.post("/generate", response_model=SummaryResponse)
async def generate(request: SummaryRequest):
    """生成转院摘要"""
    return generate_summary(request)
```

### Step 17：注册所有路由并测试

#### 17.1 取消 main.py 中的注释

修改 `backend/main.py`，取消底部注释：

```python
# backend/main.py（修改底部）

# 取消以下注释 ↓
from api.routes_patient import router as patient_router
from api.routes_query import router as query_router
from api.routes_summary import router as summary_router

app.include_router(patient_router, prefix=f"{settings.API_PREFIX}/patient", tags=["患者管理"])
app.include_router(query_router, prefix=f"{settings.API_PREFIX}/query", tags=["智能检索"])
app.include_router(summary_router, prefix=f"{settings.API_PREFIX}/summary", tags=["摘要生成"])
```

#### 17.2 重启服务器

1. 在 Run 窗口点红色方形 ⏹ 停止服务器
2. 再次点绿色三角形 ▶ 启动
3. 访问 http://localhost:8000/docs

现在你应该看到三个 API 分组：**患者管理**、**智能检索**、**摘要生成**

#### 17.3 用 PyCharm HTTP Client 测试 API（Professional 版）

> 如果是 Community 版，用浏览器 Swagger UI 测试即可。

右键 `tests` → New → File → `api_test.http`：

```http
### 健康检查
GET http://localhost:8000/health

### 搜索病历
POST http://localhost:8000/api/v1/query/search
Content-Type: application/json

{
  "query": "患者张三在2023年5月的糖尿病就诊记录",
  "top_k": 5,
  "enable_time_align": true
}

### 获取患者详情
GET http://localhost:8000/api/v1/patient/P00001

### 生成摘要
POST http://localhost:8000/api/v1/summary/generate
Content-Type: application/json

{
  "patient_id": "P00001",
  "summary_type": "transfer",
  "include_sections": ["chief_complaint", "diagnosis", "treatment"]
}
```

在 `.http` 文件中，每个 `###` 分隔一个请求。点击请求旁边的绿色 ▶ 可直接发送，响应显示在右侧面板。

> 💡 **PyCharm HTTP Client** 比 Postman 更轻量，与代码同窗口，推荐使用。

---

## 阶段五：核心算法实现（已在 Step 15 完成）

> 时间语义对齐、混合检索已在 Step 15 完成。此处补充单元测试。

### Step 18：编写单元测试

右键 `tests` → New → Python File → `test_rag.py`：

```python
# tests/test_rag.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from rag.query_rewriter import rewrite_query
from rag.time_aligner import TimeAligner
from rag.hybrid_search import bm25_score, rrf_fusion
from data.in_memory_store import init_mock_data


def test_query_rewrite():
    result = rewrite_query("患者张三的血糖高记录")
    assert "糖尿病" in result["rewritten_query"]
    assert result["intent"] == "search_by_patient"
    print("[PASS] test_query_rewrite")


def test_time_aligner():
    aligner = TimeAligner()
    # 绝对时间
    c = aligner.extract_time_constraint("2023年5月的就诊记录")
    assert c is not None
    assert c["type"] == "absolute"
    # 相对时间
    c = aligner.extract_time_constraint("3个月前的复查")
    assert c is not None
    assert c["type"] == "relative"
    # 无时间
    c = aligner.extract_time_constraint("糖尿病用药")
    assert c is None
    print("[PASS] test_time_aligner")


def test_bm25():
    score = bm25_score(["糖尿病"], "患者确诊糖尿病5年，使用二甲双胍治疗糖尿病")
    assert score > 0
    print(f"[PASS] test_bm25 (score={score:.4f})")


def test_rrf():
    list1 = [{"document": {"record_id": "A"}, "score": 0.9, "source": "bm25"},
             {"document": {"record_id": "B"}, "score": 0.7, "source": "bm25"}]
    list2 = [{"document": {"record_id": "B"}, "score": 0.8, "source": "vector"},
             {"document": {"record_id": "C"}, "score": 0.6, "source": "vector"}]
    fused = rrf_fusion([list1, list2])
    assert len(fused) == 3
    # B 出现在两个列表中，应该排名靠前
    assert fused[0]["document"]["record_id"] == "B"
    print("[PASS] test_rrf")


if __name__ == "__main__":
    init_mock_data()
    test_query_rewrite()
    test_time_aligner()
    test_bm25()
    test_rrf()
    print("\n全部测试通过！")
```

**运行测试**：

方法一：右键 `test_rag.py` → **Run 'test_rag'**

方法二：Terminal 中：
```bash
cd backend
python ../tests/test_rag.py
```

预期输出：
```
[OK] 模拟数据：3患者，3条病历
[PASS] test_query_rewrite
[PASS] test_time_aligner
[PASS] test_bm25 (score=...)
[PASS] test_rrf

全部测试通过！
```

---

## 阶段六：前端界面开发

### Step 19：创建首页 HTML

右键 `frontend` → New → HTML File → `index.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>智能病历检索系统</title>
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>🏥 智能病历检索系统</h1>
            <nav>
                <a href="/">首页</a>
                <a href="/patient.html">患者详情</a>
                <a href="/summary.html">生成摘要</a>
            </nav>
        </div>
    </header>

    <main class="container">
        <section class="card">
            <h2>🔍 智能检索</h2>
            <div class="search-box">
                <input type="text" id="searchInput"
                       placeholder="输入查询，如：患者张三在2023年5月的糖尿病就诊记录">
                <button id="searchBtn" class="btn-primary">搜索</button>
            </div>
            <div class="options">
                <label>患者ID：<input type="text" id="patientId" size="8"></label>
                <label>结果数：<input type="number" id="topK" value="10" min="1" max="50" size="3"></label>
                <label><input type="checkbox" id="timeAlign" checked> 时间语义对齐</label>
            </div>
            <div id="suggestions" class="suggestions"></div>
        </section>

        <div id="loading" class="loading hidden">
            <div class="spinner"></div>
            <p>正在检索...</p>
        </div>

        <section id="results" class="hidden">
            <h3>检索结果 <span id="resultCount"></span></h3>
            <div id="resultsList"></div>
        </section>
    </main>

    <script src="/js/api.js"></script>
    <script src="/js/app.js"></script>
</body>
</html>
```

### Step 20：创建患者详情页 HTML

右键 `frontend` → New → HTML File → `patient.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>患者详情</title>
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>👤 患者详情</h1>
            <nav>
                <a href="/">首页</a>
                <a href="/patient.html">患者查询</a>
                <a href="/summary.html">生成摘要</a>
            </nav>
        </div>
    </header>

    <main class="container">
        <div id="loading" class="loading">加载中...</div>
        <div id="patientContent" class="hidden">
            <div class="patient-header">
                <h2 id="patientName"></h2>
                <div id="patientMeta"></div>
            </div>
            <h3>📅 时间轴</h3>
            <div id="timeline" class="timeline"></div>
            <h3>🏷️ 关键实体</h3>
            <div id="entities" class="entities"></div>
        </div>
    </main>

    <script src="/js/api.js"></script>
    <script src="/js/patient.js"></script>
</body>
</html>
```

### Step 21：创建摘要生成页 HTML

右键 `frontend` → New → HTML File → `summary.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>生成摘要</title>
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>📝 生成摘要</h1>
            <nav>
                <a href="/">首页</a>
                <a href="/patient.html">患者查询</a>
                <a href="/summary.html">生成摘要</a>
            </nav>
        </div>
    </header>

    <main class="container">
        <section class="card">
            <h2>摘要配置</h2>
            <div class="options">
                <label>患者ID：<input type="text" id="patientId"></label>
                <label>类型：
                    <select id="summaryType">
                        <option value="transfer">转院摘要</option>
                        <option value="discharge">出院小结</option>
                    </select>
                </label>
            </div>
            <div id="sections" class="options">
                <label><input type="checkbox" value="chief_complaint" checked> 主诉</label>
                <label><input type="checkbox" value="history" checked> 现病史</label>
                <label><input type="checkbox" value="diagnosis" checked> 诊断</label>
                <label><input type="checkbox" value="treatment" checked> 治疗方案</label>
            </div>
            <button id="generateBtn" class="btn-primary">生成摘要</button>
        </section>

        <div id="loading" class="loading hidden">生成中...</div>
        <section id="result" class="card hidden"></section>
    </main>

    <script src="/js/api.js"></script>
    <script src="/js/summary.js"></script>
</body>
</html>
```

### Step 22：创建 CSS 样式

右键 `frontend/css` → New → Stylesheet → `style.css`：

```css
/* frontend/css/style.css */

:root {
    --primary: #2563eb;
    --primary-dark: #1d4ed8;
    --bg: #f8fafc;
    --card-bg: #ffffff;
    --border: #e2e8f0;
    --text: #1e293b;
    --text-muted: #64748b;
    --success: #16a34a;
    --radius: 8px;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
}

.container { max-width: 1000px; margin: 0 auto; padding: 0 20px; }

.header {
    background: linear-gradient(135deg, var(--primary), var(--primary-dark));
    color: white; padding: 1rem 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.header .container { display: flex; align-items: center; justify-content: space-between; }
.header h1 { font-size: 1.4rem; }
.header nav a { color: white; text-decoration: none; margin-left: 1.5rem; opacity: 0.9; }
.header nav a:hover { opacity: 1; }

.card {
    background: var(--card-bg); border-radius: var(--radius);
    padding: 1.5rem; margin: 1.5rem 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.search-box { display: flex; gap: 0.5rem; margin: 1rem 0; }
.search-box input {
    flex: 1; padding: 0.7rem 1rem;
    border: 2px solid var(--border); border-radius: var(--radius);
    font-size: 1rem;
}
.search-box input:focus { outline: none; border-color: var(--primary); }

.btn-primary {
    background: var(--primary); color: white; border: none;
    padding: 0.7rem 1.5rem; border-radius: var(--radius);
    cursor: pointer; font-size: 1rem; transition: background 0.2s;
}
.btn-primary:hover { background: var(--primary-dark); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

.options { display: flex; flex-wrap: wrap; gap: 1rem; margin: 1rem 0; font-size: 0.9rem; }
.options label { display: flex; align-items: center; gap: 0.3rem; }

.suggestions { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1rem; }
.suggestion-chip {
    background: #eff6ff; color: var(--primary-dark);
    padding: 0.3rem 0.8rem; border-radius: 20px;
    cursor: pointer; font-size: 0.85rem;
}
.suggestion-chip:hover { background: var(--primary); color: white; }

.result-item {
    border: 1px solid var(--border); border-radius: var(--radius);
    padding: 1rem; margin: 0.8rem 0;
}
.result-item:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.result-header { display: flex; justify-content: space-between; }
.result-title { font-weight: 600; }
.result-score { color: var(--success); font-size: 0.85rem; }
.result-meta { display: flex; flex-wrap: wrap; gap: 1rem; margin: 0.5rem 0; font-size: 0.85rem; color: var(--text-muted); }
.result-content { font-size: 0.9rem; background: var(--bg); padding: 0.8rem; border-radius: var(--radius); }
.result-highlight { background: #fef08a; font-weight: 600; }

.timeline { border-left: 3px solid var(--primary); margin-left: 1rem; }
.timeline-item { margin: 1rem 0; padding-left: 1.5rem; position: relative; }
.timeline-item::before {
    content: ''; position: absolute; left: -9px; top: 5px;
    width: 12px; height: 12px; background: var(--primary); border-radius: 50%;
}
.timeline-date { font-size: 0.85rem; color: var(--primary-dark); font-weight: 600; }

.entities { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.entity-tag {
    background: #eff6ff; color: var(--primary-dark);
    padding: 0.3rem 0.8rem; border-radius: 6px; font-size: 0.85rem;
}

.loading { text-align: center; padding: 2rem; color: var(--text-muted); }
.spinner {
    width: 40px; height: 40px; border: 4px solid var(--border);
    border-top-color: var(--primary); border-radius: 50%;
    animation: spin 1s linear infinite; margin: 0 auto 1rem;
}
@keyframes spin { to { transform: rotate(360deg); } }
.hidden { display: none !important; }
```

### Step 23：创建 JavaScript 文件

#### 23.1 API 通信层

右键 `frontend/js` → New → JavaScript File → `api.js`：

```javascript
// frontend/js/api.js

const API_BASE = '/api/v1';

class ApiClient {
    async request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const config = {
            headers: { 'Content-Type': 'application/json' },
            ...options
        };
        const response = await fetch(url, config);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    }

    async search(query, options = {}) {
        return this.request('/query/search', {
            method: 'POST',
            body: JSON.stringify({
                query,
                patient_id: options.patientId || null,
                top_k: options.topK || 10,
                enable_time_align: options.enableTimeAlign !== false
            })
        });
    }

    async getPatient(patientId) {
        return this.request(`/patient/${patientId}`);
    }

    async generateSummary(patientId, options = {}) {
        return this.request('/summary/generate', {
            method: 'POST',
            body: JSON.stringify({
                patient_id: patientId,
                summary_type: options.type || 'transfer',
                include_sections: options.sections || ['chief_complaint', 'history', 'diagnosis', 'treatment']
            })
        });
    }

    async healthCheck() {
        return this.request('/health');
    }
}

window.api = new ApiClient();
```

#### 23.2 首页逻辑

右键 `frontend/js` → New → JavaScript File → `app.js`：

```javascript
// frontend/js/app.js

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const patientIdInput = document.getElementById('patientId');
    const topKInput = document.getElementById('topK');
    const timeAlignCheck = document.getElementById('timeAlign');
    const suggestionsEl = document.getElementById('suggestions');
    const resultsSection = document.getElementById('results');
    const resultsList = document.getElementById('resultsList');
    const resultCount = document.getElementById('resultCount');
    const loadingEl = document.getElementById('loading');

    async function performSearch() {
        const query = searchInput.value.trim();
        if (!query) return;

        loadingEl.classList.remove('hidden');
        resultsSection.classList.add('hidden');

        try {
            const data = await api.search(query, {
                patientId: patientIdInput.value.trim(),
                topK: parseInt(topKInput.value) || 10,
                enableTimeAlign: timeAlignCheck.checked
            });
            displayResults(data);
        } catch (error) {
            alert('搜索失败：' + error.message);
        } finally {
            loadingEl.classList.add('hidden');
        }
    }

    function displayResults(data) {
        const results = data.results || [];
        resultCount.textContent = `(${results.length})`;

        if (results.length === 0) {
            resultsList.innerHTML = '<p style="color:#64748b;">未找到结果</p>';
        } else {
            resultsList.innerHTML = results.map(r => {
                const doc = r.document;
                return `
                    <div class="result-item">
                        <div class="result-header">
                            <span class="result-title">${doc.record_type || '病历'}</span>
                            <span class="result-score">相关度: ${(r.score * 100).toFixed(1)}%</span>
                        </div>
                        <div class="result-meta">
                            ${doc.patient_id ? `<span>🆔 ${doc.patient_id}</span>` : ''}
                            ${doc.department ? `<span>🏥 ${doc.department}</span>` : ''}
                            ${doc.visit_time ? `<span>📅 ${doc.visit_time.split('T')[0]}</span>` : ''}
                        </div>
                        <div class="result-content">${highlight(doc.content || '', searchInput.value)}</div>
                        ${doc.patient_id ? `<button class="btn-primary" style="margin-top:0.5rem;font-size:0.85rem;padding:0.3rem 0.8rem;" onclick="location.href='/patient.html?id=${doc.patient_id}'">查看患者</button>` : ''}
                    </div>
                `;
            }).join('');
        }
        resultsSection.classList.remove('hidden');
    }

    function highlight(text, query) {
        if (!text) return '';
        const escaped = text.substring(0, 300).replace(/</g, '&lt;');
        return escaped.replace(new RegExp(query, 'gi'), m => `<span class="result-highlight">${m}</span>`);
    }

    searchBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', e => { if (e.key === 'Enter') performSearch(); });

    // 实时建议
    let timeout;
    searchInput.addEventListener('input', () => {
        clearTimeout(timeout);
        timeout = setTimeout(async () => {
            const q = searchInput.value.trim();
            if (q.length < 2) { suggestionsEl.innerHTML = ''; return; }
            try {
                const data = await api.request(`/query/suggest?query=${encodeURIComponent(q)}`);
                suggestionsEl.innerHTML = (data.suggestions || []).map(s =>
                    `<span class="suggestion-chip" onclick="document.getElementById('searchInput').value='${s.text}';performSearch()">${s.text}</span>`
                ).join('');
            } catch (e) {}
        }, 500);
    });

    api.healthCheck().catch(() => console.warn('后端未连接'));
});
```

#### 23.3 患者详情页逻辑

右键 `frontend/js` → New → JavaScript File → `patient.js`：

```javascript
// frontend/js/patient.js

document.addEventListener('DOMContentLoaded', () => {
    const loadingEl = document.getElementById('loading');
    const contentEl = document.getElementById('patientContent');
    const nameEl = document.getElementById('patientName');
    const metaEl = document.getElementById('patientMeta');
    const timelineEl = document.getElementById('timeline');
    const entitiesEl = document.getElementById('entities');

    const params = new URLSearchParams(window.location.search);
    const patientId = params.get('id');

    if (!patientId) {
        loadingEl.textContent = '未提供患者ID';
        return;
    }

    async function loadPatient() {
        try {
            const data = await api.getPatient(patientId);
            const patient = data.patient || {};

            nameEl.textContent = `${patient.name || patientId} (${patientId})`;
            metaEl.innerHTML = [
                patient.gender ? `👤 ${patient.gender}` : '',
                patient.age ? `🎂 ${patient.age}岁` : '',
                patient.phone ? `📞 ${patient.phone}` : ''
            ].filter(Boolean).map(t => `<span style="margin-right:1rem;">${t}</span>`).join('');

            const timeline = data.timeline || [];
            timelineEl.innerHTML = timeline.map(t => `
                <div class="timeline-item">
                    <div class="timeline-date">${(t.date || '').split('T')[0]}</div>
                    <div><strong>${t.type || ''}</strong> - ${t.department || ''}</div>
                    <div style="font-size:0.85rem;color:#64748b;">${t.description || ''}</div>
                </div>
            `).join('');

            const entities = data.entities || {};
            const allEntities = [];
            Object.values(entities).forEach(list => {
                (list || []).forEach(e => allEntities.push(e.name));
            });
            entitiesEl.innerHTML = allEntities.map(name =>
                `<span class="entity-tag">${name}</span>`
            ).join('');

            loadingEl.classList.add('hidden');
            contentEl.classList.remove('hidden');
        } catch (error) {
            loadingEl.textContent = '加载失败：' + error.message;
        }
    }

    loadPatient();
});
```

#### 23.4 摘要生成页逻辑

右键 `frontend/js` → New → JavaScript File → `summary.js`：

```javascript
// frontend/js/summary.js

document.addEventListener('DOMContentLoaded', () => {
    const patientIdInput = document.getElementById('patientId');
    const typeSelect = document.getElementById('summaryType');
    const sectionsEl = document.getElementById('sections');
    const generateBtn = document.getElementById('generateBtn');
    const loadingEl = document.getElementById('loading');
    const resultEl = document.getElementById('result');

    const params = new URLSearchParams(window.location.search);
    if (params.get('patient_id')) {
        patientIdInput.value = params.get('patient_id');
    }

    generateBtn.addEventListener('click', async () => {
        const patientId = patientIdInput.value.trim();
        if (!patientId) { alert('请输入患者ID'); return; }

        const sections = Array.from(sectionsEl.querySelectorAll('input:checked')).map(cb => cb.value);

        loadingEl.classList.remove('hidden');
        resultEl.classList.add('hidden');
        generateBtn.disabled = true;

        try {
            const data = await api.generateSummary(patientId, {
                type: typeSelect.value,
                sections
            });

            let html = '<h2>📋 生成结果</h2>';
            Object.values(data.sections || {}).forEach(sec => {
                html += `
                    <div style="margin:1rem 0;">
                        <h3 style="color:var(--primary-dark);">${sec.title}</h3>
                        <div class="result-content">${sec.text.replace(/\n/g, '<br>')}</div>
                    </div>
                `;
            });

            if (data.entities) {
                html += '<h3>🏷️ 关键实体</h3><div class="entities">';
                Object.values(data.entities).forEach(list => {
                    (list || []).forEach(e => {
                        html += `<span class="entity-tag">${e.name}</span>`;
                    });
                });
                html += '</div>';
            }

            resultEl.innerHTML = html;
            resultEl.classList.remove('hidden');
        } catch (error) {
            alert('生成失败：' + error.message);
        } finally {
            loadingEl.classList.add('hidden');
            generateBtn.disabled = false;
        }
    });
});
```

---

## 阶段七：前后端联调测试

### Step 24：创建演示服务器（同时服务前后端）

右键 `backend` → New → Python File → `demo_server.py`：

```python
# backend/demo_server.py
"""
演示服务器 — 同时提供 API 和静态文件服务
用于本地开发联调，无需 Nginx
"""

import json
import os
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# 添加 backend 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.in_memory_store import init_mock_data, patients_db, records_db, summaries_db
from rag.query_rewriter import rewrite_query
from rag.time_aligner import TimeAligner
from rag.hybrid_search import hybrid_search
from llm.summary_generator import generate_summary
from models import SummaryRequest, SummaryType

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')

MIME = {'.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
        '.js': 'application/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8'}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path, params = parsed.path, parse_qs(parsed.query)

        # API
        if path == '/health':
            return self._json({"status": "healthy", "version": "1.0.0"})

        if path == '/api/v1/query/suggest':
            q = params.get('query', [''])[0]
            s = [{"text": f"{q} 在2023年", "score": 0.9},
                 {"text": f"{q} 的诊断记录", "score": 0.85}] if len(q) >= 2 else []
            return self._json({"suggestions": s})

        if path.startswith('/api/v1/patient/') and not path.endswith('/timeline'):
            pid = path.split('/')[-1]
            if pid in patients_db:
                recs = [r for r in records_db.values() if r['patient_id'] == pid]
                recs.sort(key=lambda x: x['visit_time'])
                timeline = [{"date": r.get('visit_time'), "type": r.get('record_type'),
                             "department": r.get('department'), "description": r.get('content', '')[:200]}
                            for r in recs]
                return self._json({"patient": patients_db[pid], "timeline": timeline,
                                   "entities": {"diseases": [{"name": "2型糖尿病"}],
                                                "medications": [{"name": "二甲双胍"}]}})
            return self._json({"error": "not found"}, 404)

        # 静态文件
        return self._serve_static(path)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8') if length else "{}"
        try:
            data = json.loads(body)
        except:
            data = {}

        if path == '/api/v1/query/search':
            query = data.get('query', '')
            rewritten = rewrite_query(query)
            aligner = TimeAligner()
            tc = aligner.extract_time_constraint(query)
            results = hybrid_search(query, data.get('patient_id'), data.get('top_k', 10),
                                    data.get('enable_time_align', True), tc)
            return self._json({"query": query,
                               "query_info": {"processed_query": rewritten["rewritten_query"],
                                              "intent": rewritten["intent"],
                                              "time_constraint": tc},
                               "results": results, "total": len(results), "time_ms": 0.0})

        if path == '/api/v1/summary/generate':
            req = SummaryRequest(
                patient_id=data['patient_id'],
                summary_type=SummaryType(data.get('summary_type', 'transfer')),
                include_sections=data.get('include_sections', ['chief_complaint', 'history', 'diagnosis', 'treatment'])
            )
            summary = generate_summary(req)
            return self._json(summary.dict())

        return self._json({"error": "not found"}, 404)

    def _serve_static(self, path):
        file_path = os.path.join(FRONTEND_DIR, 'index.html' if path == '/' else path.lstrip('/'))
        if not os.path.isfile(file_path):
            file_path = os.path.join(FRONTEND_DIR, 'index.html')
        if os.path.isfile(file_path):
            ext = os.path.splitext(file_path)[1]
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', MIME.get(ext, 'application/octet-stream'))
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        else:
            self._json({"error": "file not found"}, 404)

    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))

    def log_message(self, *args):
        pass


def run(port=8000):
    init_mock_data()
    print(f"\n[OK] 演示服务器启动: http://localhost:{port}")
    print(f"[OK] 前端目录: {FRONTEND_DIR}")
    print(f"[OK] API 文档: http://localhost:{port}/docs (需要 FastAPI 模式)\n")
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()


if __name__ == '__main__':
    run(8000)
```

### Step 25：在 PyCharm 中配置并运行演示服务器

1. **Run → Edit Configurations**
2. 点 **+** → Python
3. 配置：

```
Name:           Demo Server
Script path:    C:\...\medical-rag-system\backend\demo_server.py
Working dir:    C:\...\medical-rag-system\backend
```

4. 点 OK
5. 在配置下拉菜单选择 **Demo Server** → 点 ▶ 启动

### Step 26：前后端联调

1. 确认服务器已启动（Run 窗口显示 `[OK] 演示服务器启动`）
2. 打开浏览器访问 http://localhost:8000
3. **测试流程**：

| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 在搜索框输入"糖尿病" | 出实时建议 |
| 2 | 点击"搜索"按钮 | 显示检索结果列表 |
| 3 | 点击"查看患者" | 跳转到患者详情页 |
| 4 | 看到时间轴和关键实体 | 页面正常展示 |
| 5 | 访问 `/summary.html?patient_id=P00001` | 摘要生成页 |
| 6 | 点击"生成摘要" | 显示结构化摘要 |

> 💡 **PyCharm 调试技巧**：如果前端 JS 有问题，在 Chrome 按 `F12` → Console 查看错误。如果后端有问题，在 PyCharm Run 窗口查看日志。

---

## 阶段八：Docker 容器化部署

### Step 27：编写 Dockerfile

#### 后端 Dockerfile

右键 `backend` → New → File → `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 前端 Dockerfile

右键 `frontend` → New → File → `Dockerfile`：

```dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Step 28：编写 Docker Compose

右键 `deploy` → New → File → `docker-compose.yml`：

```yaml
version: '3.8'

services:
  backend:
    build: ../backend
    ports:
      - "8000:8000"
    depends_on:
      - mysql
      - redis

  frontend:
    build: ../frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: medical_rag
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  mysql_data:
```

### Step 29：使用 PyCharm Docker 集成部署（Professional 版）

> Community 版用户请用 Terminal 执行 `docker-compose` 命令。

1. 确保 Docker Desktop 已启动
2. 在 PyCharm 中：**Settings → Build → Docker → +** 添加 Docker 连接
3. 右键 `docker-compose.yml` → **Run 'docker-compose'**
4. PyCharm 会自动构建并启动所有服务
5. 在 **Services** 面板（底部）可查看容器状态

**Terminal 方式**（所有版本通用）：

```bash
cd deploy
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f backend

# 停止
docker-compose down
```

### Step 30：最终验证

| 服务 | 地址 | 验证方式 |
|------|------|----------|
| 前端 | http://localhost | 看到检索页面 |
| 后端 API | http://localhost:8000/health | 返回 JSON |
| API 文档 | http://localhost:8000/docs | Swagger UI |
| MySQL | localhost:3306 | 用 PyCharm Database 工具连接 |
| Redis | localhost:6379 | `docker exec -it <container> redis-cli ping` |

---

## 附录 A：PyCharm 实用快捷键速查

| 快捷键 | 功能 |
|--------|------|
| `Alt+1` | 打开/关闭 Project 面板 |
| `Alt+F12` | 打开 Terminal |
| `Ctrl+Shift+F10` | 运行当前文件 |
| `Shift+F9` | Debug 模式运行 |
| `Ctrl+B` | 跳转到定义 |
| `Ctrl+Alt+L` | 格式化代码 |
| `Ctrl+D` | 复制当前行 |
| `Ctrl+Y` | 删除当前行 |
| `Ctrl+/` | 注释/取消注释 |
| `Ctrl+F` | 当前文件搜索 |
| `Ctrl+Shift+F` | 全局搜索 |
| `Ctrl+R` | 替换 |
| `F2` | 跳转到下一个错误 |
| `Alt+Enter` | 快速修复（智能提示） |
| `Ctrl+K` | Git Commit |

## 附录 B：常见问题

### Q1：ModuleNotFoundError: No module named 'fastapi'

**原因**：虚拟环境未激活或依赖未安装。

**解决**：
1. `Alt+F12` 打开 Terminal
2. 确认提示符有 `(venv)`
3. 如果没有：`source venv/bin/activate`（Mac/Linux）或 `venv\Scripts\activate`（Windows）
4. `pip install -r requirements.txt`

### Q2：端口 8000 被占用

**解决**：
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :8000
kill -9 <PID>
```

### Q3：PyCharm 找不到 Python 解释器

**解决**：`Ctrl+Alt+S` → Project → Python Interpreter → 齿轮图标 → Add → Existing → 选择 `venv/Scripts/python.exe`

### Q4：前端页面打开是空白

**原因**：直接用 `file://` 协议打开 HTML 会有跨域问题。

**解决**：必须通过服务器访问（http://localhost:8000），不能直接双击 HTML 文件。

### Q5：Docker 构建失败

**解决**：
```bash
# 清理重新构建
docker-compose down -v
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
```

---

## 项目完成清单

完成后，检查以下清单：

- [ ] PyCharm 项目创建并配置虚拟环境
- [ ] `requirements.txt` 依赖安装成功
- [ ] `config.py` 配置模块正常加载
- [ ] `main.py` FastAPI 应用启动成功
- [ ] `/docs` Swagger UI 可正常访问
- [ ] 患者管理 API 通过测试
- [ ] 检索 API 返回正确结果
- [ ] 时间语义对齐功能正常
- [ ] 混合检索 RRF 融合正确
- [ ] 摘要生成 API 返回结构化结果
- [ ] 单元测试全部通过
- [ ] 前端三页面正常显示
- [ ] 前后端联调成功
- [ ] Docker 部署成功
- [ ] 所有服务正常运行

---

**恭喜完成项目搭建！** 🎉

如果遇到问题，请先查看 **附录 B 常见问题**，或在 PyCharm 中使用 Debug 模式逐步排查。
