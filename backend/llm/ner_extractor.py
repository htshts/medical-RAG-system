"""
NER 抽取模块
基于 LLM 的关键信息抽取（疾病、用药、检查、症状等实体）
"""

import json
import time
from typing import List, Dict, Optional
from loguru import logger
from config import settings


class NERExtractor:
    """命名实体识别（NER）抽取器"""
    
    def __init__(self):
        """初始化 NER 抽取器"""
        # 实体类型定义
        self.entity_types = [
            "疾病", "症状", "药物", "检查", "手术", 
            "解剖部位", "时间", "剂量", "频率"
        ]
        
        # Few-shot 示例（用于 Prompt）
        self.few_shot_examples = self._load_few_shot_examples()
        
        logger.info("NER 抽取器初始化完成")
    
    def extract(self, text: str, patient_id: Optional[str] = None) -> Dict:
        """
        从文本中抽取关键实体
        
        Args:
            text: 输入文本（病历内容）
            patient_id: 患者 ID（可选，用于上下文）
            
        Returns:
            Dict: 抽取的实体字典，按类型分组
        """
        logger.info(f"开始 NER 抽取: text_length={len(text)}")
        start_time = time.time()
        
        # 构建 Prompt
        prompt = self._build_prompt(text)
        
        # 调用 LLM 进行实体抽取
        try:
            entities = self._call_llm_for_ner(prompt)
            
            # 实体链接（映射到标准 ICD 编码）
            linked_entities = self._link_entities(entities)
            
            # 计算置信度
            confidence_scores = self._calculate_confidence(entities, text)
            
            result = {
                "entities": linked_entities,
                "confidence_scores": confidence_scores,
                "extraction_time_ms": int((time.time() - start_time) * 1000)
            }
            
            logger.info(f"NER 抽取完成: 找到 {sum(len(v) for v in linked_entities.values())} 个实体")
            return result
            
        except Exception as e:
            logger.error(f"NER 抽取失败: {str(e)}")
            return {
                "entities": {},
                "confidence_scores": {},
                "error": str(e)
            }
    
    def _build_prompt(self, text: str) -> str:
        """
        构建 NER 抽取的 Prompt
        
        Args:
            text: 输入文本
            
        Returns:
            str: 构建的 Prompt
        """
        prompt = f"""
你是一个专业的医疗信息抽取助手。请从以下病历文本中抽取关键信息。

【抽取实体类型】
{', '.join(self.entity_types)}

【输出格式】
请严格按照以下 JSON 格式输出，不要输出任何其他内容：
```json
{{
  "疾病": [{{"name": "疾病名称", "icd_code": "ICD编码（如未知则为空）", "confidence": 0.95}}],
  "症状": [{{"name": "症状名称", "onset_time": "出现时间（如已知）", "confidence": 0.90}}],
  "药物": [{{"name": "药物名称", "dosage": "剂量", "frequency": "频率", "confidence": 0.85}}],
  "检查": [{{"name": "检查项目名称", "result": "检查结果", "confidence": 0.90}}],
  "手术": [{{"name": "手术名称", "date": "手术日期", "confidence": 0.95}}]
}}
```

【Few-shot 示例】
{self.few_shot_examples}

【待抽取文本】
{text}

【要求】
1. 只抽取文本中明确提到的信息，不要推测或编造
2. 每个实体都要给出置信度（0.0-1.0）
3. 如果某个类型的实体不存在，返回空列表 []
4. 输出的 JSON 必须是合法的，不要有多余的逗号或引号
"""
        
        return prompt.strip()
    
    def _call_llm_for_ner(self, prompt: str) -> Dict:
        """
        调用 LLM 进行 NER 抽取
        
        Args:
            prompt: 输入 Prompt
            
        Returns:
            Dict: LLM 返回的实体字典
        """
        # TODO: 实际调用 OpenAI API
        # 这里先返回模拟数据作为占位符
        
        # 模拟 LLM 返回
        mock_entities = {
            "疾病": [
                {"name": "急性心肌梗死", "icd_code": "I21.0", "confidence": 0.95}
            ],
            "症状": [
                {"name": "胸痛", "onset_time": "3天前", "confidence": 0.90}
            ],
            "药物": [
                {"name": "阿司匹林肠溶片", "dosage": "100mg", "frequency": "每日1次", "confidence": 0.85}
            ]
        }
        
        logger.warning("使用模拟 NER 结果，请实现实际 LLM 调用")
        return mock_entities
    
    def _link_entities(self, entities: Dict) -> Dict:
        """
        实体链接（映射到标准 ICD 编码）
        
        Args:
            entities: 抽取的实体字典
            
        Returns:
            Dict: 链接后的实体字典（添加 icd_code 字段）
        """
        # ICD 编码映射词典（简化版）
        icd_mapping = {
            "急性心肌梗死": "I21.0",
            "不稳定型心绞痛": "I20.0",
            "高血压": "I10",
            "2型糖尿病": "E11",
            "脑梗死": "I63",
            "社区获得性肺炎": "J15",
            "慢性阻塞性肺疾病": "J44"
        }
        
        linked = entities.copy()
        
        # 为疾病实体添加 ICD 编码
        if "疾病" in linked:
            for disease in linked["疾病"]:
                if "icd_code" not in disease or not disease["icd_code"]:
                    disease_name = disease.get("name", "")
                    if disease_name in icd_mapping:
                        disease["icd_code"] = icd_mapping[disease_name]
        
        return linked
    
    def _calculate_confidence(self, entities: Dict, text: str) -> Dict:
        """
        计算每个实体的置信度
        
        Args:
            entities: 抽取的实体字典
            text: 原始文本
            
        Returns:
            Dict: 置信度字典（按实体类型分组）
        """
        confidence_scores = {}
        
        for entity_type, entity_list in entities.items():
            if isinstance(entity_list, list) and entity_list:
                # 计算该类型实体的平均置信度
                avg_confidence = sum(
                    e.get("confidence", 0.0) for e in entity_list
                ) / len(entity_list)
                
                confidence_scores[entity_type] = {
                    "average": round(avg_confidence, 2),
                    "min": min(e.get("confidence", 0.0) for e in entity_list),
                    "max": max(e.get("confidence", 0.0) for e in entity_list)
                }
        
        return confidence_scores
    
    def _load_few_shot_examples(self) -> str:
        """
        加载 Few-shot 示例
        
        Returns:
            str: 格式化的 Few-shot 示例文本
        """
        examples = """
示例 1:
输入文本：患者因"胸痛3天"入院。既往高血压病史10年，口服阿司匹林肠溶片100mg qd控制血压。入院后查心电图提示心肌缺血表现。
输出：
```json
{{
  "疾病": [{"name": "急性心肌梗死", "icd_code": "I21.0", "confidence": 0.95}],
  "症状": [{"name": "胸痛", "onset_time": "3天前", "confidence": 0.90}],
  "药物": [{"name": "阿司匹林肠溶片", "dosage": "100mg", "frequency": "qd", "confidence": 0.85}]
}}
```

示例 2:
输入文本：患者头部CT提示脑梗死征象。给予静脉溶栓治疗后病情好转。既往糖尿病病史5年。
输出：
```json
{{
  "疾病": [{"name": "脑梗死", "icd_code": "I63", "confidence": 0.95}],
  "症状": [],
  "药物": [],
  "检查": [{"name": "头部CT", "result": "脑梗死征象", "confidence": 0.90}]
}}
```
"""
        
        return examples


# 全局 NER 抽取器实例
ner_extractor = NERExtractor()
