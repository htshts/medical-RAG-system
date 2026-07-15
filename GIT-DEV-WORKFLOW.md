# 项目搭建中的 Git 化管理思想 — 实操指南

> **核心理念**：Git 不只是代码备份工具，而是贯穿项目全生命周期的**管理方法论**。  
> 本文以 Medical RAG System 为例，演示如何在项目搭建的每个阶段应用 Git 管理思想。

---

## 目录

- [一、Git 管理思想总览](#一git-管理思想总览)
- [二、分支策略设计](#二分支策略设计)
- [三、提交规范](#三提交规范)
- [四、阶段一：项目初始化的 Git 操作](#四阶段一项目初始化的-git-操作)
- [五、阶段二：数据层开发的 Git 操作](#五阶段二数据层开发的-git-操作)
- [六、阶段三：后端 API 开发的 Git 操作](#六阶段三后端-api-开发的-git-操作)
- [七、阶段四：核心算法的 Git 操作](#七阶段四核心算法的-git-操作)
- [八、阶段五：前端开发的 Git 操作](#八阶段五前端开发的-git-操作)
- [九、阶段六：联调测试的 Git 操作](#九阶段六联调测试的-git-操作)
- [十、阶段七：Docker 部署的 Git 操作](#十阶段七docker-部署的-git-操作)
- [十一、版本发布管理](#十一版本发布管理)
- [十二、团队协作流程](#十二团队协作流程)
- [附录：Git 命令速查表](#附录git-命令速查表)

---

## 一、Git 管理思想总览

### 1.1 为什么要 Git 化管理？

| 场景 | 不用 Git | 用 Git |
|------|---------|--------|
| 代码改坏了 | 无法回退，只能重写 | `git reset` 一秒回退 |
| 多人协作 | 手动合并，冲突频发 | 分支隔离，自动合并 |
| 功能开发中途要修 Bug | 改到一半不敢动 | `git stash` 暂存，切分支修 Bug |
| 想知道某行为什么这样写 | 靠记忆和注释 | `git blame` 查看历史决策 |
| 发版后发现线上有 Bug | 找不到是哪个版本引入的 | `git tag` + `git bisect` 精确定位 |
| 新人入职 | 看代码猜架构 | `git log --graph` 理解演进历史 |

### 1.2 Git 管理的五大原则

```
原则一：小步提交 —— 每个逻辑单元一次提交，不要攒一大堆
原则二：原子提交 —— 一个提交只做一件事，可独立回退
原则三：分支隔离 —— 新功能在分支开发，不污染主干
原则四：提交可读 —— commit message 清晰描述"做了什么"
原则五：频繁同步 —— 每天至少 pull/push 一次，减少冲突
```

### 1.3 Git 在项目生命周期中的角色

```
需求分析 ──→ 技术选型 ──→ 项目初始化 ──→ 开发 ──→ 测试 ──→ 部署 ──→ 维护
    │              │              │           │        │        │        │
   (文档)       (文档)        (仓库创建)  (分支管理) (PR)   (Tag)  (Hotfix)
                                 ↑           ↑        ↑        ↑
                              ──┴───────────┴────────┴────────┘
                              Git 贯穿全程，每个阶段都有对应操作
```

---

## 二、分支策略设计

### 2.1 分支模型（Git Flow 简化版）

本项目采用 **Git Flow 简化版**，适合中小型项目：

```
main (生产环境)
 │
 ├── develop (开发主干)
 │    │
 │    ├── feature/patient-api (患者API功能)
 │    ├── feature/query-search (检索功能)
 │    ├── feature/time-aligner (时间对齐算法)
 │    └── feature/frontend-ui (前端界面)
 │
 ├── hotfix/critical-bug (紧急修复)
 │
 └── release/v1.0.0 (发布分支)
```

### 2.2 分支命名规范

| 分支类型 | 命名格式 | 示例 | 来源 | 合并到 |
|---------|---------|------|------|--------|
| 主干 | `main` | main | — | — |
| 开发主干 | `develop` | develop | main | main |
| 功能分支 | `feature/描述` | feature/patient-api | develop | develop |
| 修复分支 | `fix/描述` | fix/search-bug | develop | develop |
| 紧急修复 | `hotfix/描述` | hotfix/crash-fix | main | main + develop |
| 发布分支 | `release/版本` | release/v1.0.0 | develop | main + develop |

### 2.3 分支生命周期

```
创建分支 ──→ 开发提交 ──→ 自测 ──→ Code Review ──→ 合并 ──→ 删除分支
     ↑                    ↑          ↑              ↑
   有明确任务           频繁提交    通过测试     PR/Review 通过
```

---

## 三、提交规范

### 3.1 Conventional Commits 规范

每个 commit message 遵循以下格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 3.2 Type 类型说明

| Type | 含义 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(patient): 添加患者详情API` |
| `fix` | 修 Bug | `fix(search): 修复时间过滤失效问题` |
| `docs` | 文档 | `docs: 更新README使用说明` |
| `style` | 代码格式 | `style: 统一缩进为4空格` |
| `refactor` | 重构 | `refactor(rag): 抽取混合检索公共方法` |
| `test` | 测试 | `test(time-aligner): 添加相对时间测试用例` |
| `chore` | 构建/工具 | `chore: 添加Docker配置文件` |
| `ci` | CI/CD | `ci: 配置GitHub Actions自动测试` |

### 3.3 提交粒度指南

```
✅ 好的提交：
  feat(patient): 添加患者搜索接口
  feat(patient): 添加患者时间轴接口
  feat(query): 添加Query改写模块

❌ 不好的提交：
  update                  ← 太模糊
  修复了一些bug           ← 哪些bug？
  完成后端开发             ← 粒度太大，包含多个功能
  feat: 添加患者API和检索API和摘要API  ← 违反原子原则
```

---

## 四、阶段一：项目初始化的 Git 操作

### Step 1：在 PyCharm 中初始化 Git 仓库

#### 4.1.1 启用版本控制

1. 打开 PyCharm → 打开项目 `medical-rag-system`
2. 菜单 **VCS → Enable Version Control Integration**
3. 选择 **Git** → OK

PyCharm 底部状态栏出现 `Git: master` 或 `Git: main`，表示初始化成功。

> 💡 PyCharm 会自动创建 `.git` 目录和默认分支。

#### 4.1.2 配置 Git 用户信息

在 PyCharm Terminal（`Alt+F12`）中执行：

```bash
# 设置全局用户名和邮箱（只需一次）
git config --global user.name "你的名字"
git config --global user.email "your_email@example.com"

# 设置默认分支名为 main
git config --global init.defaultBranch main

# 配置中文文件名显示（Windows 需要）
git config --global core.quotepath false

# 验证配置
git config --list
```

### Step 2：创建 .gitignore 文件

右键项目根目录 → New → File → `.gitignore`：

```gitignore
# ============================================
# Python
# ============================================
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
*.egg-info/
dist/
build/

# ============================================
# 环境变量与密钥
# ============================================
.env
.env.local
*.pem
*.key

# ============================================
# IDE（PyCharm）
# ============================================
.idea/
*.iml
*.ipr
*.iws

# ============================================
# 数据库与数据文件
# ============================================
*.db
*.sqlite
*.sqlite3
data/uploads/
data/cache/
data/processed/

# ============================================
# 日志
# ============================================
*.log
logs/

# ============================================
# Docker
# ============================================
docker-compose.override.yml

# ============================================
# 系统文件
# ============================================
.DS_Store
Thumbs.db
desktop.ini

# ============================================
# 临时文件
# ============================================
*.tmp
*.bak
*.swp
*~
```

> ⚠️ **重要**：`.env` 文件包含密码和 API Key，**绝对不能**提交到 Git。

### Step 3：首次提交（Initial Commit）

#### 4.3.1 在 PyCharm 中提交

1. 按 `Ctrl+K`（Mac: `Cmd+K`）打开 Commit 窗口
2. 左侧勾选所有文件（除 `.gitignore` 中排除的）
3. Commit message 输入：

```
chore: 初始化项目结构与Git配置

- 创建项目目录结构（backend/frontend/deploy/tests/data）
- 配置 .gitignore 规则
- 创建 requirements.txt 依赖清单
- 创建 .env 环境变量模板
```

4. 点击 **Commit**

#### 4.3.2 验证提交

```bash
git log --oneline
# 应显示: a1b2c3d chore: 初始化项目结构与Git配置
```

### Step 4：创建 develop 分支

```bash
# 从 main 创建 develop 分支
git checkout -b develop

# 验证当前分支
git branch
# * develop
#   main
```

> 💡 **管理思想**：`main` 分支始终保持可发布状态，所有开发在 `develop` 或功能分支上进行。

### Step 5：创建远程仓库并推送（可选）

```bash
# 在 GitHub/GitLab 创建空仓库后
git remote add origin https://github.com/你的用户名/medical-rag-system.git

# 推送所有分支
git push -u origin main
git push -u origin develop
```

✅ **阶段一 Git 检查点**：
- [ ] Git 仓库已初始化
- [ ] `.gitignore` 已配置
- [ ] 首次提交完成
- [ ] `develop` 分支已创建
- [ ] 远程仓库已关联（可选）

---

## 五、阶段二：数据层开发的 Git 操作

### Step 6：创建功能分支

```bash
# 确保在 develop 分支
git checkout develop

# 创建数据层功能分支
git checkout -b feature/data-layer

# 验证
git branch
# * feature/data-layer
#   develop
#   main
```

> 💡 **管理思想**：每个功能模块在独立分支开发，互不干扰。`develop` 分支始终保持可运行状态。

### Step 7：开发过程中的提交节奏

数据层开发包含三个文件，每个文件完成后提交一次：

#### 提交 1：配置模块

完成 `backend/config.py` 后：

```
按 Ctrl+K → 勾选 config.py → 输入 message:

feat(config): 添加Pydantic配置管理模块

- 支持从.env文件自动加载配置
- 包含数据库、LLM、向量库等配置项
- 类型安全的配置访问
```

#### 提交 2：数据模型

完成 `backend/models.py` 后：

```
feat(models): 定义Pydantic数据模型

- 患者模型（PatientResponse）
- 检索模型（SearchQuery/SearchResponse）
- 摘要模型（SummaryRequest/SummaryResponse）
- 枚举类型定义（Gender/RecordType/SummaryType）
```

#### 提交 3：内存存储

完成 `backend/data/in_memory_store.py` 后：

```
feat(data): 实现内存数据存储层

- 模拟3个患者和3条病历数据
- 支持患者CRUD操作
- 支持病历关键词检索
- 支持摘要保存
```

> 💡 **管理思想**：**小步提交**。不要等三个文件全写完再提交，每个文件完成就提交一次。好处：
> 1. 如果后一个文件写错了，可以精确回退到前一个文件的状态
> 2. `git log` 能清晰反映开发进度
> 3. Code Review 时更容易审查

### Step 8：合并到 develop 分支

数据层开发完成并自测通过后，合并回 `develop`：

```bash
# 1. 切回 develop
git checkout develop

# 2. 合并 feature 分支（--no-ff 保留分支历史）
git merge --no-ff feature/data-layer -m "merge: 合并数据层功能分支"

# 3. 删除已合并的功能分支
git branch -d feature/data-layer

# 4. 查看合并历史
git log --oneline --graph
```

**预期输出**：
```
*   d4e5f6g merge: 合并数据层功能分支
|\
| * c3d4e5f feat(data): 实现内存数据存储层
| * b2c3d4e feat(models): 定义Pydantic数据模型
| * a1b2c3d feat(config): 添加Pydantic配置管理模块
|/
* 9a8b7c6 chore: 初始化项目结构与Git配置
```

> 💡 **管理思想**：`--no-ff` 参数保留分支合并记录，让历史清晰显示"哪些提交属于同一个功能"。这样回溯问题时能快速定位功能边界。

✅ **阶段二 Git 检查点**：
- [ ] 功能分支 `feature/data-layer` 已创建
- [ ] 三个文件分别提交（原子提交）
- [ ] 合并到 `develop` 分支
- [ ] 功能分支已删除
- [ ] `git log --graph` 显示清晰的分支历史

---

## 六、阶段三：后端 API 开发的 Git 操作

### Step 9：创建后端 API 功能分支

```bash
git checkout develop
git checkout -b feature/backend-api
```

### Step 10：FastAPI 应用入口的提交

完成 `backend/main.py` 基础版后：

```
feat(api): 创建FastAPI应用入口

- 配置CORS中间件
- 添加健康检查端点 /health
- 启动时初始化模拟数据
```

**验证后提交**：在 PyCharm 中运行 `main.py`，确认 http://localhost:8000/health 返回正常后再提交。

> 💡 **管理思想**：**提交前必须验证**。不要提交无法运行的代码。每个提交都应该是一个可运行的中间状态。

### Step 11：患者管理 API 的提交

完成 `backend/api/routes_patient.py` 后，先取消 `main.py` 中的路由注释：

```
feat(patient): 添加患者管理API

- GET /patient/{id} 获取患者详情+时间轴+实体
- GET /patient/search 搜索患者
```

### Step 12：查询检索 API 的提交

这个模块包含多个子文件，按完成顺序分别提交：

#### 提交 1：Query 改写

```
feat(rag): 添加Query改写模块

- 意图识别（按患者/疾病/药物检索）
- 医学术语标准化（同义词映射）
```

#### 提交 2：时间语义对齐

```
feat(rag): 实现时间语义对齐算法

- 支持绝对时间解析（2023年5月）
- 支持相对时间解析（3个月前）
- 支持模糊时间解析（上周、去年）
- 返回标准化时间约束区间
```

#### 提交 3：混合检索

```
feat(rag): 实现混合检索引擎

- BM25关键词检索算法
- 模拟向量语义检索（Jaccard相似度）
- RRF融合策略合并多路结果
- 支持时间窗口过滤
```

#### 提交 4：检索路由

```
feat(query): 添加智能检索API

- POST /query/search 混合检索
- GET /query/suggest 查询建议
- 集成时间语义对齐
```

> 💡 **管理思想**：一个功能分支内也可以有多个有意义的提交。每个子模块完成就提交，而不是等整个功能模块完成。

### Step 13：摘要生成 API 的提交

```
feat(summary): 添加摘要生成API

- POST /summary/generate 生成结构化摘要
- 支持自定义章节选择
- 模拟LLM生成（生产环境替换为OpenAI）
```

### Step 14：合并到 develop

```bash
git checkout develop
git merge --no-ff feature/backend-api -m "merge: 合并后端API功能分支"
git branch -d feature/backend-api

# 推送到远程
git push origin develop
```

✅ **阶段三 Git 检查点**：
- [ ] 6 个原子提交（每个 API/模块一次）
- [ ] 每次提交前都运行验证
- [ ] 合并到 develop 后能正常启动
- [ ] 远程仓库已同步

---

## 七、阶段四：核心算法的 Git 操作

### Step 15：创建算法测试分支

```bash
git checkout develop
git checkout -b feature/algorithm-test
```

### Step 16：编写单元测试并提交

完成 `tests/test_rag.py` 后：

```
test(rag): 添加核心算法单元测试

- test_query_rewrite: Query改写测试
- test_time_aligner: 时间语义对齐测试
- test_bm25: BM25算法测试
- test_rrf: RRF融合测试
```

### Step 17：使用 Git Stash 应对中断

**场景**：你正在写测试，突然发现线上有个 Bug 需要立即修复。

```bash
# 1. 暂存当前未完成的工作
git stash push -m "WIP: 添加向量检索测试"

# 2. 查看暂存列表
git stash list
# stash@{0}: On feature/algorithm-test: WIP: 添加向量检索测试

# 3. 切到 main 创建 hotfix 分支
git checkout main
git checkout -b hotfix/search-timeout

# 4. 修复 Bug 并提交
# ... 修改代码 ...
git add .
git commit -m "fix(search): 修复搜索超时问题

增加请求超时设置，避免长时间查询阻塞"

# 5. 合并 hotfix 到 main 和 develop
git checkout main
git merge --no-ff hotfix/search-timeout
git checkout develop
git merge --no-ff hotfix/search-timeout

# 6. 删除 hotfix 分支
git branch -d hotfix/search-timeout

# 7. 回到功能分支，恢复暂存的工作
git checkout feature/algorithm-test
git stash pop

# 8. 继续完成测试...
```

> 💡 **管理思想**：`git stash` 是开发者的"暂停键"。它让你能在不提交半成品代码的前提下，临时切换到其他任务。这是 Git 管理中处理中断的关键技能。

### Step 18：合并算法测试分支

```bash
git checkout develop
git merge --no-ff feature/algorithm-test -m "merge: 合并算法测试分支"
git branch -d feature/algorithm-test
```

✅ **阶段四 Git 检查点**：
- [ ] 单元测试提交完成
- [ ] 掌握 `git stash` 处理中断
- [ ] 掌握 hotfix 分支流程
- [ ] 所有测试通过后才合并

---

## 八、阶段五：前端开发的 Git 操作

### Step 19：创建前端功能分支

```bash
git checkout develop
git checkout -b feature/frontend-ui
```

### Step 20：前端开发的提交节奏

前端包含 HTML、CSS、JS 三类文件，按页面功能提交：

#### 提交 1：HTML 骨架

```
feat(frontend): 搭建三页面HTML骨架

- index.html: 智能检索首页
- patient.html: 患者详情页
- summary.html: 摘要生成页
- 公共导航栏组件
```

#### 提交 2：CSS 样式

```
style(frontend): 添加医疗主题样式

- CSS变量定义（配色、圆角、间距）
- 响应式布局
- 搜索框、卡片、时间轴组件样式
- 加载动画
```

#### 提交 3：API 通信层

```
feat(frontend): 实现API通信层

- 封装ApiClient类
- 统一错误处理
- 支持search/getPatient/generateSummary
```

#### 提交 4：首页逻辑

```
feat(frontend): 实现首页搜索功能

- 搜索请求与结果展示
- 关键词高亮
- 实时查询建议
- 加载状态管理
```

#### 提交 5：患者详情页逻辑

```
feat(frontend): 实现患者详情页

- 从URL参数获取患者ID
- 时间轴组件渲染
- 关键实体标签展示
```

#### 提交 6：摘要生成页逻辑

```
feat(frontend): 实现摘要生成页

- 摘要类型和章节选择
- 生成进度展示
- 结构化结果渲染
```

### Step 21：合并前端分支

```bash
git checkout develop
git merge --no-ff feature/frontend-ui -m "merge: 合并前端界面功能分支"
git branch -d feature/frontend-ui
```

✅ **阶段五 Git 检查点**：
- [ ] 6 个原子提交（按页面/功能）
- [ ] 前端页面在浏览器中正常显示
- [ ] 合并到 develop 分支

---

## 九、阶段六：联调测试的 Git 操作

### Step 22：创建联调分支

```bash
git checkout develop
git checkout -b feature/integration-test
```

### Step 23：演示服务器与联调

完成 `backend/demo_server.py` 后：

```
feat(integration): 添加前后端联调服务器

- 同时服务API和静态文件
- 零配置启动，便于联调
- 修复前端API路径不一致问题
```

### Step 24：发现并修复 Bug 的 Git 操作

**场景**：联调时发现搜索结果的时间显示格式不对。

```bash
# 1. 在当前分支直接修复（小问题不需要新分支）
# ... 修改代码 ...

# 2. 提交修复
git add .
git commit -m "fix(frontend): 修复时间显示格式问题

将ISO时间格式转换为可读的中文日期格式"

# 3. 继续联调...
```

> 💡 **管理思想**：小修复直接在功能分支提交，不需要为每个小 Bug 都创建分支。但如果是严重架构问题，应该新开分支处理。

### Step 25：合并联调分支

```bash
git checkout develop
git merge --no-ff feature/integration-test -m "merge: 合并联调测试分支"
git branch -d feature/integration-test
```

✅ **阶段六 Git 检查点**：
- [ ] 联调服务器正常运行
- [ ] 前后端数据流通畅
- [ ] 发现的 Bug 已修复并提交
- [ ] 合并到 develop 分支

---

## 十、阶段七：Docker 部署的 Git 操作

### Step 26：创建部署分支

```bash
git checkout develop
git checkout -b feature/docker-deploy
```

### Step 27：Docker 配置提交

```
chore(docker): 添加容器化部署配置

- backend/Dockerfile: Python 3.11-slim 镜像
- frontend/Dockerfile: Nginx Alpine 镜像
- docker-compose.yml: 编排4个服务
  - backend (FastAPI)
  - frontend (Nginx)
  - mysql (8.0)
  - redis (7-alpine)
```

### Step 28：创建发布分支

```bash
# 从 develop 创建发布分支
git checkout develop
git checkout -b release/v1.0.0

# 在发布分支上只做版本号更新和文档完善
# ... 更新版本号、完善文档 ...

git add .
git commit -m "release: 准备v1.0.0发布

- 更新版本号至1.0.0
- 完善README文档
- 添加部署说明"
```

### Step 29：合并到 main 并打 Tag

```bash
# 合并 release 到 main
git checkout main
git merge --no-ff release/v1.0.0 -m "merge: 合并v1.0.0发布分支"

# 打版本标签
git tag -a v1.0.0 -m "Medical RAG System v1.0.0

功能:
- 智能病历检索（BM25 + 向量 + RRF）
- 时间语义对齐
- 患者时间轴
- 结构化摘要生成
- Docker一键部署"

# 合并 release 到 develop（保持同步）
git checkout develop
git merge --no-ff release/v1.0.0 -m "merge: 同步v1.0.0到develop"

# 删除 release 分支
git branch -d release/v1.0.0

# 推送标签到远程
git push origin main
git push origin develop
git push origin --tags
```

> 💡 **管理思想**：`release` 分支是从"开发完成"到"正式发布"之间的缓冲区。在这里只做版本号更新、文档完善和最后的 Bug 修复，不再添加新功能。打 Tag 后，这个版本就被永久标记，将来可以随时 `git checkout v1.0.0` 回到这个状态。

✅ **阶段七 Git 检查点**：
- [ ] Docker 配置提交完成
- [ ] release 分支创建
- [ ] 合并到 main 并打 Tag
- [ ] develop 与 main 同步
- [ ] 远程仓库已推送所有分支和标签

---

## 十一、版本发布管理

### 11.1 版本号规范（语义化版本）

```
v<MAJOR>.<MINOR>.<PATCH>

MAJOR: 不兼容的API修改
MINOR: 向下兼容的新功能
PATCH: 向下兼容的Bug修复
```

| 版本变化 | 触发条件 | 示例 |
|---------|---------|------|
| 1.0.0 → 1.0.1 | 修复 Bug | 修复时间过滤失效 |
| 1.0.0 → 1.1.0 | 新增功能 | 添加用户认证 |
| 1.0.0 → 2.0.0 | 破坏性变更 | 重构 API 接口格式 |

### 11.2 发布流程图

```
develop ──────●──────●──────●──────●──────●───→
               \                        /
                \── release/v1.1.0 ────/
                     │           │
                     │           │ 打 Tag
                     ↓           ↓
main ────●───────●───────●(v1.0.0)───●(v1.1.0)─→
```

### 11.3 查看版本历史

```bash
# 查看所有标签
git tag

# 查看标签详情
git show v1.0.0

# 查看两个版本之间的差异
git diff v1.0.0 v1.1.0 --stat

# 查看某个版本的代码
git checkout v1.0.0  # 进入"detached HEAD"状态
git checkout develop  # 返回开发分支
```

### 11.4 线上回滚

**场景**：v1.1.0 上线后发现严重 Bug，需要回滚到 v1.0.0。

```bash
# 方法一：创建 hotfix 分支修复（推荐）
git checkout -b hotfix/rollback-v1.1.0 main
git revert <v1.1.0的合并commit>
git commit -m "revert: 回滚v1.1.0，恢复到v1.0.0稳定版本"
git checkout main
git merge --no-ff hotfix/rollback-v1.1.0
git tag -a v1.1.1 -m "紧急回滚至v1.0.0状态"
git push origin main --tags

# 方法二：直接重置（危险，仅限紧急情况）
git checkout main
git reset --hard v1.0.0
git push --force origin main  # ⚠️ 强制推送，慎用！
```

> ⚠️ **管理思想**：回滚优先用 `git revert`（创建反向提交），而非 `git reset --hard`（删除历史）。revert 保留了完整历史记录，而 reset 会丢失记录。只有在极端紧急情况下才用 force push。

---

## 十二、团队协作流程

### 12.1 Pull Request / Merge Request 工作流

```
1. 开发者创建功能分支
   git checkout -b feature/new-api develop

2. 开发完成后推送到远程
   git push origin feature/new-api

3. 在 GitHub/GitLab 创建 Pull Request
   目标分支: develop
   标题: feat: 添加XXX功能
   描述: 详细说明改动内容

4. 至少一名同事 Code Review

5. CI 自动运行测试

6. Review 通过后合并

7. 删除远程功能分支
```

### 12.2 Code Review 检查清单

```
□ 代码是否符合项目规范？
□ 是否有明显的逻辑错误？
□ 是否有安全隐患（硬编码密码等）？
□ 是否有足够的注释？
□ 是否包含单元测试？
□ commit message 是否清晰？
□ 是否处理了边界情况？
□ 是否有性能问题？
```

### 12.3 处理冲突

```bash
# 拉取最新代码时冲突
git pull origin develop
# CONFLICT (content): Merge conflict in backend/main.py

# 打开冲突文件，手动解决
# <<<<<<< HEAD
# 我的代码
# =======
# 别人的代码
# >>>>>>> origin/develop

# 解决后标记为已解决
git add backend/main.py

# 完成合并
git commit -m "merge: 解决main.py合并冲突"

# 推送
git push origin feature/my-feature
```

### 12.4 日常同步习惯

```bash
# 每天早上开始工作前
git checkout develop
git pull origin develop

# 创建当天的工作分支
git checkout -b feature/today-task

# ... 开发 ...

# 下班前推送到远程（即使没完成）
git add .
git commit -m "WIP: 今日开发进度"
git push origin feature/today-task

# 第二天继续
git checkout feature/today-task
git pull origin feature/today-task
```

> 💡 **管理思想**：每天至少 push 一次。即使代码没写完也要 push，这样：
> 1. 代码有云端备份
> 2. 同事能看到你的进度
> 3. 万一本地环境出问题，代码不丢

---

## 附录：Git 命令速查表

### 基础操作

```bash
git status                    # 查看状态
git add <file>                # 暂存文件
git add .                     # 暂存所有变更
git commit -m "message"       # 提交
git push origin <branch>      # 推送
git pull origin <branch>      # 拉取
git clone <url>               # 克隆仓库
```

### 分支操作

```bash
git branch                    # 查看本地分支
git branch -a                 # 查看所有分支（含远程）
git checkout <branch>         # 切换分支
git checkout -b <new-branch>  # 创建并切换分支
git branch -d <branch>        # 删除已合并分支
git branch -D <branch>        # 强制删除分支
git merge <branch>            # 合并分支
git merge --no-ff <branch>    # 合并（保留分支历史）
```

### 历史查看

```bash
git log                       # 查看提交历史
git log --oneline             # 简洁模式
git log --oneline --graph     # 图形化历史
git log --author="name"       # 按作者过滤
git log --since="2 weeks ago" # 按时间过滤
git show <commit>             # 查看某次提交详情
git blame <file>              # 查看每行最后修改者
git diff                      # 查看未暂存的变更
git diff --staged             # 查看已暂存的变更
```

### 撤销操作

```bash
git checkout -- <file>        # 撤销工作区修改
git reset HEAD <file>         # 撤销暂存
git commit --amend            # 修改最后一次提交
git revert <commit>           # 创建反向提交（安全）
git reset --hard <commit>     # 重置到指定提交（危险）
```

### 暂存操作

```bash
git stash                     # 暂存当前工作
git stash list                # 查看暂存列表
git stash pop                 # 恢复最近的暂存
git stash drop                # 删除最近的暂存
git stash clear               # 清除所有暂存
```

### 标签操作

```bash
git tag                       # 查看所有标签
git tag -a v1.0.0 -m "msg"    # 创建附注标签
git push origin --tags        # 推送所有标签
git push origin v1.0.0        # 推送单个标签
git tag -d v1.0.0             # 删除本地标签
git push origin :refs/tags/v1.0.0  # 删除远程标签
```

### PyCharm 中的 Git 操作对照

| 操作 | 命令行 | PyCharm 快捷键 |
|------|--------|---------------|
| 提交 | `git commit` | `Ctrl+K` |
| 更新 | `git pull` | `Ctrl+T` |
| 推送 | `git push` | `Ctrl+Shift+K` |
| 查看历史 | `git log` | 底部 **Git** 面板 |
| 解决冲突 | 手动编辑 | 弹窗可视化解决 |
| 创建分支 | `git checkout -b` | 右下角分支名 → New |
| 比较差异 | `git diff` | 右键文件 → Git → Compare |

---

## 总结：Git 管理思想的核心

```
┌─────────────────────────────────────────────────┐
│                                                 │
│   分支隔离 ──→ 并行开发互不干扰               │
│   原子提交 ──→ 每次提交可独立回退             │
│   提交规范 ──→ 历史记录清晰可读               │
│   Code Review ──→ 代码质量有保障              │
│   版本标签 ──→ 任意版本可回溯                 │
│   频繁同步 ──→ 团队协作无冲突                 │
│                                                 │
│   Git 不是工具，是项目管理方法论              │
│                                                 │
└─────────────────────────────────────────────────┘
```

**记住**：好的 Git 习惯比好的代码更重要——代码可以重构，但混乱的 Git 历史很难修复。从项目第一天就养成良好的 Git 管理习惯，是专业开发者的基本素养。
