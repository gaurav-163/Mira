"""
Enhanced Semantic RAG with Optimized Search
Implements hybrid search, query expansion, and reranking
"""

import logging
from typing import List, Dict, Tuple, Optional
from langchain_core.documents import Document
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)


class SemanticRAGOptimizer:
    """Enhanced semantic search with multiple optimization techniques"""
    
    def __init__(self, vector_store_manager):
        self.vector_store = vector_store_manager
        self.query_cache = {}  # Simple cache for repeated queries
        
    def hybrid_search(
        self,
        query: str,
        k: int = 10,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[Tuple[Document, float]]:
        """
        Hybrid search combining semantic and keyword matching
        
        Args:
            query: Search query
            k: Number of results
            semantic_weight: Weight for semantic similarity (0-1)
            keyword_weight: Weight for keyword matching (0-1)
        
        Returns:
            List of (Document, combined_score) tuples
        """
        # Check cache first
        cache_key = f"{query}_{k}"
        if cache_key in self.query_cache:
            logger.info("📦 Using cached results")
            return self.query_cache[cache_key]
        
        # Semantic search
        semantic_results = self.vector_store.similarity_search_with_score(query, k=k*2)
        
        if not semantic_results:
            return []
        
        # Normalize semantic scores (convert distance to similarity)
        max_distance = max(score for _, score in semantic_results)
        min_distance = min(score for _, score in semantic_results)
        distance_range = max_distance - min_distance if max_distance != min_distance else 1
        
        scored_docs = {}
        for doc, distance in semantic_results:
            # Convert distance to similarity score (0-1, higher is better)
            semantic_score = 1 - ((distance - min_distance) / distance_range)
            
            # Keyword matching score
            keyword_score = self._keyword_match_score(query, doc.page_content)
            
            # Combined score
            combined_score = (semantic_weight * semantic_score) + (keyword_weight * keyword_score)
            
            doc_id = id(doc)
            if doc_id not in scored_docs or scored_docs[doc_id][1] < combined_score:
                scored_docs[doc_id] = (doc, combined_score)
        
        # Sort by combined score and take top k
        results = sorted(scored_docs.values(), key=lambda x: x[1], reverse=True)[:k]
        
        # Cache results
        self.query_cache[cache_key] = results
        
        return results
    
    def _keyword_match_score(self, query: str, text: str) -> float:
        """
        Calculate keyword matching score using BM25-like approach
        
        Args:
            query: Search query
            text: Document text
        
        Returns:
            Score between 0 and 1
        """
        query_terms = set(query.lower().split())
        text_lower = text.lower()
        text_terms = set(text_lower.split())
        
        if not query_terms:
            return 0.0
        
        # Term frequency
        matches = query_terms.intersection(text_terms)
        if not matches:
            return 0.0
        
        # Calculate match ratio
        match_ratio = len(matches) / len(query_terms)
        
        # Bonus for exact phrase match
        if query.lower() in text_lower:
            match_ratio = min(1.0, match_ratio + 0.3)
        
        return match_ratio
    
    def query_expansion(self, query: str) -> List[str]:
        """
        Expand query with synonyms and related terms
        
        Args:
            query: Original query
        
        Returns:
            List of expanded query variations
        """
        # Simple query expansion - can be enhanced with word embeddings
        expansions = [query]
        
        # Add variations
        query_lower = query.lower()
        
        # Common expansions
        expansion_rules = {
            'what is': ['define', 'explain', 'describe'],
            'how to': ['steps', 'method', 'process', 'procedure'],
            'why': ['reason', 'cause', 'purpose'],
            'difference between': ['compare', 'contrast', 'versus'],
        }
        
        for pattern, additions in expansion_rules.items():
            if pattern in query_lower:
                for addition in additions:
                    expanded = query_lower.replace(pattern, addition)
                    expansions.append(expanded)
        
        return expansions[:3]  # Limit to 3 variations
    
    def multi_query_search(
        self,
        query: str,
        k: int = 5
    ) -> List[Tuple[Document, float]]:
        """
        Search using multiple query variations and merge results
        
        Args:
            query: Original query
            k: Number of final results
        
        Returns:
            List of (Document, score) tuples
        """
        query_variations = self.query_expansion(query)
        logger.info(f"🔍 Searching with {len(query_variations)} query variations")
        
        # Collect results from all variations
        all_results = defaultdict(lambda: {'doc': None, 'scores': []})
        
        for variation in query_variations:
            results = self.hybrid_search(variation, k=k*2)
            
            for doc, score in results:
                doc_content = doc.page_content
                all_results[doc_content]['doc'] = doc
                all_results[doc_content]['scores'].append(score)
        
        # Aggregate scores (average)
        final_results = []
        for doc_data in all_results.values():
            if doc_data['doc']:
                avg_score = np.mean(doc_data['scores'])
                final_results.append((doc_data['doc'], avg_score))
        
        # Sort and return top k
        final_results.sort(key=lambda x: x[1], reverse=True)
        return final_results[:k]
    
    def reciprocal_rank_fusion(
        self,
        query: str,
        k: int = 5,
        k_param: int = 60
    ) -> List[Tuple[Document, float]]:
        """
        Use Reciprocal Rank Fusion to merge multiple search results
        
        Args:
            query: Search query
            k: Number of results
            k_param: RRF parameter (default 60)
        
        Returns:
            List of (Document, RRF_score) tuples
        """
        query_variations = self.query_expansion(query)
        
        # Get ranked lists from different searches
        doc_ranks = defaultdict(list)
        
        for variation in query_variations:
            results = self.hybrid_search(variation, k=k*2)
            
            for rank, (doc, _) in enumerate(results, start=1):
                doc_content = doc.page_content
                doc_ranks[doc_content].append((rank, doc))
        
        # Calculate RRF scores
        rrf_scores = {}
        for doc_content, rank_data in doc_ranks.items():
            rrf_score = sum(1 / (k_param + rank) for rank, _ in rank_data)
            # Use first occurrence for the document
            doc = rank_data[0][1]
            rrf_scores[doc_content] = (doc, rrf_score)
        
        # Sort by RRF score
        results = sorted(rrf_scores.values(), key=lambda x: x[1], reverse=True)
        return results[:k]
    
    def smart_search(
        self,
        query: str,
        k: int = 5,
        use_rrf: bool = True
    ) -> List[Tuple[Document, float]]:
        """
        Intelligent search that chooses best strategy
        
        Args:
            query: Search query
            k: Number of results
            use_rrf: Use Reciprocal Rank Fusion
        
        Returns:
            List of (Document, score) tuples
        """
        logger.info(f"🚀 Smart search for: '{query}'")
        
        # Short queries: use multi-query with expansion
        if len(query.split()) <= 3:
            logger.info("📝 Using multi-query search for short query")
            return self.multi_query_search(query, k=k)
        
        # Long queries: use RRF or hybrid
        if use_rrf:
            logger.info("🔀 Using Reciprocal Rank Fusion")
            return self.reciprocal_rank_fusion(query, k=k)
        else:
            logger.info("🎯 Using hybrid search")
            return self.hybrid_search(query, k=k)
    
    def clear_cache(self):
        """Clear query cache"""
        self.query_cache.clear()
        logger.info("🗑️ Query cache cleared")
