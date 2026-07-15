# 手把手教你搭建智能病历检索系统

> **项目名称**：Medical RAG System  
> **预计完成时间**：4-6 小时（可分阶段完成）  
> **适用对象**：有 Python/JavaScript 基础，想学习完整项目开发流程的开发者

---

## 📋 目录

- [第一部分：项目准备](#第一部分项目准备)
- [第二部分：后端开发](#第二部分后端开发)
- [第三部分：前端开发](#第三部分前端开发)
- [第四部分：核心功能实现](#第四部分核心功能实现)
- [第五部分：Docker 部署](#第五部分docker-部署)
- [第六部分：测试与优化](#第六部分测试与优化)
- [附录：故障排查](#附录故障排查)

---

## 第一部分：项目准备

### Step 0：项目概述

#### 🎯 我们要搭建什么？

一个**面向转院场景的关键信息智能检索系统**，帮助医生快速从海量病历中检索关键信息并生成结构化转院摘要。

**核心功能**：

1. **智能检索**：输入自然语言查询（如"患者张三在2023年5月的糖尿病就诊记录"），系统自动理解并返回相关病历
2. **时间语义对齐**：理解复杂时间表达式（"3个月前"、"上周"、"手术后第5天"）
3. **混合检索**：结合关键词检索（BM25）和语义检索（向量）
4. **实体识别**：自动提取疾病、症状、药物等关键实体
5. **摘要生成**：一键生成结构化转院摘要

**技术架构**：

```
┌─────────────────────────────────────────┐
│   前端界面（HTML/CSS/JavaScript）       │  ← 您会学会
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│   API 服务层（FastAPI）                │  ← 您会学会
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│   RAG 检索层（Query改写 + 混合检索）    │  ← 您会学会
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│   数据层（MySQL + Milvus + Redis）      │  ← 您会学会基础
└─────────────────────────────────────────┘
```

#### 🛠️ 技术栈

| 层级       | 技术            | 为什么选择它？           |
| -------- | ------------- | ----------------- |
| **后端框架** | FastAPI       | 现代、快速、自动生成 API 文档 |
| **数据库**  | MySQL         | 成熟稳定，存储结构化病历数据    |
| **向量库**  | Milvus        | 开源高性能，专为向量检索设计    |
| **搜索引擎** | Elasticsearch | 强大的全文检索能力         |
| **缓存**   | Redis         | 提升查询性能            |
| **前端**   | 原生 JS         | 无框架依赖，更易理解原理      |
| **部署**   | Docker        | 一键部署，环境一致性        |

#### 📦 最终效果预览

完成后的系统界面：

**1. 智能检索首页**

```
┌──────────────────────────────────────┐
│  🔍 智能检索                       │
├──────────────────────────────────────┤
│  ┌──────────────────────────────┐  │
│  │ 输入查询内容...           │搜索│  │
│  └──────────────────────────────┘  │
│                                       │
│  ☑ 启用时间语义对齐                   │
│  结果数量：[10  ]                    │
│                                       │
│  检索结果：                           │
│  ┌──────────────────────────────┐  │
│  │ 📋 门诊病历 - 相关度: 95%   │  │
│  │ 患者ID: P00001               │  │
│  │ 时间: 2023-05-10            │  │
│  │ 内容: 患者因糖尿病...        │  │
│  │ [查看详情] [生成摘要]        │  │
│  └──────────────────────────────┘  │
└──────────────────────────────────────┘
```

**2. 患者详情页**

```
┌──────────────────────────────────────┐
│  👤 患者详情 - 张三 (P00001)       │
├──────────────────────────────────────┤
│  基本信息: 男, 45岁, 138****8001    │
│                                       │
│  📅 时间轴                           │
│  ● 2023-01-10  门诊  内分泌科       │
│  ● 2023-05-15  住院  心内科        │
│  ● 2023-08-20  复查  内分泌科      │
│                                       │
│  🏷️ 关键实体                        │
│  [糖尿病] [高血压] [二甲双胍]        │
└──────────────────────────────────────┘
```

---

### Step 1：环境搭建

#### ✅ 检查清单

在开始之前，请确保您的电脑已安装：

- [ ] **Python 3.8+**（`python --version`）
- [ ] **Git**（`git --version`）
- [ ] **代码编辑器**（推荐 VS Code）
- [ ] **Docker Desktop**（可选，用于完整部署）

#### 🔧 安装步骤（如未安装）

**1. 安装 Python**

- **Windows**：访问 <https://www.python.org/downloads/，下载> 3.11+ 版本，安装时勾选 "Add Python to PATH"
- **Mac**：`brew install python@3.11`（需要 Homebrew）
- **Linux**：`sudo apt install python3.11 python3-pip`

验证：

```bash
python --version
# 应显示 Python 3.8+

pip --version
# 应显示 pip 版本
```

**2. 安装 VS Code**

访问 <https://code.visualstudio.com/> 下载安装

推荐插件：

- Python（Microsoft）
- Pylance
- GitLens
- Live Server

**3. 安装 Docker Desktop**（可选）

访问 <https://www.docker.com/products/docker-desktop> 下载安装

验证：

```bash
docker --version
docker-compose --version
```

#### 📁 创建项目目录

打开终端，执行：

```bash
# 进入桌面（或您喜欢的项目存放位置）
cd ~/Desktop

# 创建项目根目录
mkdir medical-rag-system
cd medical-rag-system

# 创建子目录结构
mkdir backend
mkdir frontend
mkdir frontend/css
mkdir frontend/js
mkdir data
mkdir deploy
mkdir tests

# 初始化 Git 仓库
git init

echo "项目目录创建成功！"
ls -la
```

**预期输出**：

```
total 24
drwxr-xr-x 1 user  staff  256 Jan 10 10:00 .
drwxr-xr-x 1 user  staff  512 Jan 10 09:59 ..
drwxr-xr-x 1 user  staff  128 Jan 10 10:00 .git
drwxr-xr-x 1 user  staff  128 Jan 10 10:00 backend
drwxr-xr-x 1 user  staff  128 Jan 10 10:00 data
drwxr-xr-x 1 user  staff  128 Jan 10 10:00 deploy
drwxr-xr-x 1 user  staff  128 Jan 10 10:00 frontend
drwxr-xr-x 1 user  staff  128 Jan 10 10:00 tests
```

✅ **检查点**：目录结构如上所示，说明创建成功！

---

### Step 2：Python 虚拟环境

#### 为什么需要虚拟环境？

虚拟环境可以隔离项目依赖，避免不同项目之间的包版本冲突。

#### 创建虚拟环境

```bash
# 确保在项目根目录
cd ~/Desktop/medical-rag-system

# 创建虚拟环境（venv 是 Python 内置工具）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

**激活成功的标志**：终端提示符前面会出现 `(venv)`

```
(venv) C:\Users\YourName\Desktop\medical-rag-system>
```

#### 安装项目依赖

创建 `requirements.txt` 文件：

```bash
# 在项目根目录创建文件
touch requirements.txt
# Windows 用: type nul > requirements.txt
```

用 VS Code 打开项目，编辑 `requirements.txt`：

```txt
# requirements.txt

# Web 框架
fastapi==0.109.0
uvicorn[standard]==0.27.0

# 数据验证
pydantic==2.5.3
pydantic-settings==2.1.0

# 数据库
pymysql==1.1.0
sqlalchemy==2.0.25

# 向量数据库
pymilvus==2.3.4

# 搜索引擎
elasticsearch==8.11.0

# 缓存
redis==5.0.1

# LLM
openai==1.6.1
langchain==0.1.4

# 工具
python-dotenv==1.0.0
requests==2.31.0
```

安装依赖：

```bash
# 确保虚拟环境已激活（看到 (venv) 前缀）
pip install -r requirements.txt
```

**预期输出**（部分）：

```
Collecting fastapi==0.109.0
  Downloading fastapi-0.109.0-py3-none-any.whl (92 kB)
Collecting uvicorn[standard]==0.27.0
  Downloading uvicorn-0.27.0-py3-none-any.whl (76 kB)
...
Successfully installed fastapi-0.109.0 uvicorn-0.27.0 ...
```

✅ **检查点**：

```bash
pip list | grep -E "fastapi|uvicorn"
# 应显示安装的包和版本
```

---

### Step 3：第一个 FastAPI 应用

#### 创建应用入口

在 `backend/` 目录下创建 `main.py`：

```python
# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 创建 FastAPI 应用实例
app = FastAPI(
    title="Medical RAG System",
    description="面向转院场景的关键信息智能检索系统",
    version="1.0.0"
)

# 配置 CORS（允许前端跨域请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# 健康检查端点
# ============================================

@app.get("/health")
def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "message": "Medical RAG System is running!"
    }

# ============================================
# 根路径
# ============================================

@app.get("/")
def read_root():
    """API 根路径"""
    return {
        "app": "Medical RAG System",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }

# ============================================
# 示例 API 端点
# ============================================

@app.get("/api/v1/example")
def example_endpoint():
    """示例端点"""
    return {
        "message": "恭喜！您的第一个 FastAPI 应用运行成功！",
        "next_step": "访问 /docs 查看自动生成的 API 文档"
    }
```

#### 运行应用

```bash
# 进入 backend 目录
cd backend

# 启动开发服务器（--reload 启用热重载）
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**预期输出**：

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### 测试应用

打开浏览器，访问：

1. **根路径**：<http://localhost:8000>
   ```json
   {
     "app": "Medical RAG System",
     "docs": "/docs",
     "openapi": "/openapi.json"
   }
   ```
2. **健康检查**：<http://localhost:8000/health>
   ```json
   {
     "status": "healthy",
     "version": "1.0.0",
     "message": "Medical RAG System is running!"
   }
   ```
3. **API 文档**（重点！）：<http://localhost:8000/docs>

   FastAPI 会自动生成交互式 API 文档（基于 Swagger UI），您可以直接在网页上测试 API！

✅ **检查点**：

- [ ] 浏览器能访问 <http://localhost:8000>
- [ ] 能看到 JSON 响应
- [ ] 访问 <http://localhost:8000/docs> 能看到漂亮的 API 文档界面

**💡 小技巧**：

- 修改代码后，服务器会自动重启（因为加了 `--reload`）
- 随时访问 `/docs` 查看和测试 API
- 按 `Ctrl+C` 停止服务器

---

### Step 4：配置管理

#### 为什么需要配置文件？

项目中有很多配置项（数据库密码、API Key、服务端口等），硬编码在代码里不方便维护，也容易泄露敏感信息。

#### 创建配置模块

在 `backend/` 目录下创建 `config.py`：

```python
# backend/config.py

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """应用配置类
    
    使用 Pydantic Settings 自动从环境变量和 .env 文件加载配置
    """
    
    # ============================================
    # 应用基础配置
    # ============================================
    APP_NAME: str = "Medical RAG System"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"
    
    # ============================================
    # 服务器配置
    # ============================================
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # ============================================
    # 数据库配置
    # ============================================
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "rag_user"
    MYSQL_PASSWORD: str = "rag_password"
    MYSQL_DATABASE: str = "medical_rag"
    
    # ============================================
    # LLM 配置
    # ============================================
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_TEMPERATURE: float = 0.1
    OPENAI_MAX_TOKENS: int = 2000
    
    # ============================================
    # 向量数据库配置
    # ============================================
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION: str = "medical_records"
    
    # ============================================
    # 缓存配置
    # ============================================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    class Config:
        """Pydantic 配置"""
        env_file = ".env"
        env_file_encoding = "utf-8"

# 创建全局配置实例
settings = Settings()
```

#### 创建环境变量文件

在项目根目录创建 `.env` 文件（记得添加到 `.gitignore`）：

```bash
# 在项目根目录创建 .env 文件
touch .env
```

编辑 `.env`：

```env
# .env

# 应用配置
DEBUG=True

# OpenAI API Key（必需，用于 LLM 功能）
# 如果没有，可以先留空，后面使用模拟模式
OPENAI_API_KEY=sk-your-openai-api-key-here

# 数据库配置（本地开发可以不改）
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=medical_rag

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
```

#### 更新 main.py 使用配置

修改 `backend/main.py`，添加配置导入：

```python
# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings  # ← 新增：导入配置

app = FastAPI(
    title=settings.APP_NAME,  # ← 修改：使用配置
    description="面向转院场景的关键信息智能检索系统",
    version="1.0.0"
)

# ... 中间件配置保持不变 ...

# 修改健康检查端点，添加更多配置信息
@app.get("/health")
def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "debug": settings.DEBUG,
        "api_prefix": settings.API_PREFIX
    }
```

重启服务器（或等待自动重启），再次访问 <http://localhost:8000/health>

✅ **检查点**：响应中应包含 `"debug": true`

---

### Step 5：创建 .gitignore

在项目根目录创建 `.gitignore` 文件，避免提交敏感信息：

```gitignore
# .gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# 环境变量和敏感信息
.env
*.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# 日志文件
*.log
logs/

# 数据库
*.db
*.sqlite

# 数据文件
data/uploads/
data/cache/
data/processed/

# Docker
docker-compose.override.yml

# 系统文件
.DS_Store
Thumbs.db
```

---

## 第二部分：后端开发

### Step 6：数据模型设计

#### 使用 Pydantic 定义数据模型

在 `backend/` 目录下创建 `models.py`：

```python
# backend/models.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

# ============================================
# 枚举类
# ============================================

class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class RecordType(str, Enum):
    OUTPATIENT = "门诊病历"
    INPATIENT = "住院记录"
    EMERGENCY = "急诊记录"
    SURGERY = "手术记录"

class SummaryType(str, Enum):
    TRANSFER = "transfer"
    DISCHARGE = "discharge"
    ADMISSION = "admission"
    PROGRESS = "progress"

# ============================================
# 请求/响应模型
# ============================================

class PatientBase(BaseModel):
    """患者基础信息"""
    patient_id: str = Field(..., description="患者ID")
    name: str = Field(..., description="患者姓名")
    gender: Gender = Field(..., description="性别")
    age: Optional[int] = Field(None, description="年龄")
    phone: Optional[str] = Field(None, description="联系电话")

class PatientCreate(PatientBase):
    """创建患者请求"""
    pass

class PatientResponse(PatientBase):
    """患者响应"""
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MedicalRecordBase(BaseModel):
    """病历基础信息"""
    record_id: str = Field(..., description="记录ID")
    patient_id: str = Field(..., description="患者ID")
    record_type: RecordType = Field(..., description="记录类型")
    department: str = Field(..., description="科室")
    visit_time: datetime = Field(..., description="就诊时间")
    content: str = Field(..., description="病历内容")

class MedicalRecordCreate(MedicalRecordBase):
    """创建病历请求"""
    pass

class MedicalRecordResponse(MedicalRecordBase):
    """病历响应"""
    class Config:
        from_attributes = True

class SearchQuery(BaseModel):
    """搜索查询请求"""
    query: str = Field(..., description="查询内容", min_length=1)
    patient_id: Optional[str] = Field(None, description="患者ID（可选）")
    top_k: int = Field(10, description="返回结果数量", ge=1, le=50)
    enable_time_align: bool = Field(True, description="启用时间语义对齐")

class SearchResult(BaseModel):
    """搜索结果"""
    document: Dict = Field(..., description="文档内容")
    score: float = Field(..., description="相关度分数", ge=0, le=1)
    source: str = Field(..., description="来源（keyword/vector/hybrid）")

class SearchResponse(BaseModel):
    """搜索响应"""
    query: str
    query_info: Dict
    results: List[SearchResult]
    total: int
    time_ms: float

class SummaryRequest(BaseModel):
    """摘要生成请求"""
    patient_id: str = Field(..., description="患者ID")
    summary_type: SummaryType = Field(SummaryType.TRANSFER, description="摘要类型")
    include_sections: List[str] = Field(
        ["chief_complaint", "history", "diagnosis", "treatment"],
        description="包含章节"
    )
    time_window_days: int = Field(30, description="时间窗口（天）")

class SummarySection(BaseModel):
    """摘要章节"""
    title: str
    text: str

class SummaryResponse(BaseModel):
    """摘要生成响应"""
    summary_id: str
    patient_id: str
    summary_type: SummaryType
    sections: Dict[str, SummarySection]
    entities: Optional[Dict] = None
    metadata: Optional[Dict] = None
```

✅ **检查点**：

```bash
# 在 backend/ 目录执行
python -c "from models import PatientBase; print('模型导入成功！')"
```

---

### Step 7：实现内存数据存储

为了快速开发和测试，我们先实现一个内存数据存储（不需要安装数据库）。

在 `backend/` 目录下创建 `data/in_memory_store.py`：

```python
# backend/data/in_memory_store.py

"""
内存数据存储模块
用于开发和测试，无需安装数据库
生产环境应使用 MySQL/Milvus 等真实数据库
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# ============================================
# 全局数据存储
# ============================================

patients_db = {}  # 患者数据
records_db = {}    # 病历数据
summaries_db = {}  # 摘要数据

# ============================================
# 初始化模拟数据
# ============================================

def init_mock_data():
    """初始化模拟数据"""
    
    # 模拟患者数据
    mock_patients = [
        {
            "patient_id": "P00001",
            "name": "张三",
            "gender": "Male",
            "age": 45,
            "phone": "13800138001",
            "address": "北京市海淀区"
        },
        {
            "patient_id": "P00002",
            "name": "李四",
            "gender": "Female",
            "age": 52,
            "phone": "13800138002",
            "address": "上海市浦东新区"
        },
        {
            "patient_id": "P00003",
            "name": "王五",
            "gender": "Male",
            "age": 38,
            "phone": "13800138003",
            "address": "广州市天河区"
        }
    ]
    
    # 模拟病历数据
    mock_records = [
        {
            "record_id": "P00001_REC_001",
            "patient_id": "P00001",
            "record_type": "门诊病历",
            "department": "内分泌科",
            "doctor": "王医生",
            "visit_time": "2023-05-10T09:00:00",
            "content": "患者张三，45岁，因糖尿病复诊就诊。现病史：患者确诊糖尿病5年，目前使用二甲双胍0.5g tid治疗。近期自测空腹血糖7.5-8.5mmol/L，餐后2小时血糖10-12mmol/L。体格检查：BP 145/95mmHg，BMI 26.5。诊断：2型糖尿病，糖尿病控制不佳。处理：1. 继续二甲双胍0.5g tid；2. 加用恩格列净10mg qd；3. 建议低盐低脂饮食，适量运动；4. 1个月后复查糖化血红蛋白。"
        },
        {
            "record_id": "P00001_REC_002",
            "patient_id": "P00001",
            "record_type": "住院记录",
            "department": "心内科",
            "doctor": "李医生",
            "visit_time": "2023-08-15T14:00:00",
            "content": "患者张三，45岁，因胸痛3天入院。主诉：3天前无明显诱因出现胸骨后压榨样疼痛，持续5-10分钟，休息后缓解。既往史：2型糖尿病5年，高血压3年。入院检查：BP 160/100mmHg，心电图提示V1-V4 ST段压低。心肌酶：cTnI 0.8ng/ml（升高）。诊断：急性非ST段抬高型心肌梗死。治疗：阿司匹林100mg qd，氯吡格雷75mg qd，阿托伐他汀40mg qn，低分子肝素4000IU q12h。行冠脉造影示前降支近端70%狭窄，予支架植入术。"
        },
        {
            "record_id": "P00002_REC_001",
            "patient_id": "P00002",
            "record_type": "门诊病历",
            "department": "神经内科",
            "doctor": "赵医生",
            "visit_time": "2023-06-20T10:30:00",
            "content": "患者李四，52岁，因头晕、头痛2周就诊。现病史：患者2周前无明显诱因出现头晕、头痛，以枕部为主，呈持续性胀痛。既往史：高血压10年，最高血压180/110mmHg，目前服用氨氯地平5mg qd，血压控制140-150/90-95mmHg。体格检查：BP 155/98mmHg，神经系统查体未见明显异常。辅助检查：头颅CT未见出血。诊断：原发性高血压3级（很高危）。处理：1. 氨氯地平加量至5mg bid；2. 加用缬沙坦80mg qd；3. 生活方式干预；4. 1周后复查血压。"
        }
    ]
    
    # 存入内存
    for patient in mock_patients:
        patients_db[patient["patient_id"]] = patient
    
    for record in mock_records:
        records_db[record["record_id"]] = record
    
    print(f"[OK] 模拟数据初始化完成：{len(patients_db)} 个患者，{len(records_db)} 条病历")

# ============================================
# 患者相关操作
# ============================================

def get_patient(patient_id: str) -> Optional[Dict]:
    """获取患者信息"""
    return patients_db.get(patient_id)

def search_patients(keyword: str, limit: int = 10) -> List[Dict]:
    """搜索患者"""
    results = []
    for patient in patients_db.values():
        if keyword.lower() in patient["name"].lower() or keyword in patient["patient_id"]:
            results.append(patient)
            if len(results) >= limit:
                break
    return results

def get_patient_records(patient_id: str) -> List[Dict]:
    """获取患者的所有病历"""
    results = []
    for record in records_db.values():
        if record["patient_id"] == patient_id:
            results.append(record)
    
    # 按时间排序
    results.sort(key=lambda x: x["visit_time"])
    return results

# ============================================
# 病历相关操作
# ============================================

def get_record(record_id: str) -> Optional[Dict]:
    """获取病历详情"""
    return records_db.get(record_id)

def search_records(query: str, patient_id: Optional[str] = None, top_k: int = 10) -> List[Dict]:
    """搜索病历（简单关键词匹配）"""
    results = []
    query_lower = query.lower()
    
    for record in records_db.values():
        # 如果指定了患者ID，进行过滤
        if patient_id and record["patient_id"] != patient_id:
            continue
        
        # 简单关键词匹配
        if query_lower in record.get("content", "").lower():
            # 计算简单分数（基于出现次数）
            score = record.get("content", "").lower().count(query_lower) / 10
            score = min(score, 1.0)  # 限制最高1.0
            
            results.append({
                "document": record,
                "score": score,
                "source": "keyword_match"
            })
    
    # 按分数排序
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

# ============================================
# 摘要相关操作
# ============================================

def save_summary(summary: Dict) -> str:
    """保存摘要"""
    summary_id = f"SUM_{summary['patient_id']}_{len(summaries_db) + 1:03d}"
    summary["summary_id"] = summary_id
    summaries_db[summary_id] = summary
    return summary_id

def get_summary(summary_id: str) -> Optional[Dict]:
    """获取摘要"""
    return summaries_db.get(summary_id)

def get_patient_summaries(patient_id: str) -> List[Dict]:
    """获取患者的所有摘要"""
    results = []
    for summary in summaries_db.values():
        if summary["patient_id"] == patient_id:
            results.append(summary)
    return results
```

#### 初始化数据

修改 `backend/main.py`，在启动时初始化数据：

```python
# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from data.in_memory_store import init_mock_data  # ← 新增

# ... app 创建代码 ...

# ============================================
# 启动事件
# ============================================

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    print("=" * 60)
    print(f"🚀 {settings.APP_NAME} 启动中...")
    print("=" * 60)
    
    # 初始化模拟数据
    init_mock_data()
    
    print("✅ 启动完成！")

# ... 其他路由 ...
```

重启服务器，观察启动日志：

```
============================================================
🚀 Medical RAG System 启动中...
============================================================
[OK] 模拟数据初始化完成：3 个患者，3 条病历
✅ 启动完成！
```

✅ **检查点**：访问 <http://localhost:8000/health> 确认服务正常运行

---

### Step 8：实现患者管理 API

在 `backend/` 目录下创建 `api/` 子目录和路由文件：

```bash
mkdir backend/api
touch backend/api/__init__.py
```

创建 `backend/api/routes_patient.py`：

```python
# backend/api/routes_patient.py

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models import PatientResponse
from data.in_memory_store import (
    get_patient,
    search_patients,
    get_patient_records
)

# 创建路由
router = APIRouter()

# ============================================
# 获取患者详情
# ============================================

@router.get("/{patient_id}", response_model=dict)
async def get_patient_detail(patient_id: str):
    """
    获取患者详情
    
    Args:
        patient_id: 患者ID
        
    Returns:
        患者详情 + 就诊记录 + 关键实体
    """
    patient = get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail=f"患者 {patient_id} 不存在")
    
    # 获取就诊记录
    records = get_patient_records(patient_id)
    
    # 构建时间轴
    timeline = []
    for record in records:
        timeline.append({
            "date": record.get("visit_time"),
            "type": record.get("record_type"),
            "department": record.get("department"),
            "doctor": record.get("doctor"),
            "description": record.get("content", "")[:200]
        })
    
    # 模拟实体提取（后面会用 LLM 实现）
    entities = {
        "diseases": [{"name": "2型糖尿病"}],
        "symptoms": [{"name": "头晕"}, {"name": "头痛"}],
        "medications": [{"name": "二甲双胍"}, {"name": "氨氯地平"}]
    }
    
    return {
        "patient": patient,
        "timeline": timeline,
        "entities": entities
    }

# ============================================
# 搜索患者
# ============================================

@router.get("/search", response_model=dict)
async def search_patients_api(
    keyword: str = Query(..., description="搜索关键词"),
    limit: int = Query(10, ge=1, le=50, description="返回数量")
):
    """
    搜索患者
    
    Args:
        keyword: 搜索关键词（姓名或ID）
        limit: 返回数量限制
        
    Returns:
        匹配的患者列表
    """
    results = search_patients(keyword, limit)
    return {
        "patients": results,
        "total": len(results)
    }

# ============================================
# 获取患者时间轴
# ============================================

@router.get("/{patient_id}/timeline", response_model=dict)
async def get_patient_timeline(patient_id: str):
    """
    获取患者时间轴
    
    Args:
        patient_id: 患者ID
        
    Returns:
        按时间排序的就诊事件列表
    """
    patient = get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail=f"患者 {patient_id} 不存在")
    
    records = get_patient_records(patient_id)
    
    timeline = []
    for record in records:
        timeline.append({
            "event_id": record.get("record_id"),
            "date": record.get("visit_time"),
            "title": record.get("record_type"),
            "department": record.get("department"),
            "doctor": record.get("doctor"),
            "summary": record.get("content", "")[:100]
        })
    
    return {
        "patient_id": patient_id,
        "timeline": timeline,
        "total": len(timeline)
    }
```

#### 注册路由

修改 `backend/main.py`，注册患者路由：

```python
# backend/main.py

# ... 其他导入 ...
from api.routes_patient import router as patient_router  # ← 新增

app = FastAPI(...)

# ... CORS 配置 ...

# ============================================
# 注册路由
# ============================================
app.include_router(patient_router, prefix=f"{settings.API_PREFIX}/patient", tags=["患者管理"])

# ... 其他路由 ...
```

重启服务器，访问 <http://localhost:8000/docs，您会看到新的> API 端点！

测试 API：

```bash
# 获取患者详情
curl http://localhost:8000/api/v1/patient/P00001

# 搜索患者
curl "http://localhost:8000/api/v1/patient/search?keyword=张三"
```

✅ **检查点**：

- [ ] 能访问 <http://localhost:8000/docs> 看到 `患者管理` 标签
- [ ] 能成功调用 `GET /api/v1/patient/P00001` 并看到患者详情
- [ ] 能成功调用 `GET /api/v1/patient/search?keyword=张三` 并看到搜索结果

---

**🎉 恭喜！您已经完成了后端基础设施搭建！**

接下来我们将实现最核心的功能：查询检索、时间语义对齐、混合检索、摘要生成，然后开发前端界面，最后用 Docker 部署。

---

## 第二部分（续）：后端核心功能

### Step 9：查询搜索 API 实现

#### 创建查询路由

创建 `backend/api/routes_query.py`：

```python
# backend/api/routes_query.py

from fastapi import APIRouter, HTTPException
from typing import List
from models import SearchQuery, SearchResponse, SearchResult
from data.in_memory_store import search_records
from rag.query_rewriter import rewrite_query
from rag.time_aligner import TimeAligner
from rag.hybrid_search import hybrid_search

router = APIRouter()

@router.post("/search", response_model=SearchResponse)
async def search(query: SearchQuery):
    """
    智能检索接口
    
    流程：Query改写 → 时间语义对齐 → 混合检索 → 结果排序
    """
    # 1. Query 改写
    rewritten = rewrite_query(query.query)
    
    # 2. 时间语义对齐（提取时间约束）
    aligner = TimeAligner()
    time_constraint = aligner.extract_time_constraint(query.query)
    
    # 3. 混合检索
    raw_results = hybrid_search(
        query=rewritten["rewritten_query"],
        patient_id=query.patient_id,
        top_k=query.top_k,
        enable_time_align=query.enable_time_align,
        time_constraint=time_constraint
    )
    
    # 4. 格式化为响应
    results = [
        SearchResult(
            document=r["document"],
            score=r["score"],
            source=r["source"]
        )
        for r in raw_results
    ]
    
    return SearchResponse(
        query=query.query,
        query_info={
            "processed_query": rewritten["rewritten_query"],
            "intent": rewritten["intent"],
            "time_constraint": time_constraint
        },
        results=results,
        total=len(results),
        time_ms=0.0
    )

@router.get("/suggest")
async def suggest(query: str, limit: int = 5):
    """查询建议接口"""
    suggestions = []
    if len(query) >= 2:
        suggestions = [
            {"text": f"{query} 在2023年", "score": 0.9},
            {"text": f"{query} 的诊断记录", "score": 0.85},
            {"text": f"患者{query}的用药情况", "score": 0.8},
        ]
    return {"suggestions": suggestions[:limit]}
```

#### 创建 Query 改写模块

创建 `backend/rag/__init__.py` 和 `backend/rag/query_rewriter.py`：

```python
# backend/rag/query_rewriter.py

import re
from typing import Dict, List

def rewrite_query(query: str) -> Dict:
    """
    Query 改写：理解查询意图，标准化医学术语
    
    Args:
        query: 用户的原始查询
        
    Returns:
        包含改写后查询、意图、实体的字典
    """
    original = query
    intent = "comprehensive_search"
    
    # 意图识别
    if "患者" in query or re.search(r'P\d{5}', query):
        intent = "search_by_patient"
    elif "诊断" in query or "疾病" in query:
        intent = "search_by_disease"
    elif "用药" in query or "药物" in query:
        intent = "search_by_medication"
    
    # 医学术语标准化（简单映射）
    synonym_map = {
        "血糖高": "糖尿病",
        "血压高": "高血压",
        "心梗": "心肌梗死",
        "脑梗": "脑梗死",
    }
    
    rewritten = query
    for k, v in synonym_map.items():
        if k in query:
            rewritten = rewritten.replace(k, v)
    
    return {
        "original_query": original,
        "rewritten_query": rewritten,
        "intent": intent,
        "entities": []
    }
```

#### 创建时间语义对齐模块

创建 `backend/rag/time_aligner.py`：

```python
# backend/rag/time_aligner.py

"""
时间语义对齐模块 - 系统核心创新点
处理医学场景中的复杂时间表达式
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Dict

class TimeAligner:
    """时间语义对齐器"""
    
    def __init__(self):
        self.now = datetime.now()
    
    def extract_time_constraint(self, query: str) -> Optional[Dict]:
        """
        从查询中提取时间约束
        
        支持：
        - 绝对时间：2023年5月、2023/05/10
        - 相对时间：3个月前、上周、去年
        - 事件相对：手术后、入院后第5天
        """
        constraint = None
        
        # 1. 绝对时间：YYYY年MM月
        pattern_year_month = r'(\d{4})年(\d{1,2})月'
        match = re.search(pattern_year_month, query)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            start = datetime(year, month, 1)
            if month == 12:
                end = datetime(year + 1, 1, 1)
            else:
                end = datetime(year, month + 1, 1)
            constraint = {
                "type": "absolute_range",
                "start": start.isoformat(),
                "end": end.isoformat(),
                "raw": match.group(0)
            }
            return constraint
        
        # 2. 相对时间：N个月前 / N天前
        pattern_relative = r'(\d+)\s*(个月|天|周|年)前'
        match = re.search(pattern_relative, query)
        if match:
            num = int(match.group(1))
            unit = match.group(2)
            
            if unit == "个月":
                delta = timedelta(days=num * 30)
            elif unit == "周":
                delta = timedelta(weeks=num)
            elif unit == "天":
                delta = timedelta(days=num)
            else:  # 年
                delta = timedelta(days=num * 365)
            
            end = self.now
            start = self.now - delta
            constraint = {
                "type": "relative_range",
                "start": start.isoformat(),
                "end": end.isoformat(),
                "raw": match.group(0)
            }
            return constraint
        
        # 3. 模糊相对：上周、上月、去年
        fuzzy_map = {
            "上周": timedelta(weeks=1),
            "上个月": timedelta(days=30),
            "去年": timedelta(days=365),
            "前天": timedelta(days=2),
            "昨天": timedelta(days=1),
            "今天": timedelta(days=0),
        }
        for kw, delta in fuzzy_map.items():
            if kw in query:
                start = self.now - delta
                end = self.now if delta.days == 0 else start + timedelta(days=1)
                constraint = {
                    "type": "fuzzy_relative",
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "raw": kw
                }
                return constraint
        
        return constraint

# ============================================
# 使用示例
# ============================================
if __name__ == "__main__":
    aligner = TimeAligner()
    
    test_queries = [
        "患者张三在2023年5月的糖尿病就诊记录",
        "3个月前的复查结果",
        "上周的血压数据",
        "去年的体检报告"
    ]
    
    for q in test_queries:
        result = aligner.extract_time_constraint(q)
        print(f"查询: {q}")
        print(f"  → 时间约束: {result}\n")
```

#### 创建混合检索模块

创建 `backend/rag/hybrid_search.py`：

```python
# backend/rag/hybrid_search.py

"""
混合检索模块
结合关键词检索（BM25）和向量检索（模拟）
使用 RRF（Reciprocal Rank Fusion）融合结果
"""

import math
from typing import List, Dict, Optional

def bm25_score(query_terms: List[str], document: str, avg_dl: float = 200, k1: float = 1.5, b: float = 0.75) -> float:
    """
    BM25 算法实现
    
    Args:
        query_terms: 查询词列表
        document: 文档文本
        avg_dl: 平均文档长度
        k1, b: BM25 参数
    """
    doc_len = len(document)
    score = 0.0
    
    for term in query_terms:
        # 简化：计算词频
        tf = document.lower().count(term.lower())
        if tf == 0:
            continue
        
        # IDF（简化版，假设文档总数 N=100，包含词 t 的文档数 df=10）
        N = 100
        df = 10
        idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
        
        # BM25 公式
        numerator = tf * (k1 + 1)
        denominator = tf + k1 * (1 - b + b * (doc_len / avg_dl))
        score += idf * (numerator / denominator)
    
    return score

def vector_search_sim(query: str, document: str) -> float:
    """
    模拟向量语义检索
    
    真实环境中会使用 Embedding 模型（如 BGE-M3）将文本转为向量，
    然后计算余弦相似度。这里用简单的词汇重叠模拟。
    """
    query_words = set(query.lower().split())
    doc_words = set(document.lower().split())
    
    if not query_words or not doc_words:
        return 0.0
    
    intersection = query_words & doc_words
    union = query_words | doc_words
    
    # Jaccard 相似度作为模拟
    return len(intersection) / len(union)

def rrf_fusion(results_lists: List[List[Dict]], k: int = 60) -> List[Dict]:
    """
    RRF（Reciprocal Rank Fusion）融合多个检索结果
    
    RRF 公式：score = sum(1 / (k + rank))
    不依赖分数绝对值，只依赖排名，鲁棒性好
    """
    fused_scores = {}
    fused_docs = {}
    
    for results in results_lists:
        for rank, item in enumerate(results):
            doc_id = item["document"].get("record_id", str(item))
            if doc_id not in fused_scores:
                fused_scores[doc_id] = 0.0
                fused_docs[doc_id] = item
            
            # RRF 分数
            fused_scores[doc_id] += 1.0 / (k + rank + 1)
    
    # 按融合分数排序
    sorted_docs = sorted(
        fused_docs.items(),
        key=lambda x: fused_scores[x[0]],
        reverse=True
    )
    
    return [
        {**doc, "score": fused_scores[doc_id]}
        for doc_id, doc in sorted_docs
    ]

def hybrid_search(query: str, patient_id: Optional[str] = None, top_k: int = 10,
                 enable_time_align: bool = True, time_constraint: Optional[Dict] = None,
                 documents: List[Dict] = None) -> List[Dict]:
    """
    混合检索主函数
    
    流程：
    1. BM25 关键词检索
    2. 向量语义检索（模拟）
    3. RRF 融合
    4. 时间窗口过滤（可选）
    """
    # 如果没有传入文档，使用内存存储
    if documents is None:
        from data.in_memory_store import records_db
        documents = list(records_db.values())
    
    # 过滤患者
    if patient_id:
        documents = [d for d in documents if d.get("patient_id") == patient_id]
    
    # 时间过滤
    if enable_time_align and time_constraint:
        start = time_constraint.get("start")
        end = time_constraint.get("end")
        if start and end:
            from datetime import datetime
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
            filtered = []
            for d in documents:
                visit_time = d.get("visit_time", "")
                try:
                    vt = datetime.fromisoformat(visit_time)
                    if start_dt <= vt <= end_dt:
                        filtered.append(d)
                except:
                    pass
            documents = filtered if filtered else documents
    
    if not documents:
        return []
    
    # 1. BM25 检索
    query_terms = query.split()
    bm25_results = []
    for doc in documents:
        content = doc.get("content", "")
        score = bm25_score(query_terms, content)
        if score > 0:
            bm25_results.append({"document": doc, "score": score, "source": "bm25"})
    bm25_results.sort(key=lambda x: x["score"], reverse=True)
    
    # 2. 向量检索（模拟）
    vector_results = []
    for doc in documents:
        content = doc.get("content", "")
        sim = vector_search_sim(query, content)
        if sim > 0:
            vector_results.append({"document": doc, "score": sim, "source": "vector"})
    vector_results.sort(key=lambda x: x["score"], reverse=True)
    
    # 3. RRF 融合
    fused = rrf_fusion([bm25_results, vector_results])
    
    return fused[:top_k]
```

#### 注册路由

修改 `backend/main.py`：

```python
# backend/main.py
# ... 已有导入 ...
from api.routes_query import router as query_router  # ← 新增
from api.routes_summary import router as summary_router  # ← 后面会创建

# ... app 创建 ...

app.include_router(query_router, prefix=f"{settings.API_PREFIX}/query", tags=["智能检索"])
app.include_router(summary_router, prefix=f"{settings.API_PREFIX}/summary", tags=["摘要生成"])
app.include_router(patient_router, prefix=f"{settings.API_PREFIX}/patient", tags=["患者管理"])
```

#### 创建摘要路由（占位，Step 12 完善）

创建 `backend/api/routes_summary.py`：

```python
# backend/api/routes_summary.py

from fastapi import APIRouter
from models import SummaryRequest, SummaryResponse
from llm.summary_generator import generate_summary

router = APIRouter()

@router.post("/generate", response_model=SummaryResponse)
async def generate(request: SummaryRequest):
    """生成结构化摘要"""
    summary = generate_summary(request)
    return summary
```

#### 测试搜索功能

重启服务器，测试：

```bash
# 测试混合搜索
curl -X POST http://localhost:8000/api/v1/query/search \
  -H "Content-Type: application/json" \
  -d '{"query": "患者张三在2023年5月的糖尿病就诊记录", "top_k": 5}'
```

**预期输出**应包含 results 数组，每个结果有 score 和 source 字段。

✅ **检查点**：搜索接口返回非空结果，时间约束被正确提取

---

### Step 10：摘要生成实现

创建 `backend/llm/__init__.py` 和 `backend/llm/summary_generator.py`：

```python
# backend/llm/summary_generator.py

"""
摘要生成模块
使用 LLM 生成结构化转院摘要
演示版本使用模拟数据，生产环境接入 OpenAI API
"""

import time
from typing import Dict
from models import SummaryRequest, SummaryResponse, SummarySection
from data.in_memory_store import get_patient_records, save_summary
from config import settings

def build_prompt(patient_id: str, records: list, request: SummaryRequest) -> str:
    """构建 LLM Prompt"""
    prompt = f"""你是一名资深医生，请为以下患者生成{request.summary_type}摘要：

患者ID: {patient_id}
时间窗口: 最近 {request.time_window_days} 天
需要包含章节: {', '.join(request.include_sections)}

相关病历记录：
"""
    for r in records:
        prompt += f"\n[{r.get('visit_time')}] {r.get('record_type')} - {r.get('department')}\n"
        prompt += f"{r.get('content', '')[:500]}\n"
    
    prompt += "\n请按照要求的章节输出结构化摘要（JSON格式）。"
    return prompt

def generate_summary(request: SummaryRequest) -> SummaryResponse:
    """
    生成摘要（主函数）
    
    真实环境中：
    1. 检索患者相关病历
    2. 调用 LLM API（OpenAI）
    3. 解析并验证输出
    4. 返回结构化结果
    """
    # 1. 检索病历
    records = get_patient_records(request.patient_id)
    
    # 2. 构建 Prompt
    prompt = build_prompt(request.patient_id, records, request)
    
    # 3. 模拟 LLM 调用（生产环境替换为真实 API）
    start_time = time.time()
    
    # 模拟生成的摘要内容
    mock_sections = {
        "chief_complaint": SummarySection(
            title="主诉",
            text="患者因胸痛3天入院，伴出汗、气短。"
        ),
        "history": SummarySection(
            title="现病史",
            text="患者3天前无明显诱因出现胸痛，位于胸骨后，呈压榨样，持续5-10分钟，休息后缓解。既往有2型糖尿病5年、高血压3年。"
        ),
        "examination": SummarySection(
            title="体格检查",
            text="BP 160/100mmHg，HR 88次/分，律齐。双肺呼吸音清，未闻及干湿性啰音。"
        ),
        "diagnosis": SummarySection(
            title="诊断",
            text="1. 急性非ST段抬高型心肌梗死\n2. 2型糖尿病\n3. 原发性高血压3级（很高危）"
        ),
        "treatment": SummarySection(
            title="治疗方案",
            text="1. 抗血小板：阿司匹林100mg qd + 氯吡格雷75mg qd\n2. 调脂：阿托伐他汀40mg qn\n3. 抗凝：低分子肝素4000IU q12h\n4. 冠脉造影+支架植入术"
        )
    }
    
    # 只保留请求的章节
    selected_sections = {
        k: v for k, v in mock_sections.items()
        if k in request.include_sections
    }
    
    processing_time = (time.time() - start_time) * 1000
    
    # 4. 构建响应
    summary = SummaryResponse(
        summary_id=f"SUM_{request.patient_id}_{int(time.time())}",
        patient_id=request.patient_id,
        summary_type=request.summary_type,
        sections=selected_sections,
        entities={
            "diseases": [{"name": "急性非ST段抬高型心肌梗死"}, {"name": "2型糖尿病"}],
            "medications": [{"name": "阿司匹林"}, {"name": "氯吡格雷"}]
        },
        metadata={
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model": "demo-model",
            "processing_time_ms": int(processing_time)
        }
    )
    
    # 5. 保存摘要
    save_summary(summary.dict())
    
    return summary
```

#### 测试摘要生成

```bash
curl -X POST http://localhost:8000/api/v1/summary/generate \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "P00001", "summary_type": "transfer", "include_sections": ["chief_complaint", "diagnosis", "treatment"]}'
```

✅ **检查点**：返回包含 sections 的 JSON 摘要

---

### Step 11：演示服务器（零依赖版）

为了方便没有安装依赖的用户快速体验，创建纯标准库版服务器：

创建 `backend/demo_server_simple.py`：

```python
# backend/demo_server_simple.py
"""
零依赖演示服务器 - 使用 Python 内置模块
运行：python demo_server_simple.py
"""

import json
import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# 导入核心模块（如果依赖已安装）
try:
    from data.in_memory_store import patients_db, records_db, init_mock_data
    from rag.query_rewriter import rewrite_query
    from rag.time_aligner import TimeAligner
    from rag.hybrid_search import hybrid_search
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'frontend')

MIME_TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        # 静态文件
        if path == "/" or path.endswith(".html") or "." in path.split("/")[-1]:
            self.serve_static(path)
            return
        
        # API
        if path == "/api/health":
            self.json({"status": "healthy", "version": "1.0.0-demo"})
        elif path.startswith("/api/v1/patient/"):
            pid = path.split("/")[-1]
            if MODULES_AVAILABLE and pid in patients_db:
                self.json({"patient": patients_db[pid]})
            else:
                self.json({"error": "not found"}, 404)
        else:
            self.json({"error": "not found"}, 404)
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8') if length else "{}"
        
        try:
            data = json.loads(body)
        except:
            data = {}
        
        if path == "/api/v1/query/search":
            query = data.get("query", "")
            if MODULES_AVAILABLE:
                rewritten = rewrite_query(query)
                results = hybrid_search(query, data.get("patient_id"), data.get("top_k", 10))
                self.json({
                    "query": query,
                    "query_info": {"processed_query": rewritten["rewritten_query"]},
                    "results": results,
                    "total": len(results)
                })
            else:
                self.json({"error": "modules not available"}, 500)
        else:
            self.json({"error": "not found"}, 404)
    
    def serve_static(self, path):
        if path == "/":
            file_path = os.path.join(FRONTEND_DIR, "index.html")
        else:
            file_path = os.path.join(FRONTEND_DIR, path.lstrip("/"))
        
        if not os.path.isfile(file_path):
            file_path = os.path.join(FRONTEND_DIR, "index.html")
        
        if os.path.isfile(file_path):
            ext = os.path.splitext(file_path)[1]
            mime = MIME_TYPES.get(ext, 'application/octet-stream')
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.json({"error": "file not found"}, 404)
    
    def json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def log_message(self, *args):
        pass

def run_server(port=8000):
    if MODULES_AVAILABLE:
        init_mock_data()
    
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"[OK] Demo server running at http://localhost:{port}")
    print(f"[FRONTEND] {FRONTEND_DIR}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[STOP] Server stopped")

if __name__ == "__main__":
    run_server(8000)
```

**运行方式**：

```bash
cd backend
python demo_server_simple.py
```

✅ **检查点**：访问 <http://localhost:8000> 看到前端首页

---

## 第三部分：前端开发

### Step 12：HTML 结构搭建

#### 创建首页 `frontend/index.html`

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
                <label>患者ID（可选）：<input type="text" id="patientId"></label>
                <label>结果数：<input type="number" id="topK" value="10" min="1" max="50"></label>
                <label><input type="checkbox" id="timeAlign" checked> 时间语义对齐</label>
            </div>
            <div id="suggestions" class="suggestions"></div>
        </section>

        
        <section id="results" class="hidden">
            <h3>检索结果 <span id="resultCount"></span></h3>
            <div id="resultsList"></div>
        </section>

        
        <div id="loading" class="loading hidden">
            <div class="spinner"></div>
            <p>正在检索...</p>
        </div>
    </main>

    <script src="/js/api.js"></script>
    <script src="/js/app.js"></script>
</body>
</html>
```

#### 创建患者详情页 `frontend/patient.html`

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

#### 创建摘要生成页 `frontend/summary.html`

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
            <label>患者ID：<input type="text" id="patientId"></label>
            <label>摘要类型：
                <select id="summaryType">
                    <option value="transfer">转院摘要</option>
                    <option value="discharge">出院小结</option>
                    <option value="admission">入院记录</option>
                </select>
            </label>
            <div id="sections">
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

✅ **检查点**：三个 HTML 文件创建完成

---

### Step 13：CSS 样式设计

创建 `frontend/css/style.css`（医疗主题）：

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
    color: white;
    padding: 1rem 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.header .container { display: flex; align-items: center; justify-content: space-between; }
.header h1 { font-size: 1.4rem; }
.header nav a { color: white; text-decoration: none; margin-left: 1.5rem; opacity: 0.9; }
.header nav a:hover { opacity: 1; }

.card {
    background: var(--card-bg);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin: 1.5rem 0;
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

.options { display: flex; flex-wrap: wrap; gap: 1rem; margin: 1rem 0; }
.options label { display: flex; align-items: center; gap: 0.3rem; font-size: 0.9rem; }

.suggestions { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1rem; }
.suggestion-chip {
    background: #eff6ff; color: var(--primary-dark);
    padding: 0.3rem 0.8rem; border-radius: 20px;
    cursor: pointer; font-size: 0.85rem; transition: background 0.2s;
}
.suggestion-chip:hover { background: var(--primary); color: white; }

.result-item {
    border: 1px solid var(--border); border-radius: var(--radius);
    padding: 1rem; margin: 0.8rem 0; transition: box-shadow 0.2s;
}
.result-item:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.result-header { display: flex; justify-content: space-between; align-items: center; }
.result-title { font-weight: 600; }
.result-score { color: var(--success); font-size: 0.85rem; }
.result-meta { display: flex; flex-wrap: wrap; gap: 1rem; margin: 0.5rem 0; font-size: 0.85rem; color: var(--text-muted); }
.result-content { font-size: 0.9rem; color: var(--text); background: var(--bg); padding: 0.8rem; border-radius: var(--radius); }
.result-highlight { background: #fef08a; font-weight: 600; }

.timeline { border-left: 3px solid var(--primary); margin-left: 1rem; }
.timeline-item { margin: 1rem 0; padding-left: 1.5rem; position: relative; }
.timeline-item::before {
    content: ''; position: absolute; left: -9px; top: 5px;
    width: 12px; height: 12px; background: var(--primary);
    border-radius: 50%;
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

✅ **检查点**：CSS 文件创建完成，定义了医疗主题配色

---

### Step 14：JavaScript 逻辑实现

#### API 通信层 `frontend/js/api.js`

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
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
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

#### 首页逻辑 `frontend/js/app.js`

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

    // 搜索
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
        if (results.length === 0) {
            resultsList.innerHTML = '<p class="text-muted">未找到结果</p>';
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
                            ${doc.visit_time ? `<span>📅 ${doc.visit_time}</span>` : ''}
                        </div>
                        <div class="result-content">${highlight(doc.content || '', query)}</div>
                    </div>
                `;
            }).join('');
        }
        resultCount.textContent = `(${results.length})`;
        resultsSection.classList.remove('hidden');
    }

    function highlight(text, query) {
        if (!text) return '';
        const escaped = text.substring(0, 300).replace(/</g, '&lt;');
        const regex = new RegExp(`(${query})`, 'gi');
        return escaped.replace(regex, '<span class="result-highlight">$1</span>');
    }

    // 事件绑定
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

    // 页面加载检查服务状态
    api.healthCheck()
        .then(() => console.log('服务正常'))
        .catch(() => alert('无法连接后端服务'));
});
```

#### 患者详情页逻辑 `frontend/js/patient.js`

```javascript
// frontend/js/patient.js

