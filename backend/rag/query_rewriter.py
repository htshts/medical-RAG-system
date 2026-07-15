"""
Query 理解与改写模块
实现意图识别、医学术语标准化、同义词扩展、LLM 辅助 Query 改写
"""

import re
import json
from typing import List, Dict, Tuple, Optional
from loguru import logger
from config import settings


class QueryRewriter:
    """Query 改写器"""
    
    def __init__(self):
        """初始化 Query 改写器"""
        # 意图分类关键词
        self.intent_keywords = {
            "按患者查": ["患者", "病人", "病历号", "住院号", "patient_id"],
            "按疾病查": ["诊断", "疾病", "病情", "病名", "diagnosis"],
            "按时间查": ["时间", "日期", "入院", "出院", "手术", "检查"],
            "综合查": []
        }
        
        # 医学术语标准化词典（ICD 编码映射）
        self.medical_terms = {
            "心梗": "急性心肌梗死",
            "心肌梗死": "急性心肌梗死",
            "MI": "急性心肌梗死",
            "冠心病": "冠状动脉粥样硬化性心脏病",
            "高血压": "原发性高血压",
            "糖尿病": "2型糖尿病",
            "甲亢": "甲状腺功能亢进",
            "脑梗": "脑梗死",
            "中风": "脑梗死"
        }
        
        # 同义词词典
        self.synonyms = {
            "胸痛": ["胸闷", "胸部不适", "心绞痛"],
            "头痛": ["头疼", "头部不适"],
            "腹痛": ["腹部不适", "肚子痛"],
            "恶心": ["想吐", "反胃"],
            "呕吐": ["吐了", "呕出"]
        }
    
    def understand_query(self, query: str) -> Dict:
        """
        理解 Query（意图识别 + 实体抽取）
        
        Args:
            query: 原始查询文本
            
        Returns:
            Dict: 包含意图、实体、时间表达式等的字典
        """
        result = {
            "original_query": query,
            "intent": self._identify_intent(query),
            "entities": self._extract_entities(query),
            "time_expressions": self._extract_time_expressions(query),
            "rewritten_query": query
        }
        
        logger.info(f"Query 理解结果: {result}")
        return result
    
    def _identify_intent(self, query: str) -> str:
        """
        识别查询意图
        
        Args:
            query: 查询文本
            
        Returns:
            str: 意图类型（按患者查/按疾病查/按时间查/综合查）
        """
        # 简单规则匹配（实际使用时可以用 LLM 辅助）
        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    return intent
        
        # 默认：综合查
        return "综合查"
    
    def _extract_entities(self, query: str) -> List[Dict]:
        """
        抽取医学实体
        
        Args:
            query: 查询文本
            
        Returns:
            List[Dict]: 实体列表，每个实体包含名称和类型
        """
        entities = []
        
        # 匹配患者 ID（简单模式：P + 数字）
        patient_pattern = r"P\d{5}"
        matches = re.findall(patient_pattern, query)
        for match in matches:
            entities.append({
                "name": match,
                "type": "patient_id"
            })
        
        # 匹配医学术语（使用词典）
        for term, standard_term in self.medical_terms.items():
            if term in query:
                entities.append({
                    "name": term,
                    "standard_name": standard_term,
                    "type": "disease"
                })
        
        return entities
    
    def _extract_time_expressions(self, query: str) -> List[str]:
        """
        抽取时间表达式
        
        Args:
            query: 查询文本
            
        Returns:
            List[str]: 时间表达式列表
        """
        time_expressions = []
        
        # 匹配常见时间表达
        patterns = [
            r"\d{4}年\d{1,2}月\d{1,2}日",  # 2024年1月15日
            r"\d{1,2}天前",  # 3天前
            r"入院后第\d+天",  # 入院后第3天
            r"术后\d+周",  # 术后2周
            r"最近\d+天"   # 最近7天
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query)
            time_expressions.extend(matches)
        
        return time_expressions
    
    def rewrite_query(self, query: str) -> Dict:
        """
        改写 Query
        
        Args:
            query: 原始查询文本
            
        Returns:
            Dict: 包含原始查询、改写后查询、意图、实体等的字典
        """
        # 1. 理解 Query
        understanding = self.understand_query(query)
        
        # 2. 医学术语标准化
        standardized_query = self._standardize_medical_terms(query)
        
        # 3. 同义词扩展
        expanded_query = self._expand_synonyms(standardized_query)
        
        # 4. 构建结构化查询
        structured_query = self._build_structured_query(understanding, expanded_query)
        
        result = {
            "original_query": query,
            "standardized_query": standardized_query,
            "expanded_query": expanded_query,
            "structured_query": structured_query,
            "intent": understanding["intent"],
            "entities": understanding["entities"],
            "time_expressions": understanding["time_expressions"]
        }
        
        logger.info(f"Query 改写结果: {result}")
        return result
    
    def _standardize_medical_terms(self, query: str) -> str:
        """
        标准化医学术语
        
        Args:
            query: 查询文本
            
        Returns:
            str: 标准化后的查询文本
        """
        standardized = query
        
        for term, standard_term in self.medical_terms.items():
            if term in standardized:
                # 保留原词，添加标准化词（用空格分隔）
                standardized = standardized.replace(term, f"{term} {standard_term}")
        
        return standardized
    
    def _expand_synonyms(self, query: str) -> str:
        """
        扩展同义词
        
        Args:
            query: 查询文本
            
        Returns:
            str: 扩展后的查询文本
        """
        expanded = query
        
        for term, synonyms in self.synonyms.items():
            if term in expanded:
                # 添加同义词（用空格分隔）
                synonym_str = " ".join(synonyms)
                expanded = f"{expanded} {synonym_str}"
        
        return expanded
    
    def _build_structured_query(self, understanding: Dict, expanded_query: str) -> Dict:
        """
        构建结构化查询
        
        Args:
            understanding: Query 理解结果
            expanded_query: 扩展后的查询文本
            
        Returns:
            Dict: 结构化查询字典
        """
        structured = {
            "must": [],  # 必须满足的条件
            "should": [],  # 应该满足的条件（提升评分）
            "filter": []  # 过滤条件
        }
        
        # 根据意图添加条件
        intent = understanding["intent"]
        
        if intent == "按患者查":
            # 添加患者 ID 过滤
            for entity in understanding["entities"]:
                if entity["type"] == "patient_id":
                    structured["filter"].append({
                        "term": {"patient_id": entity["name"]}
                    })
        
        elif intent == "按疾病查":
            # 添加疾病关键词
            for entity in understanding["entities"]:
                if entity["type"] == "disease":
                    structured["must"].append(entity["standard_name"])
        
        elif intent == "按时间查":
            # 添加时间过滤（需要解析时间表达式）
            # TODO: 实现时间过滤逻辑
            pass
        
        # 添加扩展后的查询文本
        structured["should"].append(expanded_query)
        
        return structured


# 全局 Query 改写器实例
query_rewriter = QueryRewriter()
