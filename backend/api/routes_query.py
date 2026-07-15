"""
API 路由 - 查询接口
处理检索查询相关的 API 请求
"""

import time
import json
import numpy as np
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from loguru import logger

# 导入 RAG 模块
from rag.query_rewriter import query_rewriter
from rag.hybrid_search import hybrid_search
from rag.time_aligner import time_aligner

router = APIRouter()


class QueryRequest(BaseModel):
    """查询请求模型"""
    query: str
    patient_id: Optional[str] = None
    time_range: Optional[Dict] = None
    top_k: Optional[int] = 20
    filters: Optional[Dict] = None


class SearchResult(BaseModel):
    """检索结果模型"""
    record_id: str
    patient_id: str
    content: str
    score: float
    source: str
    metadata: Optional[Dict] = None


class QueryResponse(BaseModel):
    """查询响应模型"""
    query: str
    rewritten_query: Optional[Dict] = None
    results: List[SearchResult]
    total: int
    time_ms: float
    trace_id: str


@router.post("/search", response_model=QueryResponse)
async def search(request: QueryRequest):
    """
    执行检索查询
    
    核心 RAG 检索接口，实现：
    1. Query 理解与改写
    2. 混合检索（BM25 + 向量检索）
    3. 时间语义对齐
    4. 重排序
    5. 上下文压缩
    """
    start_time = time.time()
    trace_id = f"trace_{int(time.time() * 1000)}"
    
    logger.info(f"[{trace_id}] 收到查询请求: {request.query}")
    
    try:
        # 1. Query 改写
        logger.info(f"[{trace_id}] 步骤1: Query 改写...")
        rewritten = query_rewriter.rewrite_query(request.query)
        
        # 2. 生成查询向量（TODO: 使用 BGE-M3 模型）
        logger.info(f"[{trace_id}] 步骤2: 生成查询向量...")
        query_embedding = np.random.randn(1024).astype(np.float32)  # 模拟向量
        
        # 3. 混合检索
        logger.info(f"[{trace_id}] 步骤3: 混合检索...")
        filter_expr = None
        if request.patient_id:
            filter_expr = f"patient_id == '{request.patient_id}'"
        
        retrieved_docs = hybrid_search.search(
            query=request.query,
            query_embedding=query_embedding,
            filter_expr=filter_expr
        )
        
        # 4. 时间语义对齐（如果查询结果不为空）
        if retrieved_docs and request.patient_id:
            logger.info(f"[{trace_id}] 步骤4: 时间语义对齐...")
            # 获取患者时间线（TODO: 从数据库加载）
            patient_timeline = None  # TODO: 从数据库获取
            
            if patient_timeline:
                time_alignment_result = time_aligner.align_time(
                    query=request.query,
                    patient_timeline=patient_timeline
                )
                # TODO: 根据时间对齐结果调整检索结果排序
        
        # 5. 组装响应
        results = []
        for doc in retrieved_docs:
            results.append(SearchResult(
                record_id=doc.get("record_id") or doc.get("id", ""),
                patient_id=doc.get("patient_id", ""),
                content=doc.get("content", "")[:500],  # 截断长文本
                score=doc.get("rrf_score", doc.get("score", 0.0)),
                source=doc.get("source", "unknown"),
                metadata=doc.get("metadata")
            ))
        
        elapsed_time = (time.time() - start_time) * 1000
        
        logger.info(f"[{trace_id}] 查询完成: {len(results)} 条结果, 耗时 {elapsed_time:.2f}ms")
        
        return QueryResponse(
            query=request.query,
            rewritten_query=rewritten,
            results=results,
            total=len(results),
            time_ms=elapsed_time,
            trace_id=trace_id
        )
        
    except Exception as e:
        logger.error(f"[{trace_id}] 查询失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rewrite")
async def rewrite_query(query: str):
    """
    Query 改写接口
    返回改写后的查询和意图识别结果
    """
    logger.info(f"Query 改写请求: {query}")
    
    try:
        result = query_rewriter.rewrite_query(query)
        return result
    except Exception as e:
        logger.error(f"Query 改写失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_search_history(limit: int = 10, offset: int = 0):
    """获取查询历史"""
    # TODO: 从数据库查询历史记录
    logger.info(f"查询历史: limit={limit}, offset={offset}")
    return {"history": [], "total": 0}
