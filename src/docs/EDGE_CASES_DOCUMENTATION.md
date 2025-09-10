# Edge Case Handling Documentation

## Overview

This document describes the comprehensive edge case handling system implemented for the Factorio ROI Calculator. The system provides robust validation, error recovery, and graceful degradation to ensure the calculator handles all possible input scenarios without crashing.

## Architecture

### Core Components

1. **EdgeCaseHandler** (`edge_case_handler.py`)
   - Primary validation and sanitization engine
   - Handles numeric, string, and currency validations
   - Chilean market-specific processing
   - Memory and performance monitoring

2. **EnhancedROICalculator** (`enhanced_roi_calculator_with_edge_cases.py`)
   - Extends base ROI Calculator with edge case handling
   - Integrates validation with calculation logic
   - Provides fallback calculations and error recovery

3. **Test Suite** (`tests/test_*.py`)
   - Comprehensive test coverage for all edge cases
   - Automated testing of validation logic
   - Performance and stress testing

4. **Test Scenarios** (`edge_case_scenarios.json`)
   - Predefined edge case scenarios
   - Real-world test data
   - Performance benchmarks

## Edge Case Categories

### 1. Extreme Values

#### Numeric Extremes
- **Zero values**: Revenue = $0, Orders = 0
- **Negative values**: Automatically converted to positive
- **Very large values**: $1 trillion+ revenues (capped at limits)
- **Infinite values**: `float('inf')`, `-inf` (converted to safe values)
- **NaN values**: `float('nan')` (converted to 0)
- **Very small values**: Values < 1e-10 (precision warnings)

#### String Extremes
- **Very long strings**: Truncated at 10,000 characters
- **Empty strings**: Handled gracefully
- **Special characters**: Sanitized for safety

### 2. Input Format Variations

#### Numeric Formats
```python
# All handled correctly:
"1,000,000.50"    # Comma thousands separator
"$1,500.00"       # Currency symbol prefix
"€2,500.75"       # Euro symbol
"1.5e6"          # Scientific notation
"inf"            # String infinity
"nan"            # String NaN
```

#### String Encoding
- **UTF-8**: Full support for international characters
- **Spanish characters**: `ñ`, `á`, `é`, `í`, `ó`, `ú` preserved
- **Unicode normalization**: Different encodings normalized
- **Control characters**: Removed or sanitized

### 3. Chilean Market Specifics

#### UF (Unidad de Fomento) Handling
```python
# UF conversion example
{
    'uf_amount': 1000,           # Input in UF
    'clp_from_uf': 36_500_000    # Auto-converted to CLP
}
```

#### Inflation Scenarios
- **Normal inflation**: 0-5% handled normally
- **High inflation**: 5-50% with warnings
- **Hyperinflation**: >50% capped at maximum
- **Deflation**: Negative rates supported down to -50%

#### IVA (Chilean VAT)
- **Automatic IVA calculation**: 19% tax automatically applied
- **IVA-inclusive reporting**: Separate line items for tax amounts

### 4. Concurrent Access

#### Thread Safety
- **Multiple simultaneous calculations**: Up to 100 concurrent
- **Resource contention**: Handled with proper locking
- **Memory isolation**: Each calculation independent

#### Performance Under Load
- **High-frequency calculations**: 50+ calculations/second
- **Memory management**: Garbage collection optimization
- **Timeout handling**: 30-second calculation timeout

### 5. Memory Limitations

#### Memory Monitoring
```python
# Memory usage tracking
handler.check_memory_usage()  # Returns True if under 1GB limit
```

#### Large Dataset Handling
- **Billion-dollar companies**: Revenue up to $1 trillion
- **Million orders/month**: Handled efficiently
- **Memory-efficient calculations**: Optimized algorithms

### 6. Network Failures

#### Currency API Failures
- **Primary API down**: Fallback to cached rates
- **Network timeout**: Use hardcoded fallback rates
- **Malformed responses**: Error recovery with defaults

#### Retry Logic
- **Exponential backoff**: For transient failures
- **Circuit breaker**: Prevent cascade failures
- **Graceful degradation**: Continue with fallback data

### 7. Special Characters and Security

