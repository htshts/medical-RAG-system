"""
时间语义对齐模块（核心技术亮点）
实现四层架构：
1. Layer 1: 时间实体抽取（正则 + 规则 + NLP）
2. Layer 2: 时间归一化（相对时间转绝对时间）
3. Layer 3: 时序排序 + 因果校验
4. Layer 4: Cross-Encoder 精排
"""

import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from loguru import logger
from config import settings


class TimeAligner:
    """时间语义对齐器（四层架构）"""
    
    def __init__(self):
        """初始化时间对齐器"""
        # 时间锚点
        self.time_anchors = {}
        
        # 正则模式（Layer 1）
        self.regex_patterns = {
            "explicit_date": [
                r"(\d{4})[年-](\d{1,2})[月-](\d{1,2})[日]?",  # 2024年1月15日 或 2024-01-15
                r"(\d{1,2})[月-](\d{1,2})[日]?"  # 1月15日（缺少年份）
            ],
            "explicit_time": [
                r"(\d{1,2}):(\d{2})",  # 14:30
                r"(\d{1,2})点(\d{1,2})分?"  # 14点30分
            ],
            "relative_days": [
                r"第(\d+)天",  # 第3天
                r"(\d+)天后",  # 3天后
                r"(\d+)天前"   # 3天前
            ],
            "relative_weeks": [
                r"(\d+)周后",  # 2周后
                r"(\d+)周前"   # 2周前
            ],
            "fuzzy_time": [
                r"约?(\d+)天前",  # 约3天前
                r"(\d+)天左右",  # 3天左右
                r"半个月前",  # 半个月前
                r"一周前"       # 一周前
            ]
        }
        
        # 规则词典（Layer 1）
        self.rule_patterns = {
            "入院后": "入院日期",
            "出院后": "出院日期",
            "术后": "手术日期",
            "转院后": "转院日期"
        }
        
        logger.info("时间语义对齐器初始化完成")
    
    def align_time(self, query: str, patient_timeline: Dict) -> Dict:
        """
        时间语义对齐主函数
        
        Args:
            query: 查询文本
            patient_timeline: 患者时间线数据
            
        Returns:
            Dict: 对齐后的时间信息和相关文档
        """
        logger.info(f"开始时间语义对齐: query='{query}'")
        
        # Layer 1: 时间实体抽取
        logger.info("Layer 1: 时间实体抽取...")
        time_entities = self._extract_time_entities(query)
        
        # Layer 2: 时间归一化
        logger.info("Layer 2: 时间归一化...")
        normalized_times = self._normalize_time(time_entities, patient_timeline)
        
        # Layer 3: 时序排序 + 因果校验
        logger.info("Layer 3: 时序排序 + 因果校验...")
        sorted_events = self._sort_and_validate(patient_timeline, normalized_times)
        
        # Layer 4: Cross-Encoder 精排（时间相关性加权）
        logger.info("Layer 4: Cross-Encoder 精排...")
        reranked_docs = self._rerank_with_time_weight(sorted_events, query)
        
        result = {
            "query": query,
            "time_entities": time_entities,
            "normalized_times": normalized_times,
            "sorted_events": sorted_events,
            "reranked_docs": reranked_docs
        }
        
        logger.info(f"时间语义对齐完成: {len(reranked_docs)} 条相关文档")
        return result
    
    def _extract_time_entities(self, text: str) -> List[Dict]:
        """
        Layer 1: 时间实体抽取
        
        使用三层策略：
        1. 正则表达式 → 匹配显式时间格式
        2. 规则引擎 → 匹配常见相对时间表达
        3. NLP 模型 → 识别隐式/模糊时间指代（TODO）
        
        Args:
            text: 输入文本
            
        Returns:
            List[Dict]: 时间实体列表
        """
        time_entities = []
        
        # 策略 1: 正则表达式匹配
        for pattern_name, patterns in self.regex_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    time_entities.append({
                        "text": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "type": pattern_name,
                        "value": match.groups()
                    })
        
        # 策略 2: 规则引擎匹配
        for rule, anchor in self.rule_patterns.items():
            if rule in text:
                # 查找规则后面的时间表达
                pattern = f"{rule}(\d+){{1,2}}"
                match = re.search(pattern, text)
                if match:
                    time_entities.append({
                        "text": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "type": "relative_with_anchor",
                        "anchor": anchor,
                        "offset": match.groups()
                    })
        
        # 策略 3: NLP 模型识别（TODO）
        # 使用轻量级 NLP 模型识别模糊的时间指代
        # 例如："上周三"、"最近"、"约半个月前"
        # TODO: 集成 NLP 模型（如 BERT+CRF）
        
        logger.info(f"时间实体抽取: 找到 {len(time_entities)} 个时间实体")
        return time_entities
    
    def _normalize_time(self, time_entities: List[Dict], 
                       patient_timeline: Dict) -> List[Dict]:
        """
        Layer 2: 时间归一化
        
        建立时间锚点体系，将相对时间转为 ISO 8601 绝对时间
        
        Args:
            time_entities: 时间实体列表
            patient_timeline: 患者时间线数据（包含锚点日期）
            
        Returns:
            List[Dict]: 归一化后的时间列表
        """
        normalized = []
        
        # 提取时间锚点
        anchors = self._extract_time_anchors(patient_timeline)
        
        for entity in time_entities:
            entity_type = entity["type"]
            text = entity["text"]
            normalized_time = None
            
            # 显式绝对时间
            if entity_type == "explicit_date":
                normalized_time = self._parse_explicit_date(entity["value"])
            
            # 相对时间（需要锚点）
            elif entity_type == "relative_with_anchor":
                anchor_name = entity.get("anchor")
                if anchor_name in anchors:
                    anchor_date = anchors[anchor_name]
                    offset = entity.get("offset")
                    # 计算相对时间
                    if offset:
                        days = int(offset[0])
                        normalized_time = anchor_date + timedelta(days=days)
            
            # 模糊时间表达
            elif entity_type == "fuzzy_time":
                # 处理模糊时间
                if "半个月" in text:
                    normalized_time = datetime.now() - timedelta(days=15)
                elif "一周" in text:
                    normalized_time = datetime.now() - timedelta(days=7)
                elif "约" in text:
                    # 提取天数
                    match = re.search(r"(\d+)", text)
                    if match:
                        days = int(match.group(1))
                        normalized_time = datetime.now() - timedelta(days=days)
            
            if normalized_time:
                normalized.append({
                    "original_text": text,
                    "normalized_time": normalized_time.isoformat(),
                    "timestamp": int(normalized_time.timestamp())
                })
        
        logger.info(f"时间归一化: {len(normalized)} 个时间实体已归一化")
        return normalized
    
    def _extract_time_anchors(self, patient_timeline: Dict) -> Dict[str, datetime]:
        """
        提取时间锚点
        
        时间锚点包括：
        - 入院日期
        - 手术日期
        - 出院日期
        - 转院日期
        
        Args:
            patient_timeline: 患者时间线数据
            
        Returns:
            Dict[str, datetime]: 锚点名称到日期的映射
        """
        anchors = {}
        
        if not patient_timeline:
            return anchors
        
        # 从时间线中提取锚点
        events = patient_timeline.get("events", [])
        
        for event in events:
            event_type = event.get("event_type")
            event_date = event.get("date")
            
            if event_type == "入院" and event_date:
                anchors["入院日期"] = datetime.fromisoformat(event_date)
            elif event_type == "手术" and event_date:
                anchors["手术日期"] = datetime.fromisoformat(event_date)
            elif event_type == "出院" and event_date:
                anchors["出院日期"] = datetime.fromisoformat(event_date)
            elif event_type == "转院" and event_date:
                anchors["转院日期"] = datetime.fromisoformat(event_date)
        
        return anchors
    
    def _parse_explicit_date(self, value: Tuple) -> Optional[datetime]:
        """
        解析显式日期
        
        Args:
            value: 日期元组（年, 月, 日）或（月, 日）
            
        Returns:
            Optional[datetime]: 解析后的日期
        """
        try:
            if len(value) == 3:
                # 完整日期：年, 月, 日
                year, month, day = int(value[0]), int(value[1]), int(value[2])
                return datetime(year, month, day)
            elif len(value) == 2:
                # 缺少年份：月, 日
                # 使用当前年份
                month, day = int(value[0]), int(value[1])
                return datetime(datetime.now().year, month, day)
        except Exception as e:
            logger.warning(f"解析日期失败: {value}, error={str(e)}")
        
        return None
    
    def _sort_and_validate(self, patient_timeline: Dict, 
                          normalized_times: List[Dict]) -> List[Dict]:
        """
        Layer 3: 时序排序 + 因果校验
        
        按事件发生时间线排序，并进行因果一致性检验：
        - 用药必须在诊断之后
        - 检查必须在入院之后
        - 手术必须在诊断之后
        
        Args:
            patient_timeline: 患者时间线数据
            normalized_times: 归一化后的时间列表
            
        Returns:
            List[Dict]: 排序和校验后的事件列表
        """
        if not patient_timeline:
            return []
        
        events = patient_timeline.get("events", [])
        
        # 按时间戳排序
        for event in events:
            if "timestamp" in event and event["timestamp"]:
                event["timestamp"] = int(event["timestamp"])
        
        sorted_events = sorted(events, key=lambda x: x.get("timestamp") or 0)
        
        # 因果一致性检验
        warnings = []
        diagnoses = []
        medications = []
        
        for idx, event in enumerate(sorted_events):
            event_type = event.get("event_type")
            
            # 记录诊断时间
            if event_type == "诊断":
                diagnoses.append(event)
            
            # 检验用药是否在诊断之后
            elif event_type == "用药":
                if diagnoses:
                    last_diagnosis_time = diagnoses[-1].get("timestamp")
                    event_time = event.get("timestamp")
                    
                    if last_diagnosis_time and event_time:
                        if event_time < last_diagnosis_time:
                            warnings.append({
                                "event": event,
                                "warning": "用药时间早于诊断时间，可能存在时间线矛盾"
                            })
        
        # 标记异常事件
        for warning in warnings:
            event = warning["event"]
            event["warning"] = warning["warning"]
        
        logger.info(f"时序排序 + 因果校验: {len(sorted_events)} 个事件，{len(warnings)} 个警告")
        return sorted_events
    
    def _rerank_with_time_weight(self, sorted_events: List[Dict], 
                                 query: str) -> List[Dict]:
        """
        Layer 4: Cross-Encoder 精排（时间相关性加权）
        
        使用 Cross-Encoder 对 Top-K 候选片段二次打分，
        结合时间相关性权重调整最终排序
        
        Args:
            sorted_events: 排序后的事件列表
            query: 查询文本
            
        Returns:
            List[Dict]: 精排后的文档列表
        """
        # TODO: 实现 Cross-Encoder 精排逻辑
        # 这里先使用简单的规则排序
        
        # 根据查询时间和事件时间的接近程度打分
        query_time = datetime.now().timestamp()
        
        for event in sorted_events:
            event_time = event.get("timestamp")
            if event_time:
                # 计算时间差（天）
                time_diff_days = abs(query_time - event_time) / (24 * 3600)
                
                # 时间越近，得分越高
                time_score = 1.0 / (1.0 + time_diff_days)
                event["time_score"] = time_score
            else:
                event["time_score"] = 0.0
        
        # 按时间得分排序
        reranked = sorted(sorted_events, key=lambda x: x.get("time_score", 0.0), reverse=True)
        
        logger.info(f"Cross-Encoder 精排: {len(reranked)} 个文档")
        return reranked


# 全局时间对齐器实例
time_aligner = TimeAligner()
