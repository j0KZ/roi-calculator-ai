#!/usr/bin/env python3
"""
Debug Utilities - Common error handling functions for Chilean E-commerce Sales Toolkit
Provides comprehensive debugging, validation, and error recovery mechanisms
"""

import logging
import traceback
import sys
import os
import json
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from functools import wraps
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sales_toolkit_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class ValidationResult:
    """Result of validation operations"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    sanitized_value: Any = None

@dataclass
class ErrorContext:
    """Context information for errors"""
    function_name: str
    parameters: Dict[str, Any]
    timestamp: datetime
    severity: ErrorSeverity
    error_message: str
    stack_trace: str

class DebugLogger:
    """Enhanced logging utility"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.errors = []
        self.warnings = []
        
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(f"{message} {kwargs if kwargs else ''}")
        
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(f"{message} {kwargs if kwargs else ''}")
        
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        warning_msg = f"{message} {kwargs if kwargs else ''}"
        self.logger.warning(warning_msg)
        self.warnings.append({
            'timestamp': datetime.now(),
            'message': warning_msg,
            'context': kwargs
        })
        
    def error(self, message: str, error: Exception = None, **kwargs):
        """Log error message"""
        error_msg = f"{message} {kwargs if kwargs else ''}"
        if error:
            error_msg += f" - {str(error)}"
        
        self.logger.error(error_msg)
        self.errors.append({
            'timestamp': datetime.now(),
            'message': error_msg,
            'exception': str(error) if error else None,
            'context': kwargs
        })
        
    def critical(self, message: str, error: Exception = None, **kwargs):
        """Log critical error message"""
        error_msg = f"CRITICAL: {message} {kwargs if kwargs else ''}"
        if error:
            error_msg += f" - {str(error)}"
        
        self.logger.critical(error_msg)
        self.errors.append({
            'timestamp': datetime.now(),
            'message': error_msg,
            'exception': str(error) if error else None,
            'severity': 'CRITICAL',
            'context': kwargs
        })
        
    def get_error_summary(self) -> Dict:
        """Get summary of logged errors and warnings"""
        return {
            'total_errors': len(self.errors),
            'total_warnings': len(self.warnings),
            'errors': self.errors,
            'warnings': self.warnings
        }