#### Spanish Character Support
```python
# Preserved correctly:
"José María & Asociados S.A."
"Compañía Española Ltda."
"Señoría Ñuñoa SpA"
```

#### Security Sanitization
```python
# XSS Prevention
"<script>alert('XSS')</script>"  # → Sanitized output
"javascript:alert('XSS')"       # → Safe string

# SQL Injection Prevention
"'; DROP TABLE companies; --"   # → Sanitized output
"1' OR '1'='1"                  # → Safe string
```

#### PDF Generation Safety
- **Safe filenames**: Special characters removed/replaced
- **Unicode in PDFs**: Proper encoding for international text
- **File path traversal**: Prevention of directory traversal attacks

## Validation Rules

### Input Validation

#### Required Fields
```python
REQUIRED_FIELDS = [
    'annual_revenue',
    'monthly_orders', 
    'avg_order_value',
    'labor_costs',
    'shipping_costs',
    'error_costs',
    'inventory_costs',
    'service_investment'
]
```

#### Business Rules
1. **Minimum business size**: Warning if revenue < $100K
2. **Investment reasonableness**: Warning if investment > 50% of revenue
3. **Order consistency**: Cross-validation of orders × AOV vs revenue
4. **Industry cost ratios**: Validation against industry benchmarks

### Cross-Validation

#### Revenue Consistency
```python
calculated_revenue = monthly_orders * avg_order_value * 12
# Warning if differs from stated annual_revenue by >30%
```

#### Cost Structure Validation
```python
# Industry-specific cost ratio expectations
EXPECTED_COST_RATIOS = {
    'retail': (0.7, 0.9),
    'wholesale': (0.8, 0.95),
    'ecommerce': (0.65, 0.85)
}
```

## Error Recovery

### Graceful Degradation

#### Calculation Failures
1. **Division by zero**: Return safe fallback values
2. **Numerical overflow**: Cap at maximum reasonable values
3. **Invalid inputs**: Use corrected values with warnings
4. **Missing data**: Provide default values

#### Fallback Calculations
```python
# Conservative fallback estimates
estimated_savings = total_costs * 0.3  # 30% savings estimate
estimated_roi = ((estimated_savings - investment) / investment) * 100
```

### Error Reporting

#### Validation Results
```python
{
    'is_valid': False,
    'errors': ['Invalid revenue value'],
    'warnings': ['High cost ratio detected'],
    'corrected_inputs': {...},
    'processing_time_ms': 45.2,
    'memory_ok': True
}
```

## Testing Strategy

### Test Categories

1. **Unit Tests**: Individual validation functions
2. **Integration Tests**: End-to-end calculation flows
3. **Edge Case Tests**: Boundary conditions and extremes
4. **Performance Tests**: Speed and memory usage
5. **Stress Tests**: Concurrent access and high load
6. **Security Tests**: Input sanitization and safety

### Test Scenarios

#### Automated Test Suite
- **2,000+ test cases**: Covering all edge conditions
- **Performance benchmarks**: Speed and memory limits
- **Concurrent testing**: Multi-threaded validation
- **Real-world data**: Based on actual client scenarios

#### Continuous Integration
```bash
# Run all edge case tests
python tests/test_edge_case_runner.py

# Run specific test categories
pytest tests/test_edge_cases.py -v
pytest tests/test_chilean_edge_cases.py -v
pytest tests/test_performance_edge_cases.py -v
pytest tests/test_unicode_pdf_edge_cases.py -v
```

## Performance Specifications

### Response Time Limits
- **Simple calculation**: < 100ms
- **Complex calculation**: < 500ms
- **Concurrent calculations**: < 30s for 100 simultaneous

### Memory Limits
- **Single calculation**: < 50MB additional memory
- **Maximum memory usage**: 1GB total
- **Memory leak detection**: Automated monitoring

### Throughput
- **Sequential calculations**: 50+ per second
- **Concurrent calculations**: 100+ simultaneous
- **Stress test capacity**: 1000+ calculations in test suite

## Configuration Options

### EdgeCaseHandler Settings
```python
handler = EdgeCaseHandler()
handler.MAX_REVENUE = 1e12          # $1 trillion max
handler.MAX_STRING_LENGTH = 10000   # 10K character limit
handler.MAX_MEMORY_MB = 1024        # 1GB memory limit
```

