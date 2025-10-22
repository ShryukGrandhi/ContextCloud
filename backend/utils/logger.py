"""
Logging utilities for ContextCloud Agents
"""

import logging
import sys
from datetime import datetime
from typing import Optional

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Setup logger with consistent formatting"""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Prevent duplicate logs
    logger.propagate = False
    
    return logger

class AgentLogger:
    """Specialized logger for agent activities"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = setup_logger(f"Agent.{agent_name}")
    
    def log_action(self, action: str, details: Optional[str] = None):
        """Log agent action with emoji and formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if details:
            self.logger.info(f"[{self.agent_name}] → {action} ✅ ({details})")
        else:
            self.logger.info(f"[{self.agent_name}] → {action} ✅")
    
    def log_error(self, error: str, details: Optional[str] = None):
        """Log agent error"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if details:
            self.logger.error(f"[{self.agent_name}] → ❌ {error} ({details})")
        else:
            self.logger.error(f"[{self.agent_name}] → ❌ {error}")
    
    def log_tool_call(self, tool_name: str, params: dict):
        """Log tool calling activity"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logger.info(f"[{self.agent_name}] → 🔧 Calling {tool_name} with params: {params}")
    
    def log_result(self, result_summary: str):
        """Log agent result"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logger.info(f"[{self.agent_name}] → 📊 Result: {result_summary}")

# Global logger instance
main_logger = setup_logger("ContextCloud")
