import logging
import os
import json
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from collections import defaultdict, deque
from typing import Dict, List, Optional
import time
import statistics
import threading
from .cache import CacheManager

logger = logging.getLogger(__name__)

class PerformanceLogHandler(RotatingFileHandler):
    def __init__(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        super().__init__(
            filename,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
    def format(self, record):
        """Format the log record as JSON with additional performance metrics"""
        data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'path': getattr(record, 'path', None),
            'method': getattr(record, 'method', None),
            'duration': getattr(record, 'duration', None),
            'status_code': getattr(record, 'status_code', None),
            'request_id': getattr(record, 'request_id', None),
            'message': record.getMessage()
        }
        
        # Add any extra performance metrics
        if hasattr(record, 'metrics'):
            data['metrics'] = record.metrics
            
        return json.dumps(data)

def setup_performance_logging():
    """Setup performance logging configuration"""
    logger = logging.getLogger('performance')
    logger.setLevel(logging.INFO)
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Add performance log handler
    handler = PerformanceLogHandler(
        os.path.join(log_dir, 'performance.log')
    )
    logger.addHandler(handler)
    
    return logger

# Create global logger instance
performance_logger = setup_performance_logging()

class PerformanceLogger:
    def __init__(self, window_size: int = 3600, cache: Optional[CacheManager] = None):
        self._metrics = defaultdict(lambda: {
            "response_times": deque(maxlen=window_size),
            "error_counts": deque(maxlen=window_size),
            "request_counts": deque(maxlen=window_size),
            "timestamps": deque(maxlen=window_size)
        })
        self._lock = threading.Lock()
        self.cache = cache
        self.cache_prefix = "timeline:metrics:"

    def log_request(self, endpoint: str, response_time: float, is_error: bool = False):
        """记录请求性能数据"""
        with self._lock:
            now = datetime.now()
            timestamp = now.timestamp()
            
            # Store in local metrics
            self._metrics[endpoint]["response_times"].append(response_time)
            self._metrics[endpoint]["error_counts"].append(1 if is_error else 0)
            self._metrics[endpoint]["request_counts"].append(1)
            self._metrics[endpoint]["timestamps"].append(now)
            
            # Store in Redis if available
            if self.cache:
                try:
                    metric_key = f"{self.cache_prefix}{endpoint}"
                    metric_data = {
                        "timestamp": timestamp,
                        "response_time": response_time,
                        "is_error": is_error
                    }
                    self.cache.set(
                        f"{metric_key}:{timestamp}",
                        metric_data,
                        ttl=3600  # 1 hour TTL
                    )
                except Exception as e:
                    logger.error(f"Failed to store metrics in cache: {str(e)}")

    def get_metrics(self, endpoint: str = None) -> Dict:
        """获取性能指标统计，结合Redis和内存中的数据"""
        with self._lock:
            # 获取内存中的指标
            in_memory_metrics = {}
            if endpoint:
                in_memory_metrics = self._calculate_endpoint_metrics(endpoint)
            else:
                for ep in self._metrics.keys():
                    in_memory_metrics[ep] = self._calculate_endpoint_metrics(ep)
            
            # 如果没有Redis缓存，直接返回内存指标
            if not self.cache:
                return in_memory_metrics
                
            # 从Redis获取指标并合并
            redis_metrics = {}
            try:
                if endpoint:
                    # 获取单个端点的Redis指标
                    pattern = f"{self.cache_prefix}{endpoint}:*"
                    keys = self.cache.client.keys(pattern)
                    redis_data = [self.cache.get(k) for k in keys]
                    redis_metrics = self._calculate_redis_metrics(endpoint, redis_data)
                else:
                    # 获取所有端点的Redis指标
                    pattern = f"{self.cache_prefix}*"
                    keys = self.cache.client.keys(pattern)
                    endpoints = set(k.decode().split(':')[2] for k in keys)
                    for ep in endpoints:
                        ep_keys = [k for k in keys if k.decode().endswith(f":{ep}:*")]
                        redis_data = [self.cache.get(k) for k in ep_keys]
                        redis_metrics[ep] = self._calculate_redis_metrics(ep, redis_data)
            except Exception as e:
                logger.error(f"Failed to get metrics from Redis: {str(e)}")
                return in_memory_metrics
            
            # 合并内存和Redis指标
            if endpoint:
                return self._merge_metrics(in_memory_metrics, redis_metrics)
            else:
                merged = {}
                all_endpoints = set(in_memory_metrics.keys()) | set(redis_metrics.keys())
                for ep in all_endpoints:
                    merged[ep] = self._merge_metrics(
                        in_memory_metrics.get(ep, {}),
                        redis_metrics.get(ep, {})
                    )
                return merged

    def _calculate_endpoint_metrics(self, endpoint: str) -> Dict:
        """计算单个端点的性能指标"""
        if endpoint not in self._metrics:
            return {}

        data = self._metrics[endpoint]
        if not data["response_times"]:
            return {}

        # 计算基本统计数据
        response_times = list(data["response_times"])
        error_count = sum(data["error_counts"])
        request_count = sum(data["request_counts"])

        try:
            metrics = {
                "average_response_time": statistics.mean(response_times),
                "p95_response_time": statistics.quantiles(response_times, n=20)[18],  # 95th percentile
                "max_response_time": max(response_times),
                "min_response_time": min(response_times),
                "request_count": request_count,
                "error_rate": error_count / request_count if request_count > 0 else 0,
                "requests_per_second": self._calculate_request_rate(data["timestamps"])
            }
        except Exception as e:
            logger.error(f"Error calculating metrics for endpoint {endpoint}: {str(e)}")
            metrics = {
                "average_response_time": 0,
                "p95_response_time": 0,
                "max_response_time": 0,
                "min_response_time": 0,
                "request_count": 0,
                "error_rate": 0,
                "requests_per_second": 0
            }

        return metrics

    def _calculate_redis_metrics(self, endpoint: str, redis_data: List[Dict]) -> Dict:
        """Calculate metrics from Redis data"""
        if not redis_data:
            return {}
            
        response_times = [d["response_time"] for d in redis_data if d]
        error_count = sum(1 for d in redis_data if d and d.get("is_error"))
        request_count = len(redis_data)
        timestamps = [d["timestamp"] for d in redis_data if d]
        
        if not response_times:
            return {}
            
        try:
            return {
                "average_response_time": statistics.mean(response_times),
                "p95_response_time": statistics.quantiles(response_times, n=20)[18],
                "max_response_time": max(response_times),
                "min_response_time": min(response_times),
                "request_count": request_count,
                "error_rate": error_count / request_count if request_count > 0 else 0,
                "requests_per_second": self._calculate_request_rate(timestamps)
            }
        except Exception as e:
            logger.error(f"Error calculating Redis metrics: {str(e)}")
            return {}

    def _merge_metrics(self, mem_metrics: Dict, redis_metrics: Dict) -> Dict:
        """Merge in-memory and Redis metrics"""
        if not mem_metrics and not redis_metrics:
            return {}
            
        if not mem_metrics:
            return redis_metrics
            
        if not redis_metrics:
            return mem_metrics
            
        # Calculate weighted averages based on request counts
        mem_count = mem_metrics.get("request_count", 0)
        redis_count = redis_metrics.get("request_count", 0)
        total_count = mem_count + redis_count
        
        if total_count == 0:
            return mem_metrics
            
        return {
            "average_response_time": (
                mem_metrics["average_response_time"] * mem_count + 
                redis_metrics["average_response_time"] * redis_count
            ) / total_count,
            "p95_response_time": max(
                mem_metrics["p95_response_time"],
                redis_metrics["p95_response_time"]
            ),
            "max_response_time": max(
                mem_metrics["max_response_time"],
                redis_metrics["max_response_time"]
            ),
            "min_response_time": min(
                mem_metrics["min_response_time"],
                redis_metrics["min_response_time"]
            ),
            "request_count": total_count,
            "error_rate": (
                mem_metrics["error_rate"] * mem_count + 
                redis_metrics["error_rate"] * redis_count
            ) / total_count,
            "requests_per_second": (
                mem_metrics["requests_per_second"] + 
                redis_metrics["requests_per_second"]
            )
        }

    def _calculate_request_rate(self, timestamps: deque) -> float:
        """计算请求频率（每秒请求数）"""
        if len(timestamps) < 2:
            return 0

        newest = max(timestamps)
        oldest = min(timestamps)
        time_span = (newest - oldest).total_seconds()
        if time_span == 0:
            return 0

        return len(timestamps) / time_span

    def clear_old_data(self, max_age: timedelta = timedelta(hours=1)):
        """清理旧数据"""
        with self._lock:
            now = datetime.now()
            for endpoint in self._metrics:
                while (self._metrics[endpoint]["timestamps"] and 
                       now - self._metrics[endpoint]["timestamps"][0] > max_age):
                    self._metrics[endpoint]["response_times"].popleft()
                    self._metrics[endpoint]["error_counts"].popleft()
                    self._metrics[endpoint]["request_counts"].popleft()
                    self._metrics[endpoint]["timestamps"].popleft()

# 创建全局性能记录器实例
_performance_logger = PerformanceLogger()

def get_performance_logger() -> PerformanceLogger:
    """获取性能记录器实例"""
    return _performance_logger

def get_performance_metrics(endpoint: str = None) -> Dict:
    """获取性能指标的便捷方法"""
    return _performance_logger.get_metrics(endpoint)
