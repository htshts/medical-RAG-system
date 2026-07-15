"""
输出校验模块
使用 Pydantic 定义输出数据模型，确保 LLM 输出的 JSON 格式正确
"""

import json
import time
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, validator, Field
from loguru import logger


class Medication(BaseModel):
    """药物模型"""
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    start_date: Optional[str] = None


class Examination(BaseModel):
    """检查模型"""
    name: str
    date: Optional[str] = None
    result: Optional[str] = None


class KeyEvent(BaseModel):
    """关键事件模型"""
    time: str
    event: str
    details: Optional[str] = None


class Diagnosis(BaseModel):
    """诊断模型"""
    name: str
    icd_code: Optional[str] = None
    confidence: float = 0.0


class PatientSummary(BaseModel):
    """患者摘要模型（核心输出）"""
    chief_complaint: str = ""
    diagnosis: List[Diagnosis] = Field(default_factory=list)
    key_events: List[KeyEvent] = Field(default_factory=list)
    medications: List[Medication] = Field(default_factory=list)
    examinations: List[Examination] = Field(default_factory=list)
    transfer_recommendation: str = ""


class InformationCompleteness(BaseModel):
    """信息完整度模型"""
    chief_complaint: bool = False
    diagnosis: bool = False
    key_events: bool = False
    medications: bool = False
    examinations: bool = False


class SummaryOutput(BaseModel):
    """摘要输出模型（完整）"""
    patient_summary: PatientSummary
    information_completeness: Optional[InformationCompleteness] = None
    missing_information: Optional[List[str]] = Field(default_factory=list)


class OutputValidator:
    """输出校验器"""
    
    def __init__(self):
        """初始化输出校验器"""
        logger.info("输出校验器初始化完成")
    
    def validate(self, data: Dict) -> Dict:
        """
        校验 LLM 输出
        
        Args:
            data: LLM 输出的字典
            
        Returns:
            Dict: 校验和格式化后的字典
        """
        try:
            # 使用 Pydantic 模型校验
            validated = SummaryOutput(**data)
            
            # 转换为字典
            result = validated.dict()
            
            logger.info("输出校验成功")
            return {
                "status": "success",
                "data": result,
                "errors": []
            }
            
        except Exception as e:
            logger.error(f"输出校验失败: {str(e)}")
            return {
                "status": "error",
                "data": None,
                "errors": [str(e)]
            }
    
    def validate_with_retry(self, llm_call_func, prompt: str, 
                            max_retries: int = 3) -> Dict:
        """
        校验失败自动重试
        
        Args:
            llm_call_func: LLM 调用函数
            prompt: 输入 Prompt
            max_retries: 最大重试次数
            
        Returns:
            Dict: 校验后的输出
        """
        for attempt in range(max_retries):
            try:
                # 调用 LLM
                llm_output = llm_call_func(prompt)
                
                # 尝试解析 JSON
                if isinstance(llm_output, str):
                    data = json.loads(llm_output)
                else:
                    data = llm_output
                
                # 校验
                validation_result = self.validate(data)
                
                if validation_result["status"] == "success":
                    return validation_result
                else:
                    logger.warning(f"校验失败 (尝试 {attempt+1}/{max_retries}): {validation_result['errors']}")
                    
                    # 更新 Prompt，加入错误信息
                    prompt += f"\n\n【上次输出格式错误】\n{validation_result['errors']}\n请修正后重新输出合法的 JSON。"
                    
            except json.JSONDecodeError as e:
                logger.warning(f"JSON 解析失败 (尝试 {attempt+1}/{max_retries}): {str(e)}")
                
                # 更新 Prompt，强调 JSON 格式
                prompt += f"\n\n【上次输出不是合法的 JSON】\n请严格按照 JSON 格式输出，不要有多余的逗号或引号。"
                
            except Exception as e:
                logger.error(f"未知错误 (尝试 {attempt+1}/{max_retries}): {str(e)}")
        
        # 重试次数用尽
        logger.error(f"校验失败，已达到最大重试次数 {max_retries}")
        return {
            "status": "error",
            "data": None,
            "errors": [f"已达到最大重试次数 {max_retries}"]
        }
    
    def calculate_information_completeness(self, summary: Dict) -> Dict:
        """
        计算信息完整度
        
        Args:
            summary: 摘要字典
            
        Returns:
            Dict: 信息完整度评估结果
        """
        patient_summary = summary.get("patient_summary", {})
        
        completeness = {
            "chief_complaint": bool(patient_summary.get("chief_complaint")),
            "diagnosis": bool(patient_summary.get("diagnosis")),
            "key_events": bool(patient_summary.get("key_events")),
            "medications": bool(patient_summary.get("medications")),
            "examinations": bool(patient_summary.get("examinations"))
        }
        
        # 计算完整度得分
        total_fields = len(completeness)
        completed_fields = sum(1 for v in completeness.values() if v)
        completeness_score = completed_fields / total_fields if total_fields > 0 else 0.0
        
        return {
            "completeness": completeness,
            "completeness_score": round(completeness_score, 2),
            "missing_fields": [k for k, v in completeness.items() if not v]
        }


# 全局输出校验器实例
output_validator = OutputValidator()