### EnhancedROICalculator Settings
```python
calculator = EnhancedROICalculator(
    strict_validation=False,    # Allow corrected inputs
    max_memory_mb=1024         # Memory limit
)
```

## Monitoring and Logging

### Validation Logging
```python
# Automatic logging of validation issues
logger.info("Using cached exchange rates")
logger.warning("High memory usage detected")
logger.error("API request failed: Network timeout")
```

### Performance Metrics
```python
# Built-in performance tracking
validation_info = {
    'processing_time_ms': 45.2,
    'memory_ok': True,
    'total_errors': 0,
    'total_warnings': 2
}
```

## Best Practices

### Input Handling
1. **Always validate inputs** before calculation
2. **Sanitize string inputs** to prevent security issues
3. **Provide meaningful error messages** to users
4. **Log validation issues** for debugging

### Error Recovery
1. **Fail gracefully** rather than crashing
2. **Provide fallback values** when possible
3. **Warn users** about corrected inputs
4. **Maintain calculation consistency**

### Performance Optimization
1. **Monitor memory usage** during calculations
2. **Use efficient algorithms** for large datasets
3. **Implement proper caching** for repeated calculations
4. **Handle concurrent access** safely

## Troubleshooting

### Common Issues

#### Validation Failures
```python
# Problem: Input validation fails
# Solution: Check validation_info for specific errors
result = calculator.calculate_roi(inputs)
if not result['validation_info']['validation_passed']:
    errors = result['validation_info']['input_errors']
    # Address specific validation errors
```

#### Performance Issues
```python
# Problem: Slow calculations
# Solution: Check processing time and memory usage
processing_time = result['validation_info']['processing_time_ms']
if processing_time > 1000:  # More than 1 second
    # Investigate input size and complexity
```

#### Memory Issues
```python
# Problem: High memory usage
# Solution: Monitor and optimize
if not result['validation_info']['memory_ok']:
    # Reduce calculation complexity or increase limits
```

### Debugging Tools

#### Validation Summary
```python
# Get detailed validation information
summary = handler.get_validation_summary()
print(f"Errors: {summary['total_errors']}")
print(f"Warnings: {summary['total_warnings']}")
print(f"Processing time: {summary['processing_time']}s")
```

#### Test Runner
```bash
# Run comprehensive edge case testing
python tests/test_edge_case_runner.py
```

## Future Enhancements

### Planned Improvements
1. **Machine learning validation**: Intelligent input correction
2. **Real-time monitoring**: Live performance dashboards
3. **Advanced caching**: Redis-based caching system
4. **API rate limiting**: Prevent abuse and ensure stability

### Extensibility
1. **Custom validation rules**: Industry-specific validations
2. **Pluggable error handlers**: Custom error recovery logic
3. **Configurable limits**: Runtime configuration updates
4. **Multiple languages**: Internationalization support

---

## Quick Reference

### Validation Methods
```python
from edge_case_handler import EdgeCaseHandler

handler = EdgeCaseHandler()

# Validate numeric input
value, errors = handler.validate_numeric_input(input_value, 'field_name')

# Validate string input
text, errors = handler.validate_string_input(input_text, 'field_name')

# Validate currency
amount, errors = handler.validate_currency_input(amount, 'USD', 'field_name')

# Comprehensive ROI input validation
validation_result = handler.validate_roi_inputs(inputs)
```

### Enhanced Calculator Usage
```python
from enhanced_roi_calculator_with_edge_cases import EnhancedROICalculator

calculator = EnhancedROICalculator()
result = calculator.calculate_roi(inputs)

# Check if calculation succeeded
if result.get('success', True):
    roi = result['roi_metrics']['first_year_roi']
else:
    error = result['error']
    validation_errors = result['validation_info']['input_errors']
```

### Test Execution
```bash
# Run all edge case tests
python tests/test_edge_case_runner.py

# Run specific test files
pytest tests/test_edge_cases.py -v
pytest tests/test_chilean_edge_cases.py -v
```

This comprehensive edge case handling system ensures the Factorio ROI Calculator operates reliably under all conditions, from normal business scenarios to extreme edge cases and malicious inputs.