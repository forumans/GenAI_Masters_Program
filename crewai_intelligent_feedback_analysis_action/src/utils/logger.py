"""
Comprehensive error handling and logging utilities
"""

import logging
import traceback
import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any, Exception
from functools import wraps
import json

class SystemLogger:
    """Enhanced logging system for the feedback analysis system"""
    
    def __init__(self, name: str = "feedback_system", log_dir: str = "logs"):
        """
        Initialize the system logger
        
        Args:
            name (str): Logger name
            log_dir (str): Directory for log files
        """
        self.name = name
        self.log_dir = log_dir
        self.logger = self._setup_logger()
        
        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger with file and console handlers"""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handler for detailed logging
        file_handler = logging.FileHandler(
            os.path.join(self.log_dir, f'{self.name}.log'),
            mode='a',
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # Error file handler
        error_handler = logging.FileHandler(
            os.path.join(self.log_dir, f'{self.name}_errors.log'),
            mode='a',
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.addHandler(error_handler)
        
        return logger
    
    def log_agent_action(self, agent_name: str, action: str, details: Dict[str, Any]):
        """Log agent-specific actions"""
        self.logger.info(f"[AGENT] {agent_name} - {action} - {json.dumps(details)}")
    
    def log_processing_step(self, step: str, status: str, details: Dict[str, Any] = None):
        """Log processing steps"""
        message = f"[STEP] {step} - {status}"
        if details:
            message += f" - {json.dumps(details)}"
        self.logger.info(message)
    
    def log_error(self, error: Exception, context: str = "", details: Dict[str, Any] = None):
        """Log errors with full context"""
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'traceback': traceback.format_exc(),
            'timestamp': datetime.now().isoformat()
        }
        
        if details:
            error_info['details'] = details
        
        self.logger.error(f"[ERROR] {json.dumps(error_info)}")
    
    def log_performance(self, operation: str, duration: float, details: Dict[str, Any] = None):
        """Log performance metrics"""
        perf_info = {
            'operation': operation,
            'duration_seconds': duration,
            'timestamp': datetime.now().isoformat()
        }
        
        if details:
            perf_info['details'] = details
        
        self.logger.info(f"[PERF] {json.dumps(perf_info)}")
    
    def log_quality_metrics(self, metrics: Dict[str, Any]):
        """Log quality metrics"""
        self.logger.info(f"[QUALITY] {json.dumps(metrics)}")
    
    def log_system_event(self, event: str, details: Dict[str, Any] = None):
        """Log system events"""
        event_info = {
            'event': event,
            'timestamp': datetime.now().isoformat()
        }
        
        if details:
            event_info['details'] = details
        
        self.logger.info(f"[SYSTEM] {json.dumps(event_info)}")

def handle_exceptions(logger: Optional[SystemLogger] = None, 
                     reraise: bool = True,
                     return_on_error: Any = None):
    """
    Decorator for handling exceptions consistently across the system
    
    Args:
        logger (Optional[SystemLogger]): Logger instance
        reraise (bool): Whether to reraise exceptions
        return_on_error (Any): Value to return on error if not reraising
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = f"Function: {func.__name__}, Module: {func.__module__}"
                details = {
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys()) if kwargs else []
                }
                
                if logger:
                    logger.log_error(e, context, details)
                else:
                    # Fallback logging
                    print(f"ERROR in {func.__name__}: {str(e)}")
                    print(f"Context: {context}")
                    print(traceback.format_exc())
                
                if reraise:
                    raise
                else:
                    return return_on_error
        
        return wrapper
    return decorator