document.addEventListener('DOMContentLoaded', () => {
    const loadingEl = document.getElementById('loading');
    const contentEl = document.getElementById('patientContent');
    const nameEl = document.getElementById('patientName');
    const metaEl = document.getElementById('patientMeta');
    const timelineEl = document.getElementById('timeline');
    const entitiesEl = document.getElementById('entities');

    // 从 URL 获取患者 ID
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
                patient.age ? `🎂 ${patient.age}岁` : ''
            ].filter(Boolean).map(t => `<span>${t}</span>`).join(' ');

            // 时间轴
            const timeline = data.timeline || [];
            timelineEl.innerHTML = timeline.map(t => `
                <div class="timeline-item">
                    <div class="timeline-date">${t.date || ''}</div>
                    <div><strong>${t.type || ''}</strong> - ${t.department || ''}</div>
                    <div style="font-size:0.85rem;color:#64748b;">${t.description || ''}</div>
                </div>
            `).join('');

            // 实体
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

#### 摘要生成页逻辑 `frontend/js/summary.js`

```javascript
// frontend/js/summary.js

document.addEventListener('DOMContentLoaded', () => {
    const patientIdInput = document.getElementById('patientId');
    const typeSelect = document.getElementById('summaryType');
    const sectionsEl = document.getElementById('sections');
    const generateBtn = document.getElementById('generateBtn');
    const loadingEl = document.getElementById('loading');
    const resultEl = document.getElementById('result');

    // 从 URL 预填患者 ID
    const params = new URLSearchParams(window.location.search);
    if (params.get('patient_id')) {
        patientIdInput.value = params.get('patient_id');
    }

    generateBtn.addEventListener('click', async () => {
        const patientId = patientIdInput.value.trim();
        if (!patientId) { alert('请输入患者ID'); return; }

        const sections = Array.from(
            sectionsEl.querySelectorAll('input:checked')
        ).map(cb => cb.value);

        loadingEl.classList.remove('hidden');
        resultEl.classList.add('hidden');
        generateBtn.disabled = true;

        try {
            const data = await api.generateSummary(patientId, {
                type: typeSelect.value,
                sections
            });

            // 渲染结果
            let html = '<h2>📋 生成结果</h2>';
            const sections_data = data.sections || {};
            Object.values(sections_data).forEach(sec => {
                html += `
                    <div style="margin:1rem 0;">
                        <h3 style="color:var(--primary-dark);">${sec.title}</h3>
                        <div class="result-content">${sec.text.replace(/\n/g, '<br>')}</div>
                    </div>
                `;
            });

            // 实体
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

✅ **检查点**：所有 JS 文件创建完成

---

## 第四部分：Docker 部署

### Step 15：Dockerfile 编写

#### 后端 Dockerfile `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 前端 Dockerfile `frontend/Dockerfile`

```dockerfile
FROM nginx:alpine

COPY . /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Step 16：Docker Compose 编排

创建 `deploy/docker-compose.yml`：

```yaml
version: '3.8'

services:
  backend:
    build: ../backend
    ports:
      - "8000:8000"
    environment:
      - MYSQL_HOST=mysql
      - REDIS_HOST=redis
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
      - MYSQL_ROOT_PASSWORD=rootpass
      - MYSQL_DATABASE=medical_rag
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

### Step 17：启动部署

```bash
cd deploy
cp .env.example .env
# 编辑 .env 填入 OPENAI_API_KEY
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

✅ **检查点**：访问 <http://localhost> 看到前端，<http://localhost:8000/docs> 看到 API 文档

---

## 第五部分：测试与验证

### Step 18：功能测试清单

启动系统后，按以下顺序测试：

```bash
# 1. 健康检查
curl http://localhost:8000/health

# 2. 搜索测试
curl -X POST http://localhost:8000/api/v1/query/search \
  -H "Content-Type: application/json" \
  -d '{"query": "糖尿病", "top_k": 3}'

# 3. 患者查询
curl http://localhost:8000/api/v1/patient/P00001

# 4. 摘要生成
curl -X POST http://localhost:8000/api/v1/summary/generate \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "P00001", "summary_type": "transfer"}'
```

### Step 19：前端手动测试

1. 打开 <http://localhost:8000>
2. 在搜索框输入"糖尿病"并搜索
3. 点击结果中的"查看患者详情"
4. 在患者页面点击"生成摘要"
5. 确认摘要正常显示

---

## 第六部分：故障排查

### 常见问题

| 问题          | 可能原因          | 解决方案                                                          |
| ----------- | ------------- | ------------------------------------------------------------- |
| 端口被占用       | 8000 已被其他程序使用 | 修改启动端口或关闭占用程序                                                 |
| 模块导入失败      | 虚拟环境未激活或依赖未安装 | `source venv/bin/activate && pip install -r requirements.txt` |
| 前端页面空白      | 静态文件路径错误      | 检查 frontend 目录是否存在 index.html                                 |
| CORS 错误     | 前端域名不在允许列表    | 检查 main.py 中的 CORS 配置                                         |
| Docker 启动失败 | 端口冲突或镜像拉取失败   | `docker-compose down && docker-compose up -d`                 |

### 调试技巧

1. **查看后端日志**：`docker-compose logs -f backend`
2. **交互式调试**：在代码里加 `print()` 或使用 `logging`
3. **API 测试**：直接用浏览器访问 `/docs` 界面测试
4. **前端调试**：按 F12 打开浏览器开发者工具查看 Console

---

## 总结

🎊 **恭喜！您已经完成了整个项目的搭建！**

您现在拥有了一个功能完整的智能病历检索系统，包括：

- ✅ FastAPI 后端（4 个核心模块）
- ✅ 原生 JS 前端（3 个页面）
- ✅ 时间语义对齐算法（核心创新）
- ✅ 混合检索（BM25 + 向量）
- ✅ Docker 部署配置

### 下一步建议

1. **接入真实 LLM**：在 `summary_generator.py` 中替换模拟代码为 OpenAI API 调用
2. **使用真实数据库**：将 `in_memory_store.py` 替换为 MySQL/Milvus 实现
3. **添加用户认证**：使用 JWT 实现登录功能
4. **优化性能**：添加 Redis 缓存、数据库索引

### 参考资源

- FastAPI 官方文档：<https://fastapi.tiangolo.com/>
- Pydantic 文档：<https://docs.pydantic.dev/>
- Docker 文档：<https://docs.docker.com/>
- Milvus 文档：<https://milvus.io/docs>

---

**文档完成！祝您学习愉快！** 🙌

如有问题，欢迎回顾对应 Step 的"检查点"部分进行排查。
