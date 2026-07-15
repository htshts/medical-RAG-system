"""
API 路由 - 摘要生成接口
处理转院摘要生成相关的 API 请求
"""

import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from loguru import logger

# 导入 LLM 生成模块
from llm.summary_generator import summary_generator
from llm.output_validator import output_validator
from rag.hybrid_search import hybrid_search
import numpy as np

router = APIRouter()


class SummaryRequest(BaseModel):
    """摘要生成请求模型"""
    patient_id: str
    query: Optional[str] = None
    include_sections: Optional[List[str]] = None  # 指定包含的章节
    output_format: str = "json"  # json 或 text


class SummaryResponse(BaseModel):
    """摘要生成响应模型"""
    patient_id: str
    summary: Dict  # 结构化的摘要内容
    ner_entities: Optional[Dict] = None  # NER 抽取结果
    confidence_scores: Dict  # 各字段的置信度
    retrieved_docs_count: int
    trace_id: str
    time_ms: float


class FeedbackRequest(BaseModel):
    """反馈请求模型"""
    trace_id: str
    rating: int  # 1-5 评分
    comment: Optional[str] = None
    incorrect_fields: Optional[List[str]] = None


@router.post("/generate", response_model=SummaryResponse)
async def generate_summary(request: SummaryRequest):
    """
    生成转院摘要
    
    核心 LLM 生成接口，实现：
    1. 基于检索结果生成结构化摘要
    2. NER 抽取
    3. 实体链接
    4. 置信度评分
    """
    start_time = time.time()
    trace_id = f"trace_{int(time.time() * 1000)}"
    
    logger.info(f"[{trace_id}] 生成转院摘要: patient_id={request.patient_id}")
    
    try:
        # 1. 检索患者相关信息（使用混合检索）
        logger.info(f"[{trace_id}] 步骤1: 检索患者信息...")
        
        # 构建查询（如果有指定查询，则使用；否则使用默认查询）
        query = request.query or f"患者 {request.patient_id} 的病历摘要"
        
        # 生成查询向量（TODO: 使用 BGE-M3 模型）
        query_embedding = np.random.randn(1024).astype(np.float32)  # 模拟向量
        
        # 执行混合检索
        filter_expr = f"patient_id == '{request.patient_id}'"
        retrieved_docs = hybrid_search.search(
            query=query,
            query_embedding=query_embedding,
            filter_expr=filter_expr,
            top_k=20
        )
        
        # 2. 生成摘要
        logger.info(f"[{trace_id}] 步骤2: 生成摘要...")
        generation_result = summary_generator.generate(
            patient_id=request.patient_id,
            retrieved_docs=retrieved_docs,
            query=request.query
        )
        
        # 3. 校验输出（使用 Pydantic 模型）
        logger.info(f"[{trace_id}] 步骤3: 校验输出...")
        validation_result = output_validator.validate(generation_result.get("summary", {}))
        
        if validation_result["status"] == "success":
            summary = validation_result["data"]
        else:
            logger.warning(f"[{trace_id}] 输出校验失败: {validation_result['errors']}")
            summary = generation_result.get("summary", {})
        
        # 4. 组装响应
        elapsed_time = (time.time() - start_time) * 1000
        
        logger.info(f"[{trace_id}] 摘要生成完成: 耗时 {elapsed_time:.2f}ms")
        
        return SummaryResponse(
            patient_id=request.patient_id,
            summary=summary,
            ner_entities=generation_result.get("ner_entities"),
            confidence_scores=generation_result.get("confidence_scores", {}),
            retrieved_docs_count=generation_result.get("retrieved_docs_count", 0),
            trace_id=trace_id,
            time_ms=elapsed_time
        )
        
    except Exception as e:
        logger.error(f"[{trace_id}] 摘要生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    提交用户反馈
    用于系统优化和评估
    """
    logger.info(f"收到反馈: trace_id={request.trace_id}, rating={request.rating}")
    
    try:
        # TODO: 将反馈存储到 MySQL
        logger.info(f"反馈内容: rating={request.rating}, comment={request.comment}")
        
        return {"status": "success", "message": "反馈已提交"}
        
    except Exception as e:
        logger.error(f"提交反馈失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_summary_templates():
    """
    获取摘要模板列表
    """
    # TODO: 实现模板管理
    logger.info("获取摘要模板列表")
    return {"templates": []}


@router.post("/export")
async def export_summary(patient_id: str, format: str = "pdf"):
    """
    导出摘要（PDF 或 Word 格式）
    """
    logger.info(f"导出摘要: patient_id={patient_id}, format={format}")
    
    try:
        # TODO: 实现摘要导出逻辑
        # 1. 生成摘要
        # 2. 使用报告生成库（如 reportlab）生成 PDF
        # 3. 返回文件下载链接
        
        return {"status": "success", "download_url": ""}
        
    except Exception as e:
        logger.error(f"导出摘要失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
