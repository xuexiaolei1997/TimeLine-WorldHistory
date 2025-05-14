import logging
import os
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler

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