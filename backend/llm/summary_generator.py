"""
摘要生成模块
基于检索结果和 NER 抽取，生成结构化的转院摘要
"""

import json
import time
from typing import List, Dict, Optional
from loguru import logger
from config import settings
from .ner_extractor import ner_extractor


class SummaryGenerator:
    """摘要生成器"""
    
    def __init__(self):
        """初始化摘要生成器"""
        # 摘要模板
        self.summary_template = self._load_summary_template()
        
        logger.info("摘要生成器初始化完成")
    
    def generate(self, patient_id: str, retrieved_docs: List[Dict], 
                 query: Optional[str] = None) -> Dict:
        """
        生成转院摘要
        
        Args:
            patient_id: 患者 ID
            retrieved_docs: 检索到的相关文档列表
            query: 原始查询（可选，用于定制化摘要）
            
        Returns:
            Dict: 生成的结构化摘要
        """
        logger.info(f"开始生成转院摘要: patient_id={patient_id}")
        start_time = time.time()
        
        try:
            # 1. 合并检索到的文档内容
            merged_text = self._merge_documents(retrieved_docs)
            
            # 2. NER 抽取关键信息
            ner_result = ner_extractor.extract(merged_text, patient_id)
            entities = ner_result["entities"]
            
            # 3. 构建摘要生成 Prompt
            prompt = self._build_summary_prompt(
                patient_id, merged_text, entities, query
            )
            
            # 4. 调用 LLM 生成摘要
            summary = self._call_llm_for_summary(prompt)
            
            # 5. 校验和格式化输出
            validated_summary = self._validate_and_format(summary)
            
            result = {
                "patient_id": patient_id,
                "summary": validated_summary,
                "ner_entities": entities,
                "confidence_scores": ner_result["confidence_scores"],
                "retrieved_docs_count": len(retrieved_docs),
                "generation_time_ms": int((time.time() - start_time) * 1000)
            }
            
            logger.info(f"摘要生成完成: patient_id={patient_id}")
            return result
            
        except Exception as e:
            logger.error(f"摘要生成失败: {str(e)}")
            return {
                "patient_id": patient_id,
                "summary": {},
                "error": str(e)
            }
    
    def _merge_documents(self, docs: List[Dict]) -> str:
        """
        合并检索到的文档内容
        
        Args:
            docs: 文档列表
            
        Returns:
            str: 合并后的文本
        """
        merged = []
        
        for doc in docs:
            content = doc.get("content", "")
            if content:
                # 添加文档来源标记
                source = doc.get("source", "unknown")
                timestamp = doc.get("timestamp")
                
                doc_text = f"【来源: {source}"
                if timestamp:
                    doc_text += f", 时间: {timestamp}"
                doc_text += f"】\n{content}\n"
                
                merged.append(doc_text)
        
        return "\n".join(merged)
    
    def _build_summary_prompt(self, patient_id: str, text: str, 
                              entities: Dict, query: Optional[str]) -> str:
        """
        构建摘要生成的 Prompt
        
        Args:
            patient_id: 患者 ID
            text: 合并后的文本
            entities: NER 抽取的实体
            query: 原始查询
            
        Returns:
            str: 构建的 Prompt
        """
        prompt = f"""
你是一个专业的医疗摘要生成助手。请根据以下患者病历信息，生成一份结构化的转院摘要。

【患者 ID】
{patient_id}

【原始查询】（如果有）
{query or "无"}

【抽取的实体信息】
{json.dumps(entities, ensure_ascii=False, indent=2)}

【病历全文】
{text}

【输出要求】
请生成一份结构化的转院摘要，严格按照以下 JSON Schema 格式输出：

```json
{{
  "patient_summary": {{
    "chief_complaint": "主诉（字符串）",
    "diagnosis": [
      {{"name": "诊断名称", "icd_code": "ICD编码", "confidence": 0.95}}
    ],
    "key_events": [
      {{"time": "ISO 8601 时间", "event": "事件描述", "details": "详细信息"}}
    ],
    "medications": [
      {{"name": "药物名称", "dosage": "剂量", "frequency": "频率", "start_date": "开始日期"}}
    ],
    "examinations": [
      {{"name": "检查项目", "date": "检查日期", "result": "检查结果"}}
    ],
    "transfer_recommendation": "转院建议（字符串）"
  }},
  "information_completeness": {{
    "chief_complaint": true/false,
    "diagnosis": true/false,
    "key_events": true/false,
    "medications": true/false,
    "examinations": true/false
  }},
  "missing_information": ["缺失的信息类型（如有）"]
}}
```

【生成要求】
1. 只基于病历中的真实信息生成，不要推测或编造
2. 时间格式统一使用 ISO 8601（如：2024-01-15T14:30:00）
3. 诊断必须包含 ICD 编码（如未知则留空字符串）
4. key_events 按时间顺序排列
5. 输出的 JSON 必须是合法的，不要有多余的逗号或引号
6. information_completeness 字段请客观评估各字段的信息完整度
"""
        
        return prompt.strip()
    
    def _call_llm_for_summary(self, prompt: str) -> Dict:
        """
        调用 LLM 生成摘要
        
        Args:
            prompt: 输入 Prompt
            
        Returns:
            Dict: LLM 返回的摘要字典
        """
        # TODO: 实际调用 OpenAI API
        # 这里先返回模拟数据作为占位符
        
        # 模拟 LLM 返回
        mock_summary = {
            "patient_summary": {
                "chief_complaint": "反复胸痛3天",
                "diagnosis": [
                    {"name": "急性心肌梗死", "icd_code": "I21.0", "confidence": 0.95}
                ],
                "key_events": [
                    {"time": "2024-01-10T08:00:00", "event": "入院", "details": "患者因胸痛入院"},
                    {"time": "2024-01-12T14:00:00", "event": "冠脉造影", "details": "提示前降支狭窄90%"}
                ],
                "medications": [
                    {"name": "阿司匹林肠溶片", "dosage": "100mg", "frequency": "每日1次", "start_date": "2024-01-10"}
                ],
                "examinations": [
                    {"name": "心电图", "date": "2024-01-10", "result": "心肌缺血表现"}
                ],
                "transfer_recommendation": "建议转心血管内科CCU进一步治疗"
            },
            "information_completeness": {
                "chief_complaint": True,
                "diagnosis": True,
                "key_events": True,
                "medications": True,
                "examinations": True
            },
            "missing_information": []
        }
        
        logger.warning("使用模拟摘要结果，请实现实际 LLM 调用")
        return mock_summary
    
    def _validate_and_format(self, summary: Dict) -> Dict:
        """
        校验和格式化输出
        
        Args:
            summary: LLM 生成的摘要
            
        Returns:
            Dict: 校验和格式化后的摘要
        """
        # TODO: 实现严格的 JSON Schema 校验
        # 使用 pydantic 模型进行校验
        
        # 简单校验：检查必要字段是否存在
        if "patient_summary" not in summary:
            logger.warning("摘要缺少 patient_summary 字段")
            summary["patient_summary"] = {}
        
        # 确保所有必要字段都存在
        required_fields = [
            "chief_complaint", "diagnosis", "key_events", 
            "medications", "examinations", "transfer_recommendation"
        ]
        
        patient_summary = summary.get("patient_summary", {})
        for field in required_fields:
            if field not in patient_summary:
                patient_summary[field] = [] if field in ["diagnosis", "key_events", "medications", "examinations"] else ""
        
        return summary
    
    def _load_summary_template(self) -> str:
        """
        加载摘要模板
        
        Returns:
            str: 摘要模板文本
        """
        # TODO: 从文件加载模板
        return ""


# 全局摘要生成器实例
summary_generator = SummaryGenerator()
