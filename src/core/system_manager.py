"""
System Manager for KSSEM College Virtual AI Assistant
Coordinates all system components and manages the overall system state
"""

import logging
import threading
import time
from typing import Dict, Any, Optional
from pathlib import Path

from .ai.nlp_engine import NLPEngine
from .ai.slam_engine import SLAMEngine
from .ai.speech_engine import SpeechEngine
from .modules.query_processor import QueryProcessor
from .modules.navigation_module import NavigationModule
from .modules.resource_access import ResourceAccessModule
from .modules.privacy_module import PrivacyModule
from .utils.performance_monitor import PerformanceMonitor
from .utils.security_manager import SecurityManager
from config.kssem_config import (
    COLLEGE_INFO, PERFORMANCE_TARGETS, SECURITY_CONFIG, 
    SLAM_CONFIG, NLP_TRAINING_DATA
)

class SystemManager:
    """Main system coordinator for the Virtual AI Assistant"""
    
    def __init__(self):
        """Initialize the system manager and all components"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing KSSEM College Virtual AI Assistant System")
        
        # System state
        self.is_running = False
        self.start_time = None
        self.system_status = "initializing"
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor(PERFORMANCE_TARGETS)
        
        # Security management
        self.security_manager = SecurityManager(SECURITY_CONFIG)
        
        # Initialize AI engines
        self._init_ai_engines()
        
        # Initialize core modules
        self._init_core_modules()
        
        # System health monitoring thread
        self.health_monitor_thread = None
        
        self.logger.info("System Manager initialization completed")
    
    def _init_ai_engines(self):
        """Initialize AI processing engines"""
        try:
            self.logger.info("Initializing AI Engines...")
            
            # NLP Engine for query understanding
            self.nlp_engine = NLPEngine(
                model_path=NLP_TRAINING_DATA.get("faq_database"),
                target_accuracy=PERFORMANCE_TARGETS["nlp_accuracy"]
            )
            
            # SLAM Engine for campus navigation
            self.slam_engine = SLAMEngine(
                algorithm=SLAM_CONFIG["algorithm"],
                sensor_type=SLAM_CONFIG["sensor_type"],
                target_precision=PERFORMANCE_TARGETS["navigation_precision"]
            )
            
            # Speech Engine for voice interactions
            self.speech_engine = SpeechEngine(
                target_languages=["English", "Kannada", "Hindi", "Telugu"]
            )
            
            self.logger.info("AI Engines initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI engines: {e}")
            raise
    
    def _init_core_modules(self):
        """Initialize core system modules"""
        try:
            self.logger.info("Initializing Core Modules...")
            
            # Query Processing Module
            self.query_processor = QueryProcessor(
                nlp_engine=self.nlp_engine,
                speech_engine=self.speech_engine
            )
            
            # Navigation Module
            self.navigation_module = NavigationModule(
                slam_engine=self.slam_engine,
                campus_config=self._get_campus_config()
            )
            
            # Resource Access Module
            self.resource_access = ResourceAccessModule(
                security_manager=self.security_manager
            )
            
            # Privacy Module
            self.privacy_module = PrivacyModule(
                security_manager=self.security_manager
            )
            
            self.logger.info("Core Modules initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize core modules: {e}")
            raise
    
    def _get_campus_config(self) -> Dict[str, Any]:
        """Get campus configuration for navigation"""
        from config.kssem_config import CAMPUS_BUILDINGS, CAMPUS_MAP_CONFIG
        
        return {
            "buildings": CAMPUS_BUILDINGS,
            "map_config": CAMPUS_MAP_CONFIG,
            "college_info": COLLEGE_INFO
        }
    
    def start(self):
        """Start the system and all components"""
        if self.is_running:
            self.logger.warning("System is already running")
            return
        
        try:
            self.logger.info("Starting KSSEM College Virtual AI Assistant System...")
            
            # Start AI engines
            self.nlp_engine.start()
            self.slam_engine.start()
            self.speech_engine.start()
            
            # Start core modules
            self.query_processor.start()
            self.navigation_module.start()
            self.resource_access.start()
            self.privacy_module.start()
            
            # Start performance monitoring
            self.performance_monitor.start()
            
            # Start health monitoring
            self._start_health_monitoring()
            
            self.is_running = True
            self.start_time = time.time()
            self.system_status = "running"
            
            self.logger.info("System started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start system: {e}")
            self.system_status = "error"
            raise
    
    def stop(self):
        """Stop the system and all components"""
        if not self.is_running:
            self.logger.warning("System is not running")
            return
        
        try:
            self.logger.info("Stopping KSSEM College Virtual AI Assistant System...")
            
            # Stop health monitoring
            self._stop_health_monitoring()
            
            # Stop performance monitoring
            self.performance_monitor.stop()
            
            # Stop core modules
            self.resource_access.stop()
            self.navigation_module.stop()
            self.query_processor.stop()
            
            # Stop AI engines
            self.speech_engine.stop()
            self.slam_engine.stop()
            self.nlp_engine.stop()
            
            self.is_running = False
            self.system_status = "stopped"
            
            self.logger.info("System stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to stop system: {e}")
            raise
    
    def shutdown(self):
        """Graceful shutdown of the system"""
        self.logger.info("Initiating system shutdown...")
        self.stop()
        
        # Cleanup resources
        self.performance_monitor.cleanup()
        self.security_manager.cleanup()
        
        self.logger.info("System shutdown completed")
    
    def _start_health_monitoring(self):
        """Start system health monitoring in background thread"""
        self.health_monitor_thread = threading.Thread(
            target=self._health_monitor_loop,
            daemon=True
        )
        self.health_monitor_thread.start()
    
    def _stop_health_monitoring(self):
        """Stop health monitoring thread"""
        if self.health_monitor_thread and self.health_monitor_thread.is_alive():
            self.health_monitor_thread.join(timeout=5)
    
    def _health_monitor_loop(self):
        """Health monitoring loop"""
        while self.is_running:
            try:
                # Check system health
                health_status = self._check_system_health()
                
                if health_status != "healthy":
                    self.logger.warning(f"System health issue detected: {health_status}")
                    self.system_status = health_status
                
                # Wait before next check
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _check_system_health(self) -> str:
        """Check overall system health"""
        try:
            # Check AI engines
            if not self.nlp_engine.is_healthy():
                return "nlp_engine_unhealthy"
            
            if not self.slam_engine.is_healthy():
                return "slam_engine_unhealthy"
            
            if not self.speech_engine.is_healthy():
                return "speech_engine_unhealthy"
            
            # Check performance metrics
            if not self.performance_monitor.is_meeting_targets():
                return "performance_degraded"
            
            # Check security status
            if not self.security_manager.is_secure():
                return "security_compromised"
            
            return "healthy"
            
        except Exception as e:
            self.logger.error(f"Health check error: {e}")
            return "health_check_failed"
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and metrics"""
        uptime = time.time() - self.start_time if self.start_time else 0
        
        return {
            "status": self.system_status,
            "is_running": self.is_running,
            "uptime_seconds": uptime,
            "uptime_formatted": self._format_uptime(uptime),
            "performance_metrics": self.performance_monitor.get_metrics(),
            "ai_engine_status": {
                "nlp": self.nlp_engine.get_status(),
                "slam": self.slam_engine.get_status(),
                "speech": self.speech_engine.get_status()
            },
            "module_status": {
                "query_processor": self.query_processor.get_status(),
                "navigation": self.navigation_module.get_status(),
                "resource_access": self.resource_access.get_status(),
                "privacy": self.privacy_module.get_status()
            },
            "college_info": COLLEGE_INFO
        }
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def process_query(self, query: str, query_type: str = "text") -> Dict[str, Any]:
        """Process user query through the system"""
        try:
            self.logger.info(f"Processing {query_type} query: {query}")
            
            # Start performance measurement
            start_time = time.time()
            
            # Process query based on type
            if query_type == "voice":
                # Convert speech to text first
                text_query = self.speech_engine.speech_to_text(query)
                query = text_query
            
            # Process through query processor
            response = self.query_processor.process(query)
            
            # Measure response time
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Update performance metrics
            self.performance_monitor.record_response_time(response_time)
            
            # Log query for privacy compliance
            self.privacy_module.log_query(query, response, response_time)
            
            return {
                "success": True,
                "response": response,
                "response_time_ms": response_time,
                "query_type": query_type,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Query processing error: {e}")
            return {
                "success": False,
                "error": str(e),
                "query_type": query_type,
                "timestamp": time.time()
            }
    
    def get_navigation_route(self, start_location: str, end_location: str) -> Dict[str, Any]:
        """Get navigation route between two campus locations"""
        try:
            return self.navigation_module.get_route(start_location, end_location)
        except Exception as e:
            self.logger.error(f"Navigation error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_campus_resource(self, resource_type: str, query: str) -> Dict[str, Any]:
        """Get campus resource information"""
        try:
            return self.resource_access.get_resource(resource_type, query)
        except Exception as e:
            self.logger.error(f"Resource access error: {e}")
            return {"success": False, "error": str(e)}