"""
Logging utility for KSSEM College Virtual AI Assistant
Configures logging with proper formatting and file output
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from datetime import datetime

def setup_logging(
    log_level: str = "INFO",
    log_file: str = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
):
    """Setup logging configuration for the application"""
    
    # Create logs directory if it doesn't exist
    if log_file is None:
        logs_dir = Path(__file__).parent.parent.parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        log_file = logs_dir / f"kssem_assistant_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("KSSEM College Virtual AI Assistant - Logging System Started")
    logger.info(f"Log Level: {log_level.upper()}")
    logger.info(f"Log File: {log_file}")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(name)

def log_performance_metric(logger: logging.Logger, metric_name: str, value: float, unit: str = ""):
    """Log a performance metric with consistent formatting"""
    logger.info(f"PERFORMANCE: {metric_name} = {value:.2f} {unit}")

def log_security_event(logger: logging.Logger, event_type: str, description: str, severity: str = "INFO"):
    """Log a security-related event"""
    logger.warning(f"SECURITY: {event_type} - {description} (Severity: {severity})")

def log_user_interaction(logger: logging.Logger, user_action: str, details: str = ""):
    """Log user interactions for analytics and debugging"""
    logger.info(f"USER_ACTION: {user_action} - {details}")

def log_system_health(logger: logging.Logger, component: str, status: str, details: str = ""):
    """Log system health status"""
    if status.lower() == "healthy":
        logger.info(f"HEALTH: {component} - {status} - {details}")
    elif status.lower() == "warning":
        logger.warning(f"HEALTH: {component} - {status} - {details}")
    else:
        logger.error(f"HEALTH: {component} - {status} - {details}")

def log_error_with_context(logger: logging.Logger, error: Exception, context: str = "", user_id: str = None):
    """Log an error with additional context information"""
    error_msg = f"ERROR: {context} - {type(error).__name__}: {str(error)}"
    if user_id:
        error_msg += f" (User: {user_id})"
    logger.error(error_msg, exc_info=True)

def log_api_call(logger: logging.Logger, endpoint: str, method: str, status_code: int, response_time: float):
    """Log API call information"""
    status_emoji = "✅" if status_code < 400 else "❌"
    logger.info(f"API_CALL: {status_emoji} {method} {endpoint} - {status_code} ({response_time:.2f}ms)")

def log_navigation_request(logger: logging.Logger, start_location: str, end_location: str, route_found: bool):
    """Log navigation requests"""
    status = "✅ Route Found" if route_found else "❌ Route Not Found"
    logger.info(f"NAVIGATION: {start_location} → {end_location} - {status}")

def log_query_processing(logger: logging.Logger, query: str, query_type: str, response_time: float, success: bool):
    """Log query processing information"""
    status_emoji = "✅" if success else "❌"
    logger.info(f"QUERY: {status_emoji} {query_type} - '{query[:50]}{'...' if len(query) > 50 else ''}' - {response_time:.2f}ms")

def log_accessibility_feature(logger: logging.Logger, feature: str, user_action: str):
    """Log accessibility feature usage"""
    logger.info(f"ACCESSIBILITY: {feature} - {user_action}")

def log_privacy_event(logger: logging.Logger, event_type: str, data_type: str, anonymized: bool):
    """Log privacy-related events"""
    status = "✅ Anonymized" if anonymized else "❌ Not Anonymized"
    logger.info(f"PRIVACY: {event_type} - {data_type} - {status}")

def log_slam_event(logger: logging.Logger, event_type: str, location: str, accuracy: float):
    """Log SLAM-related events"""
    logger.info(f"SLAM: {event_type} - {location} - Accuracy: {accuracy:.2f}%")

def log_nlp_event(logger: logging.Logger, event_type: str, input_text: str, confidence: float):
    """Log NLP-related events"""
    logger.info(f"NLP: {event_type} - '{input_text[:50]}{'...' if len(input_text) > 50 else ''}' - Confidence: {confidence:.2f}%")

def log_speech_event(logger: logging.Logger, event_type: str, language: str, success: bool):
    """Log speech processing events"""
    status_emoji = "✅" if success else "❌"
    logger.info(f"SPEECH: {status_emoji} {event_type} - Language: {language}")

def log_resource_access(logger: logging.Logger, resource_type: str, resource_id: str, access_granted: bool):
    """Log resource access attempts"""
    status_emoji = "✅" if access_granted else "❌"
    logger.info(f"RESOURCE: {status_emoji} {resource_type} - {resource_id}")

def log_campus_event(logger: logging.Logger, event_type: str, location: str, description: str):
    """Log campus-related events"""
    logger.info(f"CAMPUS: {event_type} - {location} - {description}")

def log_system_startup(logger: logging.Logger, components: list):
    """Log system startup information"""
    logger.info("=" * 60)
    logger.info("SYSTEM STARTUP INITIATED")
    logger.info(f"Components to initialize: {', '.join(components)}")
    logger.info("=" * 60)

def log_system_shutdown(logger: logging.Logger, reason: str = "Normal shutdown"):
    """Log system shutdown information"""
    logger.info("=" * 60)
    logger.info("SYSTEM SHUTDOWN INITIATED")
    logger.info(f"Reason: {reason}")
    logger.info("=" * 60)

def log_configuration_change(logger: logging.Logger, config_key: str, old_value: str, new_value: str):
    """Log configuration changes"""
    logger.info(f"CONFIG: {config_key} changed from '{old_value}' to '{new_value}'")

def log_performance_alert(logger: logging.Logger, metric: str, threshold: float, current_value: float):
    """Log performance alerts when thresholds are exceeded"""
    logger.warning(f"PERFORMANCE_ALERT: {metric} threshold {threshold} exceeded (current: {current_value})")

def log_security_alert(logger: logging.Logger, alert_type: str, severity: str, description: str):
    """Log security alerts"""
    logger.error(f"SECURITY_ALERT: {alert_type} - {severity} - {description}")

def log_user_session(logger: logging.Logger, session_id: str, action: str, user_type: str = "anonymous"):
    """Log user session events"""
    logger.info(f"SESSION: {session_id} - {user_type} - {action}")

def log_data_access(logger: logging.Logger, data_type: str, access_method: str, user_id: str = None):
    """Log data access events"""
    user_info = f" (User: {user_id})" if user_id else ""
    logger.info(f"DATA_ACCESS: {data_type} via {access_method}{user_info}")

def log_error_recovery(logger: logging.Logger, component: str, error_type: str, recovery_action: str):
    """Log error recovery attempts"""
    logger.info(f"RECOVERY: {component} recovered from {error_type} via {recovery_action}")

def log_maintenance_event(logger: logging.Logger, component: str, action: str, duration: float = None):
    """Log maintenance events"""
    duration_info = f" (Duration: {duration:.2f}s)" if duration else ""
    logger.info(f"MAINTENANCE: {component} - {action}{duration_info}")

def log_backup_event(logger: logging.Logger, backup_type: str, success: bool, size_mb: float = None):
    """Log backup events"""
    status_emoji = "✅" if success else "❌"
    size_info = f" (Size: {size_mb:.2f}MB)" if size_mb else ""
    logger.info(f"BACKUP: {status_emoji} {backup_type}{size_info}")

def log_sync_event(logger: logging.Logger, sync_type: str, source: str, target: str, success: bool):
    """Log synchronization events"""
    status_emoji = "✅" if success else "❌"
    logger.info(f"SYNC: {status_emoji} {sync_type} - {source} → {target}")

def log_cache_event(logger: logging.Logger, cache_type: str, action: str, key: str = None):
    """Log cache-related events"""
    key_info = f" - Key: {key}" if key else ""
    logger.info(f"CACHE: {cache_type} - {action}{key_info}")

def log_network_event(logger: logging.Logger, event_type: str, endpoint: str, status: str):
    """Log network-related events"""
    logger.info(f"NETWORK: {event_type} - {endpoint} - {status}")

def log_database_event(logger: logging.Logger, operation: str, table: str, success: bool, duration: float = None):
    """Log database operations"""
    status_emoji = "✅" if success else "❌"
    duration_info = f" ({duration:.2f}ms)" if duration else ""
    logger.info(f"DATABASE: {status_emoji} {operation} on {table}{duration_info}")

def log_file_operation(logger: logging.Logger, operation: str, file_path: str, success: bool, size_bytes: int = None):
    """Log file operations"""
    status_emoji = "✅" if success else "❌"
    size_info = f" ({size_bytes} bytes)" if size_bytes else ""
    logger.info(f"FILE: {status_emoji} {operation} - {file_path}{size_info}")

def log_authentication_event(logger: logging.Logger, user_id: str, method: str, success: bool, ip_address: str = None):
    """Log authentication events"""
    status_emoji = "✅" if success else "❌"
    ip_info = f" (IP: {ip_address})" if ip_address else ""
    logger.info(f"AUTH: {status_emoji} {user_id} via {method}{ip_info}")

def log_authorization_event(logger: logging.Logger, user_id: str, resource: str, permission: str, granted: bool):
    """Log authorization events"""
    status_emoji = "✅" if granted else "❌"
    logger.info(f"AUTHORIZATION: {status_emoji} {user_id} - {permission} on {resource}")

def log_audit_event(logger: logging.Logger, user_id: str, action: str, resource: str, details: str = ""):
    """Log audit events for compliance"""
    details_info = f" - {details}" if details else ""
    logger.info(f"AUDIT: {user_id} - {action} on {resource}{details_info}")

def log_compliance_event(logger: logging.Logger, compliance_type: str, status: str, details: str = ""):
    """Log compliance-related events"""
    status_emoji = "✅" if status.lower() == "compliant" else "❌"
    details_info = f" - {details}" if details else ""
    logger.info(f"COMPLIANCE: {status_emoji} {compliance_type} - {status}{details_info}")

def log_environment_info(logger: logging.Logger):
    """Log environment information for debugging"""
    import platform
    import sys
    
    logger.info("=" * 60)
    logger.info("ENVIRONMENT INFORMATION")
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Architecture: {platform.architecture()}")
    logger.info(f"Machine: {platform.machine()}")
    logger.info(f"Processor: {platform.processor()}")
    logger.info(f"Working Directory: {os.getcwd()}")
    logger.info("=" * 60)