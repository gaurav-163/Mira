"""
Redis Cache Manager for Question-Answer Pairs
Caches responses to speed up repeated questions
"""

import redis
import hashlib
import json
import logging
from typing import Optional, Dict
from datetime import timedelta

logger = logging.getLogger(__name__)


class RedisCacheManager:
    """Manages Redis cache for Q&A pairs"""
    
    def __init__(
        self,
        host: str = '127.0.0.1',
        port: int = 6379,
        password: str = None,
        ttl_hours: int = 24
    ):
        """
        Initialize Redis connection
        
        Args:
            host: Redis host (default: localhost)
            port: Redis port (default: 6379)
            password: Redis password (optional for local instance)
            ttl_hours: Time-to-live for cached entries in hours
        """
        self.ttl = timedelta(hours=ttl_hours)
        self.redis_client = None
        self.enabled = False
        
        try:
            # Connect to local Redis
            connection_params = {
                'host': host,
                'port': port,
                'decode_responses': True,
                'socket_timeout': 5,
                'socket_connect_timeout': 5
            }
            
            # Add password only if provided
            if password:
                connection_params['password'] = password
            
            self.redis_client = redis.Redis(**connection_params)
            
            # Test connection
            self.redis_client.ping()
            self.enabled = True
            logger.info("✅ Redis cache connected successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis cache unavailable: {e}")
            logger.warning("💡 Continuing without cache - responses will not be cached")
            self.enabled = False
    
    def _generate_cache_key(self, question: str) -> str:
        """
        Generate a unique cache key for a question
        
        Args:
            question: User question
            
        Returns:
            SHA256 hash of the normalized question
        """
        # Normalize: lowercase, strip whitespace
        normalized = question.lower().strip()
        
        # Generate hash
        hash_object = hashlib.sha256(normalized.encode())
        cache_key = f"mira:qa:{hash_object.hexdigest()}"
        
        return cache_key
    
    def get_cached_answer(self, question: str) -> Optional[Dict]:
        """
        Retrieve cached answer for a question
        
        Args:
            question: User question
            
        Returns:
            Cached response dict or None if not found
        """
        if not self.enabled:
            return None
        
        try:
            cache_key = self._generate_cache_key(question)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                logger.info(f"🎯 Cache HIT for question: {question[:50]}...")
                response = json.loads(cached_data)
                
                # Add cache indicator
                response['from_cache'] = True
                
                return response
            else:
                logger.info(f"❌ Cache MISS for question: {question[:50]}...")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving from cache: {e}")
            return None
    
    def cache_answer(self, question: str, response: Dict) -> bool:
        """
        Cache a question-answer pair
        
        Args:
            question: User question
            response: Response dictionary to cache
            
        Returns:
            True if cached successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            cache_key = self._generate_cache_key(question)
            
            # Remove cache indicator if present
            response_to_cache = response.copy()
            response_to_cache.pop('from_cache', None)
            
            # Serialize response
            cached_data = json.dumps(response_to_cache)
            
            # Store with TTL
            success = self.redis_client.setex(
                cache_key,
                self.ttl,
                cached_data
            )
            
            if success:
                logger.info(f"💾 Cached answer for: {question[:50]}...")
                return True
            else:
                logger.warning(f"⚠️ Failed to cache answer")
                return False
                
        except Exception as e:
            logger.error(f"Error caching answer: {e}")
            return False
    
    def invalidate_cache(self, question: str = None) -> bool:
        """
        Invalidate cache for a specific question or all cached answers
        
        Args:
            question: Specific question to invalidate (None = clear all)
            
        Returns:
            True if successful
        """
        if not self.enabled:
            return False
        
        try:
            if question:
                # Invalidate specific question
                cache_key = self._generate_cache_key(question)
                deleted = self.redis_client.delete(cache_key)
                logger.info(f"🗑️ Invalidated cache for: {question[:50]}...")
                return deleted > 0
            else:
                # Clear all Mira cache keys
                pattern = "mira:qa:*"
                keys = self.redis_client.keys(pattern)
                
                if keys:
                    deleted = self.redis_client.delete(*keys)
                    logger.info(f"🗑️ Cleared {deleted} cached answers")
                    return True
                else:
                    logger.info("💡 No cache entries to clear")
                    return True
                    
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        if not self.enabled:
            return {
                "enabled": False,
                "message": "Redis cache not available"
            }
        
        try:
            # Count cached entries
            pattern = "mira:qa:*"
            keys = self.redis_client.keys(pattern)
            
            # Get Redis info
            info = self.redis_client.info('stats')
            
            return {
                "enabled": True,
                "cached_answers": len(keys),
                "total_connections": info.get('total_connections_received', 0),
                "total_commands": info.get('total_commands_processed', 0),
                "keyspace_hits": info.get('keyspace_hits', 0),
                "keyspace_misses": info.get('keyspace_misses', 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get('keyspace_hits', 0),
                    info.get('keyspace_misses', 0)
                )
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {
                "enabled": True,
                "error": str(e)
            }
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> str:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        if total == 0:
            return "0%"
        
        rate = (hits / total) * 100
        return f"{rate:.2f}%"
    
    def close(self):
        """Close Redis connection"""
        if self.redis_client:
            try:
                self.redis_client.close()
                logger.info("🔌 Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