class PerformanceMonitor:
    """Context manager for monitoring performance"""
    
    def __init__(self, operation: str, logger: Optional[SystemLogger] = None):
        """
        Initialize performance monitor
        
        Args:
            operation (str): Operation name
            logger (Optional[SystemLogger]): Logger instance
        """
        self.operation = operation
        self.logger = logger
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        details = {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat()
        }
        
        if self.logger:
            self.logger.log_performance(self.operation, duration, details)
        else:
            print(f"PERFORMANCE: {self.operation} took {duration:.2f} seconds")
    
    @property
    def duration(self) -> float:
        """Get operation duration"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

class SystemHealthChecker:
    """System health monitoring and validation"""
    
    def __init__(self, logger: Optional[SystemLogger] = None):
        """
        Initialize health checker
        
        Args:
            logger (Optional[SystemLogger]): Logger instance
        """
        self.logger = logger
        self.health_checks = []
    
    def add_check(self, name: str, check_func, critical: bool = False):
        """
        Add a health check
        
        Args:
            name (str): Check name
            check_func: Function that returns (bool, str) tuple
            critical (bool): Whether this is a critical check
        """
        self.health_checks.append({
            'name': name,
            'func': check_func,
            'critical': critical
        })
    
    def run_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {
            'overall_status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'checks': [],
            'critical_failures': 0,
            'total_failures': 0
        }
        
        for check in self.health_checks:
            try:
                is_healthy, message = check['func']()
                
                check_result = {
                    'name': check['name'],
                    'status': 'healthy' if is_healthy else 'unhealthy',
                    'message': message,
                    'critical': check['critical']
                }
                
                results['checks'].append(check_result)
                
                if not is_healthy:
                    results['total_failures'] += 1
                    if check['critical']:
                        results['critical_failures'] += 1
                        results['overall_status'] = 'unhealthy'
                
            except Exception as e:
                error_result = {
                    'name': check['name'],
                    'status': 'error',
                    'message': f"Check failed: {str(e)}",
                    'critical': check['critical']
                }
                
                results['checks'].append(error_result)
                results['total_failures'] += 1
                
                if check['critical']:
                    results['critical_failures'] += 1
                    results['overall_status'] = 'unhealthy'
        
        if results['total_failures'] > 0 and results['critical_failures'] == 0:
            results['overall_status'] = 'degraded'
        
        if self.logger:
            self.logger.log_system_event("health_check", results)
        
        return results

def create_default_health_checks() -> SystemHealthChecker:
    """Create default system health checks"""
    health_checker = SystemHealthChecker()
    
    # Check data directory
    def check_data_directory():
        data_dir = "data"
        if not os.path.exists(data_dir):
            return False, f"Data directory {data_dir} does not exist"
        
        required_files = [
            "app_store_reviews.csv",
            "support_emails.csv",
            "expected_classifications.csv"
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(os.path.join(data_dir, file)):
                missing_files.append(file)
        
        if missing_files:
            return False, f"Missing required files: {missing_files}"
        
        return True, "Data directory and required files are present"
    
    health_checker.add_check("data_directory", check_data_directory, critical=True)
    
    # Check output directory
    def check_output_directory():
        output_dir = "data"
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                return True, f"Created output directory {output_dir}"
            except Exception as e:
                return False, f"Cannot create output directory: {str(e)}"
        
        return True, f"Output directory {output_dir} is accessible"
    
    health_checker.add_check("output_directory", check_output_directory, critical=True)
    
    # Check log directory
    def check_log_directory():
        log_dir = "logs"
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
                return True, f"Created log directory {log_dir}"
            except Exception as e:
                return False, f"Cannot create log directory: {str(e)}"
        
        return True, f"Log directory {log_dir} is accessible"
    
    health_checker.add_check("log_directory", check_log_directory, critical=False)
    
    # Check environment variables
    def check_environment():
        required_vars = ['OPENAI_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            return False, f"Missing environment variables: {missing_vars}"
        
        return True, "All required environment variables are set"
    
    health_checker.add_check("environment", check_environment, critical=True)
    
    return health_checker

class ErrorRecovery:
    """Error recovery and retry mechanisms"""
    
    @staticmethod
    def retry_on_exception(max_retries: int = 3, delay: float = 1.0, 
                          exceptions: tuple = (Exception,), 
                          logger: Optional[SystemLogger] = None):
        """
        Decorator for retrying functions on specific exceptions
        
        Args:
            max_retries (int): Maximum number of retries
            delay (float): Delay between retries in seconds
            exceptions (tuple): Exception types to retry on
            logger (Optional[SystemLogger]): Logger instance
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt < max_retries:
                            if logger:
                                logger.log_error(
                                    e, 
                                    f"Retry attempt {attempt + 1}/{max_retries} for {func.__name__}"
                                )
                            else:
                                print(f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {str(e)}")
                            
                            import time
                            time.sleep(delay * (attempt + 1))  # Exponential backoff
                        else:
                            if logger:
                                logger.log_error(
                                    e, 
                                    f"All {max_retries} retries exhausted for {func.__name__}"
                                )
                            raise
                
                # This should never be reached, but just in case
                raise last_exception
            
            return wrapper
        return decorator
    
    @staticmethod
    def fallback_on_exception(fallback_value: Any = None, 
                            exceptions: tuple = (Exception,),
                            logger: Optional[SystemLogger] = None):
        """
        Decorator for providing fallback values on exceptions
        
        Args:
            fallback_value (Any): Value to return on exception
            exceptions (tuple): Exception types to catch
            logger (Optional[SystemLogger]): Logger instance
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if logger:
                        logger.log_error(e, f"Using fallback for {func.__name__}")
                    else:
                        print(f"Using fallback for {func.__name__}: {str(e)}")
                    return fallback_value
            
            return wrapper
        return decorator

# Global logger instance
_global_logger = None

def get_logger() -> SystemLogger:
    """Get or create the global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = SystemLogger()
    return _global_logger
