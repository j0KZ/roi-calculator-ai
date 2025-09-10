"""
Edge Case Handler for Factorio ROI Calculator
Comprehensive handling of edge cases, boundary conditions, and error scenarios
"""

import math
import re
import sys
import time
import threading
import unicodedata
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
import logging

logger = logging.getLogger(__name__)

class EdgeCaseHandler:
    """Comprehensive edge case handler for ROI calculations"""
    
    # Constants for validation
    MAX_REVENUE = 1e12  # $1 trillion maximum
    MIN_REVENUE = 0
    MAX_EMPLOYEES = 1_000_000
    MAX_STRING_LENGTH = 10_000
    MAX_MEMORY_MB = 1024  # 1GB limit for calculations
    
    # Chilean-specific constants
    UF_TO_CLP_RATE = 36500  # Approximate UF value in CLP
    MAX_INFLATION_RATE = 1.0  # 100% maximum inflation
    MIN_INFLATION_RATE = -0.5  # -50% deflation limit
    
    # Currency limits
    CURRENCY_LIMITS = {
        'USD': {'min': 0, 'max': 1e12},
        'CLP': {'min': 0, 'max': 1e15},  # Higher limit for CLP due to exchange rate
        'EUR': {'min': 0, 'max': 1e12},
        'GBP': {'min': 0, 'max': 1e12}
    }
    
    def __init__(self):
        self.validation_errors = []
        self.warnings = []
        self.memory_usage = 0
        self.start_time = time.time()
        
    def validate_numeric_input(self, value: Any, field_name: str, 
                             min_val: float = 0, max_val: float = None,
                             allow_zero: bool = True, allow_negative: bool = False) -> Tuple[float, List[str]]:
        """
        Comprehensive numeric input validation
        
        Args:
            value: Input value to validate
            field_name: Name of the field for error messages
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            allow_zero: Whether zero values are allowed
            allow_negative: Whether negative values are allowed
            
        Returns:
            Tuple of (validated_value, list_of_errors)
        """
        errors = []
        
        # Handle None values
        if value is None:
            errors.append(f"{field_name}: Value cannot be None")
            return 0.0, errors
            
        # Handle string inputs that might be numbers
        if isinstance(value, str):
            # Remove common formatting characters
            cleaned = re.sub(r'[,\s$€£¥₹]', '', value.strip())
            
            # Handle empty strings
            if not cleaned:
                errors.append(f"{field_name}: Empty string provided")
                return 0.0, errors
                
            # Handle special string cases
            if cleaned.lower() in ['inf', 'infinity', '+inf', '+infinity']:
                errors.append(f"{field_name}: Infinite values not allowed")
                return max_val or self.MAX_REVENUE, errors
                
            if cleaned.lower() in ['-inf', '-infinity']:
                errors.append(f"{field_name}: Negative infinite values not allowed")
                return min_val, errors
                
            if cleaned.lower() in ['nan', 'null', 'undefined']:
                errors.append(f"{field_name}: Invalid numeric value '{cleaned}'")
                return 0.0, errors
                
            # Try to convert to float
            try:
                value = float(cleaned)
            except ValueError:
                try:
                    # Try as Decimal for high precision
                    value = float(Decimal(cleaned))
                except InvalidOperation:
                    errors.append(f"{field_name}: Cannot convert '{cleaned}' to number")
                    return 0.0, errors
        
        # Handle non-numeric types
        if not isinstance(value, (int, float, Decimal)):
            errors.append(f"{field_name}: Must be a number, got {type(value).__name__}")
            return 0.0, errors
        
        # Convert to float
        try:
            value = float(value)
        except (ValueError, OverflowError):
            errors.append(f"{field_name}: Cannot convert to float")
            return 0.0, errors
            
        # Check for NaN and infinity
        if math.isnan(value):
            errors.append(f"{field_name}: NaN (Not a Number) not allowed")
            return 0.0, errors
            
        if math.isinf(value):
            errors.append(f"{field_name}: Infinite values not allowed")
            return max_val or self.MAX_REVENUE, errors
            
        # Check zero values
        if not allow_zero and value == 0:
            errors.append(f"{field_name}: Zero values not allowed")
            return min_val if min_val > 0 else 1.0, errors
            
        # Check negative values
        if not allow_negative and value < 0:
            errors.append(f"{field_name}: Negative values not allowed")
            return abs(value), errors
            
        # Check minimum value
        if value < min_val:
            errors.append(f"{field_name}: Value {value} is below minimum {min_val}")
            return min_val, errors
            
        # Check maximum value
        if max_val is not None and value > max_val:
            errors.append(f"{field_name}: Value {value} exceeds maximum {max_val}")
            return max_val, errors
            
        # Check for extremely small positive values that might cause calculation issues
        if 0 < value < 1e-10:
            self.warnings.append(f"{field_name}: Very small value {value} may cause precision issues")
            
        return value, errors
    
    def validate_string_input(self, value: Any, field_name: str, 
                            max_length: int = None, allow_empty: bool = True,
                            sanitize: bool = True) -> Tuple[str, List[str]]:
        """
        Comprehensive string input validation
        
        Args:
            value: Input value to validate
            field_name: Name of the field for error messages
            max_length: Maximum allowed length
            allow_empty: Whether empty strings are allowed
            sanitize: Whether to sanitize the string
            
        Returns:
            Tuple of (validated_string, list_of_errors)
        """
        errors = []
        
        # Handle None values
        if value is None:
            if allow_empty:
                return "", errors
            else:
                errors.append(f"{field_name}: Value cannot be None")
                return "", errors
        
        # Convert to string
        if not isinstance(value, str):
            value = str(value)
            self.warnings.append(f"{field_name}: Converted {type(value).__name__} to string")
        
        # Handle empty strings
        if not value.strip() and not allow_empty:
            errors.append(f"{field_name}: Empty string not allowed")
            return "", errors
        
        # Check length
        if max_length is None:
            max_length = self.MAX_STRING_LENGTH
            
        if len(value) > max_length:
            errors.append(f"{field_name}: String length {len(value)} exceeds maximum {max_length}")
            value = value[:max_length]
            
        # Sanitize if requested
        if sanitize:
            value = self.sanitize_string(value)
            
        return value, errors
    
    def sanitize_string(self, text: str) -> str:
        """
        Sanitize string input to prevent issues with special characters
        
        Args:
            text: Input text to sanitize
            
        Returns:
            Sanitized text
        """
        if not text:
            return text
            
        # Normalize Unicode
        text = unicodedata.normalize('NFKC', text)
        
        # Remove or replace problematic characters
        # Keep Spanish characters (ñ, á, é, í, ó, ú, ü)
        spanish_chars = 'ñÑáéíóúÁÉÍÓÚüÜ'
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,;:()[]{}"-_+=' + spanish_chars)
        
        # Filter characters
        sanitized = ''.join(char if char in allowed_chars else ' ' for char in text)
        
        # Remove multiple spaces
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        return sanitized
    
    def validate_currency_input(self, amount: Any, currency: str, field_name: str) -> Tuple[float, List[str]]:
        """
        Validate currency amounts with currency-specific limits
        
        Args:
            amount: Currency amount to validate
            currency: Currency code (USD, CLP, EUR, etc.)
            field_name: Name of the field for error messages
            
        Returns:
            Tuple of (validated_amount, list_of_errors)
        """
        errors = []
        
        # Get currency limits
        limits = self.CURRENCY_LIMITS.get(currency.upper(), self.CURRENCY_LIMITS['USD'])
        
        # Validate numeric input
        amount, numeric_errors = self.validate_numeric_input(
            amount, field_name, 
            min_val=limits['min'], 
            max_val=limits['max'],
            allow_zero=True
        )
        
        errors.extend(numeric_errors)
        
        # Currency-specific validations
        if currency.upper() == 'CLP':
            # Chilean Peso - check for reasonable values
            if amount > 0 and amount < 100:
                self.warnings.append(f"{field_name}: Very low CLP amount {amount}, did you mean UF?")
                
        elif currency.upper() in ['JPY']:
            # Japanese Yen - no decimals expected
            if amount != int(amount):
                amount = round(amount)
                self.warnings.append(f"{field_name}: JPY amount rounded to nearest integer")
        
        return amount, errors
    
    def validate_percentage(self, value: Any, field_name: str, 
                          min_percent: float = 0, max_percent: float = 100) -> Tuple[float, List[str]]:
        """
        Validate percentage values
        
        Args:
            value: Percentage value to validate
            field_name: Name of the field for error messages
            min_percent: Minimum percentage allowed
            max_percent: Maximum percentage allowed
            
        Returns:
            Tuple of (validated_percentage, list_of_errors)
        """
        value, errors = self.validate_numeric_input(
            value, field_name,
            min_val=min_percent,
            max_val=max_percent,
            allow_zero=True
        )
        
        # Convert to decimal if it looks like it's already a percentage
        if value > 1 and max_percent <= 1:
            value = value / 100
            self.warnings.append(f"{field_name}: Converted percentage from {value*100}% to decimal {value}")
        
        return value, errors
    
    def handle_chilean_specifics(self, data: Dict) -> Dict:
        """
        Handle Chilean market-specific edge cases
        
        Args:
            data: Input data dictionary
            
        Returns:
            Processed data with Chilean specifics handled
        """
        processed_data = data.copy()
        
        # Handle UF (Unidad de Fomento) conversions
        if 'uf_amount' in data:
            uf_amount = data['uf_amount']
            if uf_amount > 0:
                clp_equivalent = uf_amount * self.UF_TO_CLP_RATE
                processed_data['clp_from_uf'] = clp_equivalent
                self.warnings.append(f"Converted {uf_amount} UF to {clp_equivalent:,.0f} CLP")
        
        # Handle high inflation scenarios
        if 'inflation_rate' in data:
            inflation_rate, errors = self.validate_percentage(
                data['inflation_rate'], 'inflation_rate',
                min_percent=self.MIN_INFLATION_RATE,
                max_percent=self.MAX_INFLATION_RATE
            )
            processed_data['inflation_rate'] = inflation_rate
            
            if inflation_rate > 0.2:  # 20% inflation
                self.warnings.append(f"High inflation rate {inflation_rate*100:.1f}% detected")
        
        # Handle Chilean tax specifics
        if 'include_iva' not in processed_data:
            processed_data['include_iva'] = True
            self.warnings.append("Assuming IVA (19%) should be included in Chilean calculations")
        
        return processed_data
    
    def validate_roi_inputs(self, inputs: Dict) -> Dict:
        """
        Comprehensive validation of ROI calculation inputs
        
        Args:
            inputs: Dictionary of input values
            
        Returns:
            Dictionary with validated inputs and validation results
        """
        validated_inputs = {}
        all_errors = []
        
        # Required fields with their validation parameters
        required_fields = {
            'annual_revenue': {'min_val': 0, 'max_val': self.MAX_REVENUE},
            'monthly_orders': {'min_val': 0, 'max_val': 10_000_000},
            'avg_order_value': {'min_val': 0, 'max_val': 1_000_000},
            'labor_costs': {'min_val': 0, 'max_val': self.MAX_REVENUE / 12},
            'shipping_costs': {'min_val': 0, 'max_val': self.MAX_REVENUE / 12},
            'error_costs': {'min_val': 0, 'max_val': self.MAX_REVENUE / 12},
            'inventory_costs': {'min_val': 0, 'max_val': self.MAX_REVENUE / 12},
            'service_investment': {'min_val': 0, 'max_val': self.MAX_REVENUE}
        }
        
        # Validate each required field
        for field, params in required_fields.items():
            if field in inputs:
                value, errors = self.validate_numeric_input(
                    inputs[field], field, **params, allow_zero=True
                )
                validated_inputs[field] = value
                all_errors.extend(errors)
            else:
                all_errors.append(f"Missing required field: {field}")
                validated_inputs[field] = 0.0
        
        # Validate optional fields
        optional_fields = {
            'company_name': {'max_length': 200},
            'industry': {'max_length': 100},
            'currency': {'max_length': 3},
            'country': {'max_length': 100}
        }
        
        for field, params in optional_fields.items():
            if field in inputs:
                value, errors = self.validate_string_input(
                    inputs[field], field, **params
                )
                validated_inputs[field] = value
                all_errors.extend(errors)
        
        # Cross-validation checks
        cross_validation_errors = self._cross_validate_inputs(validated_inputs)
        all_errors.extend(cross_validation_errors)
        
        return {
            'validated_inputs': validated_inputs,
            'errors': all_errors,
            'warnings': self.warnings.copy(),
            'is_valid': len(all_errors) == 0
        }
    
    def _cross_validate_inputs(self, inputs: Dict) -> List[str]:
        """
        Perform cross-validation checks between related fields
        
        Args:
            inputs: Validated input dictionary
            
        Returns:
            List of cross-validation errors
        """
        errors = []
        
        # Check revenue consistency
        if inputs.get('monthly_orders', 0) > 0 and inputs.get('avg_order_value', 0) > 0:
            calculated_revenue = inputs['monthly_orders'] * inputs['avg_order_value'] * 12
            actual_revenue = inputs.get('annual_revenue', 0)
            
            if abs(calculated_revenue - actual_revenue) > actual_revenue * 0.5:  # 50% tolerance
                self.warnings.append(
                    f"Revenue mismatch: Calculated {calculated_revenue:,.0f} vs provided {actual_revenue:,.0f}"
                )
        
        # Check if costs are reasonable relative to revenue
        total_monthly_costs = (
            inputs.get('labor_costs', 0) +
            inputs.get('shipping_costs', 0) +
            inputs.get('error_costs', 0) +
            inputs.get('inventory_costs', 0)
        )
        
        annual_costs = total_monthly_costs * 12
        annual_revenue = inputs.get('annual_revenue', 0)
        
        if annual_revenue > 0:
            cost_ratio = annual_costs / annual_revenue
            
            if cost_ratio > 1.0:
                errors.append(f"Total costs ({annual_costs:,.0f}) exceed revenue ({annual_revenue:,.0f})")
            elif cost_ratio > 0.8:
                self.warnings.append(f"High cost ratio: {cost_ratio*100:.1f}% of revenue")
            elif cost_ratio < 0.1:
                self.warnings.append(f"Low cost ratio: {cost_ratio*100:.1f}% of revenue - verify inputs")
        
        # Check service investment reasonableness
        service_investment = inputs.get('service_investment', 0)
        if annual_revenue > 0 and service_investment > annual_revenue:
            self.warnings.append(
                f"Service investment ({service_investment:,.0f}) exceeds annual revenue ({annual_revenue:,.0f})"
            )
        
        return errors
    
    def handle_calculation_errors(self, func, *args, **kwargs):
        """
        Wrapper to handle calculation errors gracefully
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Result of function or safe fallback value
        """
        try:
            return func(*args, **kwargs)
        except ZeroDivisionError:
            logger.error("Division by zero in calculation")
            return 0.0
        except OverflowError:
            logger.error("Numerical overflow in calculation")
            return float('inf')
        except ValueError as e:
            logger.error(f"Value error in calculation: {e}")
            return 0.0
        except Exception as e:
            logger.error(f"Unexpected error in calculation: {e}")
            return None
    
    def check_memory_usage(self) -> bool:
        """
        Check if memory usage is within acceptable limits
        
        Returns:
            True if memory usage is acceptable, False otherwise
        """
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb > self.MAX_MEMORY_MB:
                logger.warning(f"Memory usage {memory_mb:.1f}MB exceeds limit {self.MAX_MEMORY_MB}MB")
                return False
                
            return True
        except ImportError:
            # psutil not available, assume memory is OK
            return True
        except Exception as e:
            logger.error(f"Error checking memory usage: {e}")
            return True
    
    def simulate_network_failure(self, failure_rate: float = 0.1) -> bool:
        """
        Simulate network failures for testing
        
        Args:
            failure_rate: Probability of failure (0.0 to 1.0)
            
        Returns:
            True if network is available, False if simulated failure
        """
        import random
        return random.random() > failure_rate
    
    def handle_concurrent_access(self, resource_id: str, max_wait: int = 30):
        """
        Handle concurrent access to resources with timeout
        
        Args:
            resource_id: Identifier for the resource
            max_wait: Maximum wait time in seconds
            
        Returns:
            Context manager for resource access
        """
        return threading.Lock()  # Simple lock for demonstration
    
    def generate_safe_filename(self, base_name: str, extension: str = '.pdf') -> str:
        """
        Generate a safe filename handling special characters
        
        Args:
            base_name: Base name for the file
            extension: File extension
            
        Returns:
            Safe filename string
        """
        # Remove or replace problematic characters
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', base_name)
        safe_name = re.sub(r'\s+', '_', safe_name)
        safe_name = safe_name[:100]  # Limit length
        
        # Add timestamp to ensure uniqueness
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return f"{safe_name}_{timestamp}{extension}"
    
    def validate_date_input(self, date_input: Any, field_name: str) -> Tuple[datetime, List[str]]:
        """
        Validate and parse date inputs
        
        Args:
            date_input: Date input to validate
            field_name: Name of the field for error messages
            
        Returns:
            Tuple of (validated_datetime, list_of_errors)
        """
        errors = []
        
        if date_input is None:
            return datetime.now(), errors
        
        if isinstance(date_input, datetime):
            return date_input, errors
        
        if isinstance(date_input, str):
            # Try different date formats
            date_formats = [
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%m/%d/%Y',
                '%Y-%m-%d %H:%M:%S',
                '%d/%m/%Y %H:%M:%S'
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_input, fmt), errors
                except ValueError:
                    continue
            
            errors.append(f"{field_name}: Unable to parse date '{date_input}'")
            return datetime.now(), errors
        
        errors.append(f"{field_name}: Invalid date type {type(date_input)}")
        return datetime.now(), errors
    
    def get_validation_summary(self) -> Dict:
        """
        Get summary of all validation results
        
        Returns:
            Dictionary with validation summary
        """
        return {
            'total_errors': len(self.validation_errors),
            'total_warnings': len(self.warnings),
            'errors': self.validation_errors.copy(),
            'warnings': self.warnings.copy(),
            'processing_time': time.time() - self.start_time,
            'memory_ok': self.check_memory_usage()
        }