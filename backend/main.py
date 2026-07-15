"""
FastAPI 应用入口
医疗RAG系统 - 面向转院场景的关键信息智能检索系统
"""

import sys
import os

# 将项目根目录添加到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import uvicorn

from config import settings

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    description="基于 RAG 架构的医疗信息系统，帮助医生在转院会诊时快速检索患者病历中的关键信息",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"调试模式: {settings.DEBUG}")
    
    # 创建必要的目录
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    # TODO: 初始化数据库连接
    # TODO: 初始化 Milvus 客户端
    # TODO: 初始化 Elasticsearch 客户端
    # TODO: 初始化 Redis 客户端
    
    logger.info("应用启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("应用正在关闭...")
    # TODO: 关闭数据库连接
    logger.info("应用已关闭")


@app.get("/")
async def root():
    """根路径 - 健康检查"""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}


# 注册 API 路由
from api.routes_query import router as query_router
from api.routes_patient import router as patient_router
from api.routes_summary import router as summary_router

app.include_router(query_router, prefix=f"{settings.API_PREFIX}/query")
app.include_router(patient_router, prefix=f"{settings.API_PREFIX}/patient")
app.include_router(summary_router, prefix=f"{settings.API_PREFIX}/summary")


if __name__ == "__main__":
    """直接运行时的入口"""
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
