"""
混合检索模块
实现 BM25 关键词检索 + 向量语义检索 + RRF 融合策略
"""

import numpy as np
from typing import List, Dict, Optional
from loguru import logger
from config import settings

# 导入数据客户端
from data.milvus_client import milvus_client
from data.es_client import es_client


class HybridSearch:
    """混合检索器"""
    
    def __init__(self):
        """初始化混合检索器"""
        self.top_k = settings.TOP_K
        self.top_n = settings.TOP_N
        self.score_threshold = settings.SCORE_THRESHOLD
        
        # RRF 融合参数
        self.rf_k = 60  # RRF 公式中的 k 值
        
        logger.info(f"混合检索器初始化完成: top_k={self.top_k}, top_n={self.top_n}")
    
    def search(self, query: str, query_embedding: np.ndarray, 
              filter_expr: Optional[str] = None, 
              time_filter: Optional[Dict] = None) -> List[Dict]:
        """
        执行混合检索
        
        Args:
            query: 查询文本
            query_embedding: 查询向量（numpy 数组）
            filter_expr: 过滤表达式（可选）
            time_filter: 时间过滤条件（可选）
            
        Returns:
            List[Dict]: 融合后的检索结果列表
        """
        logger.info(f"开始混合检索: query='{query}', top_k={self.top_k}")
        
        # 1. BM25 关键词检索
        logger.info("步骤1: BM25 关键词检索...")
        bm25_results = self._bm25_search(query, self.top_k * 2)
        
        # 2. 向量语义检索
        logger.info("步骤2: 向量语义检索...")
        vector_results = self._vector_search(query_embedding, self.top_k * 2, filter_expr)
        
        # 3. RRF 融合
        logger.info("步骤3: RRF 融合...")
        fused_results = self._rrf_fusion(bm25_results, vector_results)
        
        # 4. 时间过滤（可选）
        if time_filter:
            logger.info("步骤4: 时间过滤...")
            fused_results = self._apply_time_filter(fused_results, time_filter)
        
        # 5. 重排序（精排）
        logger.info("步骤5: 重排序...")
        reranked_results = self._rerank(fused_results, query, query_embedding)
        
        # 6. 返回 Top-N 结果
        final_results = reranked_results[:self.top_n]
        
        logger.info(f"混合检索完成: 返回 {len(final_results)} 条结果")
        return final_results
    
    def _bm25_search(self, query: str, top_k: int) -> List[Dict]:
        """
        BM25 关键词检索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            List[Dict]: BM25 检索结果列表
        """
        try:
            results = es_client.search(query, top_k)
            
            # 添加来源标记
            for result in results:
                result["source"] = "bm25"
            
            logger.info(f"BM25 检索返回 {len(results)} 条结果")
            return results
            
        except Exception as e:
            logger.error(f"BM25 检索失败: {str(e)}")
            return []
    
    def _vector_search(self, query_embedding: np.ndarray, top_k: int, 
                     filter_expr: Optional[str] = None) -> List[Dict]:
        """
        向量语义检索
        
        Args:
            query_embedding: 查询向量
            top_k: 返回结果数量
            filter_expr: 过滤表达式
            
        Returns:
            List[Dict]: 向量检索结果列表
        """
        try:
            results = milvus_client.search(query_embedding, top_k, filter_expr)
            
            # 添加来源标记
            for result in results:
                result["source"] = "vector"
            
            logger.info(f"向量检索返回 {len(results)} 条结果")
            return results
            
        except Exception as e:
            logger.error(f"向量检索失败: {str(e)}")
            return []
    
    def _rrf_fusion(self, bm25_results: List[Dict], vector_results: List[Dict]) -> List[Dict]:
        """
        RRF (Reciprocal Rank Fusion) 融合
        
        公式：score = Σ 1/(k + rank_i)
        含义：每条结果在不同检索路的排名越靠前，融合得分越高
        
        Args:
            bm25_results: BM25 检索结果
            vector_results: 向量检索结果
            
        Returns:
            List[Dict]: 融合后的结果列表（按 RRF 得分排序）
        """
        # 构建结果 ID 到排名的映射
        bm25_ranks = {}
        for idx, result in enumerate(bm25_results):
            result_id = result.get("record_id") or result.get("id")
            bm25_ranks[result_id] = idx + 1  # 排名从 1 开始
        
        vector_ranks = {}
        for idx, result in enumerate(vector_results):
            result_id = result.get("record_id") or result.get("id")
            vector_ranks[result_id] = idx + 1
        
        # 计算 RRF 得分
        all_result_ids = set(bm25_ranks.keys()) | set(vector_ranks.keys())
        fused_scores = {}
        
        for result_id in all_result_ids:
            score = 0.0
            
            # BM25 排名贡献
            if result_id in bm25_ranks:
                rank = bm25_ranks[result_id]
                score += 1.0 / (self.rf_k + rank)
            
            # 向量排名贡献
            if result_id in vector_ranks:
                rank = vector_ranks[result_id]
                score += 1.0 / (self.rf_k + rank)
            
            fused_scores[result_id] = score
        
        # 按 RRF 得分排序
        sorted_ids = sorted(fused_scores.keys(), key=lambda x: fused_scores[x], reverse=True)
        
        # 构建融合结果列表
        fused_results = []
        all_results = {r.get("record_id") or r.get("id"): r for r in bm25_results + vector_results}
        
        for result_id in sorted_ids:
            if result_id in all_results:
                result = all_results[result_id].copy()
                result["rrf_score"] = fused_scores[result_id]
                fused_results.append(result)
        
        logger.info(f"RRF 融合完成: {len(fused_results)} 条结果")
        return fused_results
    
    def _apply_time_filter(self, results: List[Dict], time_filter: Dict) -> List[Dict]:
        """
        应用时间过滤
        
        Args:
            results: 检索结果列表
            time_filter: 时间过滤条件
            
        Returns:
            List[Dict]: 过滤后的结果列表
        """
        # TODO: 实现时间过滤逻辑
        # 示例：过滤指定时间范围内的结果
        
        filtered_results = []
        for result in results:
            timestamp = result.get("timestamp")
            if not timestamp:
                continue
            
            # 检查是否在时间范围内
            # TODO: 实现具体的时间过滤逻辑
            
            filtered_results.append(result)
        
        logger.info(f"时间过滤: {len(results)} -> {len(filtered_results)} 条结果")
        return filtered_results
    
    def _rerank(self, results: List[Dict], query: str, 
                query_embedding: np.ndarray) -> List[Dict]:
        """
        重排序（精排）
        
        使用 Cross-Encoder 对 Top-K 候选片段二次打分
        
        Args:
            results: 检索结果列表
            query: 查询文本
            query_embedding: 查询向量
            
        Returns:
            List[Dict]: 重排序后的结果列表
        """
        # TODO: 实现 Cross-Encoder 精排逻辑
        # 这里先使用简单的 RRF 得分排序
        
        reranked = sorted(results, key=lambda x: x.get("rrf_score", 0.0), reverse=True)
        
        logger.info(f"重排序完成: {len(reranked)} 条结果")
        return reranked


# 全局混合检索器实例
hybrid_search = HybridSearch()
