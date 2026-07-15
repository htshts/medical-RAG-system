"""
API 路由 - 查询接口
处理检索查询相关的 API 请求（演示模式：使用内存存储）
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
from rag.time_aligner import time_aligner

# 导入内存存储（演示模式）
from data.in_memory_store import store


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
    执行检索查询（演示模式）
    
    核心 RAG 检索接口，实现：
    1. Query 理解与改写
    2. 检索（使用内存存储）
    3. 时间语义对齐
    4. 组装响应
    """
    start_time = time.time()
    trace_id = f"trace_{int(time.time() * 1000)}"
    
    logger.info(f"[{trace_id}] 收到查询请求: {request.query}")
    
    try:
        # 1. Query 改写
        logger.info(f"[{trace_id}] 步骤1: Query 改写...")
        rewritten = query_rewriter.rewrite_query(request.query)
        
        # 2. 检索（使用内存存储）
        logger.info(f"[{trace_id}] 步骤2: 检索相关文档...")
        
        # 使用内存存储进行简单关键词匹配
        retrieved_docs = store.search_records(
            query=request.query,
            patient_id=request.patient_id
        )
        
        # 为检索结果添加模拟得分
        for idx, doc in enumerate(retrieved_docs):
            doc["rrf_score"] = 1.0 / (60 + idx + 1)  # RRF 公式
            doc["source"] = "mock_search"
        
        logger.info(f"[{trace_id}] 检索到 {len(retrieved_docs)} 条相关文档")
        
        # 3. 时间语义对齐（如果查询结果不为空）
        if retrieved_docs and request.patient_id:
            logger.info(f"[{trace_id}] 步骤3: 时间语义对齐...")
            
            # 获取患者病历记录
            patient_records = store.get_patient_records(request.patient_id)
            patient_timeline = {"events": []}
            
            for record in patient_records:
                patient_timeline["events"].append({
                    "event_type": record.get("record_type"),
                    "description": record.get("content", "")[:100],
                    "date": record.get("admission_date")
                })
            
            if patient_timeline["events"]:
                time_alignment_result = time_aligner.align_time(
                    query=request.query,
                    patient_timeline=patient_timeline
                )
                logger.info(f"[{trace_id}] 时间对齐完成")
        
        # 4. 组装响应
        results = []
        for doc in retrieved_docs[:10]:  # 只返回前 10 条
            results.append(SearchResult(
                record_id=doc.get("record_id", ""),
                patient_id=doc.get("patient_id", ""),
                content=doc.get("content", "")[:500],  # 截断长文本
                score=doc.get("rrf_score", doc.get("score", 0.0)),
                source=doc.get("source", "unknown"),
                metadata=doc.get("metadata")
            ))
        
        elapsed_time = (time.time() - start_time) * 1000
        
        logger.info(f"[{trace_id}] 查询完成: {len(results)} 条结果, 耗时 {elapsed_time:.2f}ms")
        
        # 记录查询日志
        store.add_query_log(
            trace_id=trace_id,
            query=request.query,
            patient_id=request.patient_id,
            response_time_ms=int(elapsed_time),
            result_count=len(results)
        )
        
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
    logger.info(f"查询历史: limit={limit}, offset={offset}")
    
    # 从内存存储获取查询历史
    history = store.queries[offset:offset+limit]
    return {"history": history, "total": len(store.queries)}
