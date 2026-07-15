"""
API 路由 - 患者信息接口
处理患者信息相关的 API 请求
"""

import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from loguru import logger

# 导入内存存储（演示模式）
from data.in_memory_store import store


router = APIRouter()


class PatientInfo(BaseModel):
    """患者信息模型"""
    patient_id: str
    name: str  # 脱敏后的名称
    gender: str
    age: int
    admissions: List[dict]
    diagnoses: List[str]
    medications: List[str]


class PatientDetail(PatientInfo):
    """患者详细信息模型"""
    medical_history: List[dict]
    test_results: List[dict]
    timeline: List[dict]


@router.get("/{patient_id}", response_model=PatientInfo)
async def get_patient(patient_id: str):
    """
    获取患者基本信息
    """
    logger.info(f"获取患者信息: {patient_id}")
    
    try:
        # 从内存存储查询患者信息
        patient = store.get_patient(patient_id)
        
        if not patient:
            raise HTTPException(status_code=404, detail=f"患者不存在: {patient_id}")
        
        return PatientInfo(
            patient_id=patient["patient_id"],
            name=patient["name"],
            gender=patient["gender"],
            age=patient["age"],
            admissions=patient.get("admissions", []),
            diagnoses=patient.get("diagnoses", []),
            medications=patient.get("medications", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取患者信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{patient_id}/detail", response_model=PatientDetail)
async def get_patient_detail(patient_id: str):
    """
    获取患者完整信息（包含病历时间线）
    """
    logger.info(f"获取患者详细信息: {patient_id}")
    
    try:
        # 获取基本信息
        basic_info = await get_patient(patient_id)
        
        # 获取病历记录
        records = store.get_patient_records(patient_id)
        
        timeline = []
        for record in records:
            timeline.append({
                "record_id": record["record_id"],
                "record_type": record["record_type"],
                "date": record.get("admission_date"),
                "diagnosis": record.get("diagnosis"),
                "content_preview": record["content"][:200] if record.get("content") else ""
            })
        
        return PatientDetail(
            **basic_info.dict(),
            medical_history=[],
            test_results=[],
            timeline=timeline
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取患者详细信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{patient_id}/timeline")
async def get_patient_timeline(patient_id: str):
    """
    获取患者病历时间线（用于时间语义对齐）
    """
    logger.info(f"获取患者时间线: {patient_id}")
    
    try:
        # 获取患者的所有病历记录（按时间排序）
        records = store.get_patient_records(patient_id)
        
        timeline = []
        for record in records:
            timeline.append({
                "record_id": record["record_id"],
                "record_type": record["record_type"],
                "date": record.get("admission_date"),
                "diagnosis": record.get("diagnosis"),
                "content_preview": record["content"][:200] if record.get("content") else ""
            })
        
        return {"patient_id": patient_id, "timeline": timeline}
        
    except Exception as e:
        logger.error(f"获取患者时间线失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_patients(keyword: str, limit: int = 10):
    """
    搜索患者（按 ID 或脱敏名称）
    """
    logger.info(f"搜索患者: {keyword}")
    
    try:
        results = store.search_patients(keyword)
        return {"patients": results[:limit], "total": len(results)}
        
    except Exception as e:
        logger.error(f"搜索患者失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
