#!/usr/bin/env python3
"""
KSSEM College Virtual AI Assistant - Main Application
Main entry point for the kiosk-based AI assistant system
"""

import sys
import os
import logging
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent))

from core.system_manager import SystemManager
from core.gui.main_window import MainWindow
from core.utils.logger import setup_logging
from config.kssem_config import COLLEGE_INFO, PERFORMANCE_TARGETS

def main():
    """Main application entry point"""
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=" * 60)
        logger.info(f"Starting KSSEM College Virtual AI Assistant")
        logger.info(f"College: {COLLEGE_INFO['full_name']}")
        logger.info(f"Location: {COLLEGE_INFO['location']}")
        logger.info(f"Performance Target: {PERFORMANCE_TARGETS['response_time_ms']}ms response time")
        logger.info("=" * 60)
        
        # Initialize system manager
        system_manager = SystemManager()
        
        # Initialize and start GUI
        main_window = MainWindow(system_manager)
        
        # Start the main event loop
        main_window.run()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Shutting down KSSEM College Virtual AI Assistant")
        if 'system_manager' in locals():
            system_manager.shutdown()

if __name__ == "__main__":
    main()