def error_handler(severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 fallback_value: Any = None,
                 raise_on_critical: bool = True):
    """Decorator for comprehensive error handling"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = DebugLogger(func.__name__)
            
            try:
                logger.debug(f"Entering {func.__name__}", 
                           args=len(args), kwargs=list(kwargs.keys()))
                
                result = func(*args, **kwargs)
                
                logger.debug(f"Successfully completed {func.__name__}")
                return result
                
            except Exception as e:
                error_context = ErrorContext(
                    function_name=func.__name__,
                    parameters={'args': args, 'kwargs': kwargs},
                    timestamp=datetime.now(),
                    severity=severity,
                    error_message=str(e),
                    stack_trace=traceback.format_exc()
                )
                
                if severity == ErrorSeverity.CRITICAL and raise_on_critical:
                    logger.critical(f"Critical error in {func.__name__}", error=e)
                    raise
                elif severity in [ErrorSeverity.HIGH, ErrorSeverity.MEDIUM]:
                    logger.error(f"Error in {func.__name__}", error=e)
                else:
                    logger.warning(f"Minor error in {func.__name__}", error=e)
                
                # Return fallback value or handle gracefully
                if fallback_value is not None:
                    logger.info(f"Returning fallback value for {func.__name__}")
                    return fallback_value
                    
                # For non-critical errors, try to return a safe default
                return get_safe_default(func, args, kwargs)
                
        return wrapper
    return decorator

def get_safe_default(func: Callable, args: tuple, kwargs: dict) -> Any:
    """Get safe default return value based on function signature"""
    func_name = func.__name__
    
    # Common safe defaults based on function patterns
    if 'calculate' in func_name.lower() or 'compute' in func_name.lower():
        return {'error': True, 'message': f'Calculation failed in {func_name}', 'result': 0}
    elif 'validate' in func_name.lower():
        return ValidationResult(False, [f'Validation failed in {func_name}'], [], None)
    elif 'generate' in func_name.lower():
        return {'error': True, 'message': f'Generation failed in {func_name}', 'data': {}}
    elif 'export' in func_name.lower() or 'save' in func_name.lower():
        return False
    else:
        return None

class InputValidator:
    """Comprehensive input validation utility"""
    
    def __init__(self):
        self.logger = DebugLogger("InputValidator")
    
    def validate_numeric(self, value: Any, field_name: str, 
                        min_value: float = None, max_value: float = None,
                        allow_zero: bool = True, allow_negative: bool = False) -> ValidationResult:
        """Validate numeric input with comprehensive checks"""
        errors = []
        warnings = []
        
        try:
            # Handle None or empty values
            if value is None or value == '':
                errors.append(f"{field_name} cannot be empty")
                return ValidationResult(False, errors, warnings, 0)
            
            # Convert to float
            try:
                numeric_value = float(value)
            except (ValueError, TypeError):
                errors.append(f"{field_name} must be a valid number, got: {type(value).__name__}")
                return ValidationResult(False, errors, warnings, 0)
            
            # Check for NaN or infinity
            if np.isnan(numeric_value):
                errors.append(f"{field_name} cannot be NaN")
                return ValidationResult(False, errors, warnings, 0)
            
            if np.isinf(numeric_value):
                errors.append(f"{field_name} cannot be infinite")
                return ValidationResult(False, errors, warnings, 0)
            
            # Check zero
            if not allow_zero and numeric_value == 0:
                errors.append(f"{field_name} cannot be zero")
                return ValidationResult(False, errors, warnings, 1)
            
            # Check negative
            if not allow_negative and numeric_value < 0:
                errors.append(f"{field_name} cannot be negative, got: {numeric_value}")
                return ValidationResult(False, errors, warnings, abs(numeric_value))
            
            # Check range
            if min_value is not None and numeric_value < min_value:
                errors.append(f"{field_name} must be at least {min_value}, got: {numeric_value}")
                return ValidationResult(False, errors, warnings, min_value)
            
            if max_value is not None and numeric_value > max_value:
                warnings.append(f"{field_name} exceeds maximum expected value of {max_value}")
                # Don't fail validation, just warn
            
            # Check for extremely large values that might cause issues
            if abs(numeric_value) > 1e15:
                warnings.append(f"{field_name} is extremely large: {numeric_value}")
            
            return ValidationResult(True, errors, warnings, numeric_value)
            
        except Exception as e:
            self.logger.error(f"Unexpected error validating {field_name}", error=e)
            errors.append(f"Validation error for {field_name}: {str(e)}")
            return ValidationResult(False, errors, warnings, 0)
    
    def validate_currency_clp(self, value: Any, field_name: str) -> ValidationResult:
        """Validate Chilean Peso currency values"""
        result = self.validate_numeric(
            value, field_name, 
            min_value=0, max_value=1e12,  # Max 1 trillion CLP
            allow_zero=True, allow_negative=False
        )
        
        if result.is_valid and result.sanitized_value is not None:
            # Round to nearest peso (no decimals)
            result.sanitized_value = round(result.sanitized_value)
            
            # Add warning for unusually small/large amounts
            if result.sanitized_value < 1000:
                result.warnings.append(f"{field_name} is very small: {result.sanitized_value} CLP")
            elif result.sanitized_value > 1e9:  # 1 billion CLP
                result.warnings.append(f"{field_name} is very large: {result.sanitized_value:,.0f} CLP")
        
        return result
    
    def validate_percentage(self, value: Any, field_name: str, 
                          max_percent: float = 100) -> ValidationResult:
        """Validate percentage values"""
        result = self.validate_numeric(
            value, field_name,
            min_value=0, max_value=max_percent,
            allow_zero=True, allow_negative=False
        )
        
        if result.is_valid and result.sanitized_value is not None:
            # Convert to decimal if it looks like a percentage (>1)
            if result.sanitized_value > 1 and result.sanitized_value <= 100:
                result.warnings.append(f"Converting {field_name} from percentage to decimal")
                result.sanitized_value = result.sanitized_value / 100
        
        return result
    
    def validate_string(self, value: Any, field_name: str, 
                       required: bool = True, max_length: int = None) -> ValidationResult:
        """Validate string input"""
        errors = []
        warnings = []
        
        try:
            if value is None or value == '':
                if required:
                    errors.append(f"{field_name} is required")
                    return ValidationResult(False, errors, warnings, "")
                else:
                    return ValidationResult(True, errors, warnings, "")
            
            # Convert to string
            str_value = str(value).strip()
            
            # Check length
            if max_length and len(str_value) > max_length:
                warnings.append(f"{field_name} exceeds maximum length of {max_length}")
                str_value = str_value[:max_length]
            
            # Check for potentially dangerous content
            dangerous_patterns = ['<script', 'javascript:', 'data:', 'vbscript:']
            if any(pattern in str_value.lower() for pattern in dangerous_patterns):
                errors.append(f"{field_name} contains potentially dangerous content")
                return ValidationResult(False, errors, warnings, "")
            
            return ValidationResult(True, errors, warnings, str_value)
            
        except Exception as e:
            self.logger.error(f"Error validating string {field_name}", error=e)
            errors.append(f"String validation error for {field_name}: {str(e)}")
            return ValidationResult(False, errors, warnings, "")
    
    def validate_list(self, value: Any, field_name: str, 
                     required: bool = True, min_items: int = 0, 
                     max_items: int = None) -> ValidationResult:
        """Validate list input"""
        errors = []
        warnings = []
        
        try:
            if value is None or value == '':
                if required:
                    errors.append(f"{field_name} is required")
                    return ValidationResult(False, errors, warnings, [])
                else:
                    return ValidationResult(True, errors, warnings, [])
            
            # Ensure it's a list
            if not isinstance(value, list):
                if isinstance(value, str):
                    # Try to split comma-separated string
                    list_value = [item.strip() for item in value.split(',') if item.strip()]
                else:
                    list_value = [value]
            else:
                list_value = value
            
            # Check length
            if len(list_value) < min_items:
                errors.append(f"{field_name} must have at least {min_items} items")
                return ValidationResult(False, errors, warnings, [])
            
            if max_items and len(list_value) > max_items:
                warnings.append(f"{field_name} has too many items, truncating to {max_items}")
                list_value = list_value[:max_items]
            
            return ValidationResult(True, errors, warnings, list_value)
            
        except Exception as e:
            self.logger.error(f"Error validating list {field_name}", error=e)
            errors.append(f"List validation error for {field_name}: {str(e)}")
            return ValidationResult(False, errors, warnings, [])
    
    def validate_dict(self, value: Any, field_name: str, 
                     required_keys: List[str] = None) -> ValidationResult:
        """Validate dictionary input"""
        errors = []
        warnings = []
        
        try:
            if value is None:
                errors.append(f"{field_name} cannot be None")
                return ValidationResult(False, errors, warnings, {})
            
            if not isinstance(value, dict):
                try:
                    # Try to parse as JSON if it's a string
                    if isinstance(value, str):
                        dict_value = json.loads(value)
                    else:
                        errors.append(f"{field_name} must be a dictionary")
                        return ValidationResult(False, errors, warnings, {})
                except json.JSONDecodeError:
                    errors.append(f"{field_name} is not a valid dictionary or JSON")
                    return ValidationResult(False, errors, warnings, {})
            else:
                dict_value = value
            
            # Check required keys
            if required_keys:
                missing_keys = [key for key in required_keys if key not in dict_value]
                if missing_keys:
                    errors.append(f"{field_name} missing required keys: {missing_keys}")
                    # Add missing keys with default values
                    for key in missing_keys:
                        dict_value[key] = None
            
            return ValidationResult(True, errors, warnings, dict_value)
            
        except Exception as e:
            self.logger.error(f"Error validating dict {field_name}", error=e)
            errors.append(f"Dictionary validation error for {field_name}: {str(e)}")
            return ValidationResult(False, errors, warnings, {})

class FileHandler:
    """Safe file I/O operations with error handling"""
    
    def __init__(self):
        self.logger = DebugLogger("FileHandler")
    
    @error_handler(ErrorSeverity.HIGH, fallback_value=False)
    def safe_file_write(self, filepath: str, content: str, 
                       encoding: str = 'utf-8', backup: bool = True) -> bool:
        """Safely write content to file with backup"""
        try:
            # Validate filepath
            if not filepath or not isinstance(filepath, str):
                raise ValueError(f"Invalid filepath: {filepath}")
            
            # Ensure directory exists
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                self.logger.info(f"Created directory: {directory}")
            
            # Create backup if file exists
            if backup and os.path.exists(filepath):
                backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                try:
                    import shutil
                    shutil.copy2(filepath, backup_path)
                    self.logger.info(f"Created backup: {backup_path}")
                except Exception as e:
                    self.logger.warning(f"Could not create backup: {e}")
            
            # Write file
            with open(filepath, 'w', encoding=encoding) as f:
                f.write(content)
            
            self.logger.info(f"Successfully wrote file: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to write file {filepath}", error=e)
            raise
    
    @error_handler(ErrorSeverity.MEDIUM, fallback_value={})
    def safe_json_save(self, filepath: str, data: Dict, 
                      encoding: str = 'utf-8', backup: bool = True) -> bool:
        """Safely save dictionary as JSON"""
        try:
            json_content = json.dumps(data, ensure_ascii=False, indent=2, default=str)
            return self.safe_file_write(filepath, json_content, encoding, backup)
        except Exception as e:
            self.logger.error(f"Failed to save JSON {filepath}", error=e)
            return False
    
    @error_handler(ErrorSeverity.MEDIUM, fallback_value=None)
    def safe_file_read(self, filepath: str, encoding: str = 'utf-8') -> Optional[str]:
        """Safely read file content"""
        try:
            if not os.path.exists(filepath):
                self.logger.warning(f"File does not exist: {filepath}")
                return None
            
            if not os.path.isfile(filepath):
                self.logger.error(f"Path is not a file: {filepath}")
                return None
            
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()
            
            self.logger.debug(f"Successfully read file: {filepath}")
            return content
            
        except Exception as e:
            self.logger.error(f"Failed to read file {filepath}", error=e)
            return None
    
    @error_handler(ErrorSeverity.MEDIUM, fallback_value={})
    def safe_json_load(self, filepath: str, encoding: str = 'utf-8') -> Dict:
        """Safely load JSON file"""
        try:
            content = self.safe_file_read(filepath, encoding)
            if content is None:
                return {}
            
            data = json.loads(content)
            self.logger.debug(f"Successfully loaded JSON: {filepath}")
            return data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in file {filepath}", error=e)
            return {}
        except Exception as e:
            self.logger.error(f"Failed to load JSON {filepath}", error=e)
            return {}

class DataSanitizer:
    """Data sanitization utilities"""
    
    def __init__(self):
        self.logger = DebugLogger("DataSanitizer")
        self.validator = InputValidator()
    
    def sanitize_calculation_inputs(self, inputs: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """Sanitize inputs for ROI calculations"""
        sanitized = {}
        all_errors = []
        
        # Define expected numeric fields with their validation rules
        numeric_fields = {
            'annual_revenue_clp': {'min': 0, 'max': 1e12, 'default': 10000000},
            'monthly_orders': {'min': 1, 'max': 1000000, 'default': 100},
            'avg_order_value_clp': {'min': 1000, 'max': 10000000, 'default': 25000},
            'labor_costs_clp': {'min': 0, 'max': 100000000, 'default': 1000000},
            'shipping_costs_clp': {'min': 0, 'max': 50000000, 'default': 500000},
            'platform_fees_clp': {'min': 0, 'max': 20000000, 'default': 300000},
            'error_costs_clp': {'min': 0, 'max': 10000000, 'default': 100000},
            'inventory_costs_clp': {'min': 0, 'max': 50000000, 'default': 1000000},
            'investment_clp': {'min': 1000000, 'max': 200000000, 'default': 15000000},
        }
        
        for field, rules in numeric_fields.items():
            value = inputs.get(field)
            result = self.validator.validate_currency_clp(value, field)
            
            if result.is_valid:
                sanitized[field] = result.sanitized_value
            else:
                all_errors.extend(result.errors)
                sanitized[field] = rules['default']
                self.logger.warning(f"Using default value for {field}: {rules['default']}")
        
        # Handle string fields
        string_fields = {
            'industry': {'required': False, 'default': 'retail'},
            'company_name': {'required': False, 'default': 'Cliente'},
        }
        
        for field, rules in string_fields.items():
            value = inputs.get(field)
            result = self.validator.validate_string(value, field, required=rules['required'])
            
            if result.is_valid:
                sanitized[field] = result.sanitized_value
            else:
                all_errors.extend(result.errors)
                sanitized[field] = rules['default']
        
        # Handle list fields
        list_fields = {
            'current_platforms': {'required': False, 'default': []},
        }
        
        for field, rules in list_fields.items():
            value = inputs.get(field)
            result = self.validator.validate_list(value, field, required=rules['required'])
            
            if result.is_valid:
                sanitized[field] = result.sanitized_value
            else:
                all_errors.extend(result.errors)
                sanitized[field] = rules['default']
        
        return sanitized, all_errors
    
    def sanitize_assessment_responses(self, responses: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """Sanitize assessment responses"""
        sanitized = {}
        all_errors = []
        
        # Define response types and their validation
        response_types = {
            # Basic info questions
            'b1': {'type': 'currency', 'required': True, 'default': 50000000},
            'b2': {'type': 'number', 'required': True, 'min': 1, 'max': 100000, 'default': 500},
            'b3': {'type': 'number', 'required': True, 'min': 1, 'max': 1000, 'default': 3},
            'b4': {'type': 'string', 'required': False, 'default': 'Retail'},
            
            # Technology questions
            't1': {'type': 'string', 'required': False, 'default': 'WooCommerce'},
            't2': {'type': 'boolean', 'required': True, 'default': False},
            't3': {'type': 'list', 'required': False, 'default': ['Excel']},
            't4': {'type': 'scale', 'required': True, 'min': 1, 'max': 10, 'default': 5},
            
            # Operations questions
            'o1': {'type': 'number', 'required': True, 'min': 1, 'max': 300, 'default': 15},
            'o2': {'type': 'percentage', 'required': True, 'min': 0, 'max': 100, 'default': 5},
            'o3': {'type': 'number', 'required': True, 'min': 0, 'max': 24, 'default': 6},
            'o4': {'type': 'boolean', 'required': True, 'default': False},
            'o5': {'type': 'string', 'required': False, 'default': 'Mensualmente'},
        }
        
        for field, rules in response_types.items():
            value = responses.get(field)
            
            if rules['type'] == 'currency':
                result = self.validator.validate_currency_clp(value, field)
            elif rules['type'] == 'number':
                result = self.validator.validate_numeric(
                    value, field, 
                    min_value=rules.get('min'), 
                    max_value=rules.get('max')
                )
            elif rules['type'] == 'scale':
                result = self.validator.validate_numeric(
                    value, field, 
                    min_value=rules.get('min', 1), 
                    max_value=rules.get('max', 10)
                )
            elif rules['type'] == 'percentage':
                result = self.validator.validate_percentage(value, field)
            elif rules['type'] == 'boolean':
                # Handle boolean conversion
                if isinstance(value, bool):
                    result = ValidationResult(True, [], [], value)
                elif isinstance(value, str):
                    bool_value = value.lower() in ['true', 'yes', 'sí', '1', 'y']
                    result = ValidationResult(True, [], [], bool_value)
                elif isinstance(value, (int, float)):
                    result = ValidationResult(True, [], [], bool(value))
                else:
                    result = ValidationResult(False, [f"{field} must be boolean"], [], rules['default'])
            elif rules['type'] == 'string':
                result = self.validator.validate_string(value, field, required=rules['required'])
            elif rules['type'] == 'list':
                result = self.validator.validate_list(value, field, required=rules['required'])
            else:
                result = ValidationResult(False, [f"Unknown type for {field}"], [], rules['default'])
            
            if result.is_valid:
                sanitized[field] = result.sanitized_value
            else:
                all_errors.extend(result.errors)
                sanitized[field] = rules['default']
                self.logger.warning(f"Using default value for {field}: {rules['default']}")
        
        return sanitized, all_errors

def create_error_report(errors: List[Dict], warnings: List[Dict]) -> str:
    """Create formatted error report"""
    report = []
    report.append("="*60)
    report.append("ERROR REPORT - SALES TOOLKIT DEBUG")
    report.append("="*60)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Total Errors: {len(errors)}")
    report.append(f"Total Warnings: {len(warnings)}")
    report.append("")
    
    if errors:
        report.append("ERRORS:")
        report.append("-" * 40)
        for i, error in enumerate(errors, 1):
            report.append(f"{i}. [{error.get('timestamp', 'N/A')}] {error.get('message', 'Unknown error')}")
            if error.get('exception'):
                report.append(f"   Exception: {error['exception']}")
            report.append("")
    
    if warnings:
        report.append("WARNINGS:")
        report.append("-" * 40)
        for i, warning in enumerate(warnings, 1):
            report.append(f"{i}. [{warning.get('timestamp', 'N/A')}] {warning.get('message', 'Unknown warning')}")
            report.append("")
    
    report.append("="*60)
    return "\n".join(report)

# Global instances for easy access
validator = InputValidator()
file_handler = FileHandler()
sanitizer = DataSanitizer()

# Common validation functions for quick access
def validate_clp_amount(value: Any, field_name: str = "amount") -> float:
    """Quick CLP validation"""
    result = validator.validate_currency_clp(value, field_name)
    if not result.is_valid:
        raise ValueError(f"Invalid CLP amount for {field_name}: {result.errors}")
    return result.sanitized_value

def validate_percentage(value: Any, field_name: str = "percentage") -> float:
    """Quick percentage validation"""
    result = validator.validate_percentage(value, field_name)
    if not result.is_valid:
        raise ValueError(f"Invalid percentage for {field_name}: {result.errors}")
    return result.sanitized_value

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division with zero handling"""
    try:
        if denominator == 0:
            return default
        result = numerator / denominator
        return result if not (np.isnan(result) or np.isinf(result)) else default
    except Exception:
        return default

def safe_multiply(a: float, b: float, default: float = 0.0) -> float:
    """Safe multiplication with overflow handling"""
    try:
        result = a * b
        return result if not (np.isnan(result) or np.isinf(result)) else default
    except Exception:
        return default

# Test function
if __name__ == "__main__":
    # Test validation
    logger = DebugLogger("test")
    
    # Test numeric validation
    result = validator.validate_currency_clp("50000000", "revenue")
    print(f"Validation result: {result}")
    
    # Test error handling decorator
    @error_handler(ErrorSeverity.MEDIUM, fallback_value="fallback")
    def test_function(x):
        if x < 0:
            raise ValueError("Negative value")
        return x * 2
    
    print(f"Test function with valid input: {test_function(5)}")
    print(f"Test function with invalid input: {test_function(-5)}")
    
    # Print error summary
    print("\nError Summary:")
    print(logger.get_error_summary())