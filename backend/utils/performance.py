import time
from fastapi import Request
from typing import Callable, Dict, List
import logging
from dataclasses import dataclass
from statistics import mean
from .performance_logger import performance_logger

logger = logging.getLogger(__name__)

@dataclass
class AlertThreshold:
    avg_response_time: float = 1.0  # seconds
    p95_response_time: float = 2.0  # seconds
    error_rate: float = 0.05  # 5%
    request_rate: float = 100  # requests per minute

class PerformanceAlert:
    def __init__(self, endpoint: str, metric: str, value: float, threshold: float):
        self.endpoint = endpoint
        self.metric = metric
        self.value = value
        self.threshold = threshold
        self.timestamp = time.time()

class PerformanceMonitor:
    def __init__(self):
        self.request_times: Dict[str, List[float]] = {}
        self.error_counts: Dict[str, int] = {}
        self.request_counts: Dict[str, List[float]] = {}
        self.alerts: List[PerformanceAlert] = []
        self.thresholds = AlertThreshold()
        self.alert_window = 300  # 5 minutes
        
    def _clean_old_data(self, current_time: float):
        """Remove data older than alert_window"""
        cutoff = current_time - self.alert_window
        for key in list(self.request_counts.keys()):
            self.request_counts[key] = [t for t in self.request_counts[key] if t > cutoff]
            
    def _check_alerts(self, path: str, duration: float, is_error: bool = False, status_code: int = None, request_id: str = None):
        """Check for performance alerts and log performance data"""
        current_time = time.time()
        self._clean_old_data(current_time)
        
        # Track request timing
        if path not in self.request_times:
            self.request_times[path] = []
        self.request_times[path].append(duration)
        self.request_times[path] = self.request_times[path][-100:]  # Keep last 100
        
        # Track request count
        if path not in self.request_counts:
            self.request_counts[path] = []
        self.request_counts[path].append(current_time)
        
        # Track errors
        if is_error:
            self.error_counts[path] = self.error_counts.get(path, 0) + 1
        
        # Calculate metrics
        times = self.request_times[path]
        if not times:
            return
            
        avg_time = mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        error_rate = self.error_counts.get(path, 0) / len(times)
        request_rate = len([t for t in self.request_counts[path] 
                          if t > current_time - 60]) # per minute
        
        # Log performance data
        metrics = {
            'average_response_time': avg_time,
            'p95_response_time': p95_time,
            'error_rate': error_rate,
            'request_rate': request_rate,
            'sample_count': len(times)
        }
        
        # Add performance log entry
        performance_logger.info(
            f"Performance metrics for {path}",
            extra={
                'path': path,
                'duration': duration,
                'status_code': status_code,
                'request_id': request_id,
                'metrics': metrics,
                'is_error': is_error
            }
        )
        
        # Check thresholds and generate alerts
        if avg_time > self.thresholds.avg_response_time:
            alert = PerformanceAlert(
                path, "average_response_time", 
                avg_time, self.thresholds.avg_response_time
            )
            self.alerts.append(alert)
            performance_logger.warning(
                f"High average response time on {path}",
                extra={
                    'path': path,
                    'alert_type': 'average_response_time',
                    'value': avg_time,
                    'threshold': self.thresholds.avg_response_time,
                    'request_id': request_id
                }
            )
            
        if p95_time > self.thresholds.p95_response_time:
            alert = PerformanceAlert(
                path, "p95_response_time",
                p95_time, self.thresholds.p95_response_time
            )
            self.alerts.append(alert)
            performance_logger.warning(
                f"High P95 response time on {path}",
                extra={
                    'path': path,
                    'alert_type': 'p95_response_time',
                    'value': p95_time,
                    'threshold': self.thresholds.p95_response_time,
                    'request_id': request_id
                }
            )
            
        if error_rate > self.thresholds.error_rate:
            alert = PerformanceAlert(
                path, "error_rate",
                error_rate, self.thresholds.error_rate
            )
            self.alerts.append(alert)
            performance_logger.warning(
                f"High error rate on {path}",
                extra={
                    'path': path,
                    'alert_type': 'error_rate',
                    'value': error_rate,
                    'threshold': self.thresholds.error_rate,
                    'request_id': request_id
                }
            )
            
        if request_rate > self.thresholds.request_rate:
            alert = PerformanceAlert(
                path, "request_rate",
                request_rate, self.thresholds.request_rate
            )
            self.alerts.append(alert)
            performance_logger.warning(
                f"High request rate on {path}",
                extra={
                    'path': path,
                    'alert_type': 'request_rate',
                    'value': request_rate,
                    'threshold': self.thresholds.request_rate,
                    'request_id': request_id
                }
            )
            
        # Clean old alerts
        self.alerts = [alert for alert in self.alerts 
                      if alert.timestamp > current_time - self.alert_window]

    async def __call__(self, request: Request, call_next: Callable):
        path = request.url.path
        method = request.method
        request_id = getattr(request.state, 'request_id', None)
        start_time = time.time()
        
        try:
            # Process the request
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Check for performance issues
            self._check_alerts(
                f"{method} {path}", 
                duration,
                is_error=response.status_code >= 400,
                status_code=response.status_code,
                request_id=request_id
            )
            
            # Add timing headers
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            self._check_alerts(
                f"{method} {path}", 
                duration, 
                is_error=True,
                status_code=500,
                request_id=request_id
            )
            raise

    def get_metrics(self):
        """Get performance metrics for all endpoints"""
        metrics = {}
        for key, times in self.request_times.items():
            if not times:
                continue
                
            avg_time = mean(times)
            times_sorted = sorted(times)
            p95_time = times_sorted[int(len(times) * 0.95)]
            max_time = max(times)
            
            metrics[key] = {
                "average": f"{avg_time:.3f}s",
                "p95": f"{p95_time:.3f}s",
                "max": f"{max_time:.3f}s",
                "samples": len(times),
                "error_rate": f"{(self.error_counts.get(key, 0) / len(times)) * 100:.1f}%"
            }
        return metrics

    def get_alerts(self):
        """Get current performance alerts"""
        current_time = time.time()
        live_alerts = [alert for alert in self.alerts 
                      if alert.timestamp > current_time - self.alert_window]
        
        return [{
            "endpoint": alert.endpoint,
            "metric": alert.metric,
            "value": f"{alert.value:.3f}",
            "threshold": f"{alert.threshold:.3f}",
            "timestamp": alert.timestamp
        } for alert in live_alerts]

# Create global instance
performance_monitor = PerformanceMonitor()