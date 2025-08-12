"""
Logging Utility for KSSEM Virtual AI Assistant
Provides structured logging with privacy-aware features
"""

import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import json
import os
from pathlib import Path

def setup_logger(name: str, log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup structured logger for KSSEM Virtual AI Assistant
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

class KSSEMLogger:
    """
    Enhanced logger with KSSEM-specific features
    """
    
    def __init__(self, component_name: str):
        self.component_name = component_name
        self.logger = setup_logger(f"kssem.{component_name}")
        
    def log_query(self, query: str, intent: str, confidence: float, 
                  user_id: Optional[str] = None, session_id: Optional[str] = None):
        """Log user query with privacy protection"""
        log_data = {
            "event_type": "user_query",
            "component": self.component_name,
            "intent": intent,
            "confidence": confidence,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Don't log actual query text for privacy
        if user_id:
            log_data["user_hash"] = hash(user_id) % 10000  # Simple hash for correlation
        
        self.logger.info(json.dumps(log_data))
    
    def log_navigation(self, destination: str, route_distance: float, 
                      estimated_time: float, success: bool = True):
        """Log navigation requests"""
        log_data = {
            "event_type": "navigation_request",
            "component": self.component_name,
            "destination": destination,
            "route_distance": route_distance,
            "estimated_time": estimated_time,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(json.dumps(log_data))
    
    def log_system_performance(self, operation: str, duration: float, 
                              memory_usage: Optional[float] = None):
        """Log system performance metrics"""
        log_data = {
            "event_type": "performance_metric",
            "component": self.component_name,
            "operation": operation,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat()
        }
        
        if memory_usage:
            log_data["memory_usage_mb"] = memory_usage
        
        self.logger.info(json.dumps(log_data))
    
    def log_error(self, error_type: str, error_message: str, 
                  context: Optional[Dict[str, Any]] = None):
        """Log errors with context"""
        log_data = {
            "event_type": "error",
            "component": self.component_name,
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat()
        }
        
        if context:
            log_data["context"] = context
        
        self.logger.error(json.dumps(log_data))
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security-related events"""
        log_data = {
            "event_type": "security_event",
            "component": self.component_name,
            "security_event_type": event_type,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.warning(json.dumps(log_data))

# Example usage
if __name__ == "__main__":
    # Test basic logger
    logger = setup_logger("test_logger", "INFO")
    logger.info("Test log message")
    
    # Test enhanced logger
    kssem_logger = KSSEMLogger("nlp_engine")
    kssem_logger.log_query("Where is the library?", "navigation", 0.95)
    kssem_logger.log_navigation("library", 150.5, 120.0, True)
    kssem_logger.log_system_performance("intent_recognition", 0.45, 128.5)
    kssem_logger.log_error("model_error", "BERT model not loaded", {"model": "distilbert"})
    kssem_logger.log_security_event("unauthorized_access", {"ip": "192.168.1.100", "endpoint": "/admin"})
    
    print("✓ Logging tests completed")