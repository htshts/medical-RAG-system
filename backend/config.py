"""
配置管理模块
使用 pydantic-settings 管理环境变量和配置
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    APP_NAME: str = "Medical RAG System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 后端配置
    API_PREFIX: str = "/api"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS 配置
    CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # OpenAI 配置
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: Optional[str] = None  # 自定义 API 基础 URL（用于代理）
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_TEMPERATURE: float = 0.1
    OPENAI_MAX_TOKENS: int = 2000
    
    # Milvus 配置
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION: str = "medical_records"
    MILVUS_DIM: int = 1024  # BGE-M3 向量维度
    
    # Elasticsearch 配置
    ES_HOST: str = "localhost"
    ES_PORT: int = 9200
    ES_INDEX: str = "medical_records"
    
    # MySQL 配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "password"
    MYSQL_DATABASE: str = "medical_rag"
    
    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # 检索配置
    TOP_K: int = 20  # 初步检索返回数量
    TOP_N: int = 5    # 精排后返回数量
    SCORE_THRESHOLD: float = 0.7  # 相关性阈值
    
    # 时间对齐模块配置
    TIME_ALIGNER_ENABLED: bool = True
    TIME_ANCHOR_POINTS: list = ["入院日期", "手术日期", "出院日期", "转院日期"]
    
    # 缓存配置
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600  # 缓存有效期（秒）
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # 权限控制配置
    AUTH_ENABLED: bool = False  # 开发阶段关闭，生产环境开启
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        """Pydantic 配置"""
        env_file = ".env"
        env_file_encoding = "utf-8"


# 创建全局配置实例
settings = Settings()
