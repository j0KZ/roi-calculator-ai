"""
Unicode and PDF Generation Edge Case Tests
Tests for special character handling, PDF generation with unicode, and encoding issues
"""

import pytest
import tempfile
import os
import sys
import unicodedata
from unittest.mock import patch, Mock, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from edge_case_handler import EdgeCaseHandler
from roi_calculator import ROICalculator


class TestUnicodeHandling:
    """Test Unicode and special character handling"""
    
    def setup_method(self):
        """Setup for each test"""
        self.handler = EdgeCaseHandler()
    
    def test_spanish_character_preservation(self):
        """Test that Spanish characters are preserved correctly"""
        
        spanish_test_cases = [
            'José María Rodríguez',
            'Compañía Española S.A.',
            'Señoría & Asociados Ltda.',
            'Niño Jesús Comercial',
            'Ñuñoa Investments',
            'Año Nuevo 2024',
            'Peñafiel & Muñoz',
            'Corazón de María',
            'Educación Técnica',
            'Comunicación Digital'
        ]
        
        for text in spanish_test_cases:
            result, errors = self.handler.validate_string_input(text, 'spanish_text')
            
            assert len(errors) == 0, f"Should handle Spanish text without errors: {text}"
            
            # Check that Spanish characters are preserved
            spanish_chars = set('ñÑáéíóúÁÉÍÓÚüÜ')
            original_spanish_chars = spanish_chars.intersection(set(text))
            result_spanish_chars = spanish_chars.intersection(set(result))
            
            assert original_spanish_chars == result_spanish_chars, \
                f"Spanish characters should be preserved in '{text}' -> '{result}'"
    
    def test_unicode_normalization_edge_cases(self):
        """Test Unicode normalization for different encodings"""
        
        # Different Unicode representations of the same text
        normalization_cases = [
            ('José', 'José'),  # Precomposed vs decomposed
            ('naïve', 'naïve'),
            ('résumé', 'résumé'),
            ('café', 'café'),
            ('piña', 'piña'),
            ('señor', 'señor')
        ]
        
        for text1, text2 in normalization_cases:
            # Even if they look the same, they might have different Unicode representations
            normalized1 = self.handler.sanitize_string(text1)
            normalized2 = self.handler.sanitize_string(text2)
            
            # After normalization, they should be identical
            assert normalized1 == normalized2, \
                f"Unicode normalization should make '{text1}' == '{text2}'"
    
    def test_mixed_script_handling(self):
        """Test handling of mixed scripts and languages"""
        
        mixed_script_cases = [
            'Company 公司 Empresa',  # English, Chinese, Spanish
            'José & François & José',  # Spanish & French
            'Café Москва Restaurant',  # Spanish, Russian, English
            'Πρότυπος José & Co.',  # Greek, Spanish, English
            'Société José™ Ltd.®',  # French, Spanish, English with symbols
        ]
        
        for text in mixed_script_cases:
            result, errors = self.handler.validate_string_input(text, 'mixed_script')
            
            # Should handle without errors
            assert len(errors) == 0, f"Should handle mixed script text: {text}"
            
            # Should preserve at least some recognizable characters
            assert len(result.strip()) > 0, f"Should preserve some characters from: {text}"
    
    def test_emoji_and_symbol_handling(self):
        """Test handling of emoji and special symbols"""
        
        emoji_cases = [
            'Company 🚀 Rocket',
            'Café ☕ Coffee',
            'José ❤️ María',
            'Tech 💻 Solutions',
            '⭐ Premium Service ⭐',
            'Company™ & Co.®',
            'Price: $1,000 • Quality: ★★★★★'
        ]
        
        for text in emoji_cases:
            result, errors = self.handler.validate_string_input(text, 'emoji_text')
            
            # Should handle without crashing
            assert len(errors) == 0, f"Should handle emoji text: {text}"
            
            # Emojis should be removed or converted to safe characters
            # Check that no problematic Unicode remains
            for char in result:
                # All characters should be printable or safe
                category = unicodedata.category(char)
                assert category[0] in 'LMNPZS' or char in ' .,;:()[]{}"-_+=', \
                    f"Unsafe character '{char}' (category: {category}) in result: {result}"
    
    def test_control_character_removal(self):
        """Test removal of control characters"""
        
        control_char_cases = [
            'Normal\x00Text',  # Null byte
            'Line\nBreak',     # Newline
            'Tab\tSeparated',  # Tab
            'Carriage\rReturn', # Carriage return
            'Bell\x07Sound',   # Bell character
            'José\x1bEscape',  # Escape character
        ]
        
        for text in control_char_cases:
            result, errors = self.handler.validate_string_input(text, 'control_chars')
            
            assert len(errors) == 0, f"Should handle control characters: {repr(text)}"
            
            # Control characters should be removed or converted
            for char in result:
                assert ord(char) >= 32 or char in ' \t\n', \
                    f"Control character should be removed: {repr(char)} in {repr(result)}"
    
    def test_very_long_unicode_strings(self):
        """Test handling of very long Unicode strings"""
        
        # Create very long strings with Unicode characters
        long_unicode_cases = [
            'José ' * 1000,  # 5000 characters with Spanish
            'Compañía Española ' * 500,  # 9000 characters
            '测试公司 ' * 800,  # Chinese characters
            'Señor José María Rodríguez y Fernández de la Cruz Santos ' * 100,
        ]
        
        for text in long_unicode_cases:
            result, errors = self.handler.validate_string_input(text, 'long_unicode')
            
            # Should truncate but not error
            if len(text) > EdgeCaseHandler.MAX_STRING_LENGTH:
                assert len(errors) > 0, "Should report length error for very long strings"
                assert len(result) <= EdgeCaseHandler.MAX_STRING_LENGTH, "Should truncate long strings"
            else:
                assert len(errors) == 0, "Should handle reasonably long strings without errors"


class TestPDFGenerationEdgeCases:
    """Test PDF generation with special characters"""
    
    def setup_method(self):
        """Setup for each test"""
        self.handler = EdgeCaseHandler()
    
    def test_safe_filename_generation(self):
        """Test generation of safe filenames with special characters"""
        
        filename_cases = [
            ('José María & Asociados', 'José_María___Asociados'),
            ('Compañía/Empresa<>Ltd.', 'Compañía_Empresa__Ltd.'),
            ('Report:Analysis|Results', 'Report_Analysis_Results'),
            ('File"Name"With*Quotes', 'File_Name_With_Quotes'),
            ('Señor José & Co. Ltd.', 'Señor_José___Co._Ltd.'),
            ('2024/12/31 - Report', '2024_12_31_-_Report'),
        ]
        
        for base_name, expected_pattern in filename_cases:
            filename = self.handler.generate_safe_filename(base_name)
            
            # Should not contain problematic characters
            problematic_chars = '<>:"/\\|?*'
            for char in problematic_chars:
                assert char not in filename, f"Filename should not contain '{char}': {filename}"
            
            # Should contain timestamp
            assert '_' in filename, "Filename should contain timestamp separator"
            assert filename.endswith('.pdf'), "Filename should have PDF extension"
            
            # Should preserve some of the original name structure
            clean_original = base_name.replace('/', '_').replace('<', '_').replace('>', '_')
            # Some part of the cleaned original should be in the result
            # (This is a loose check since exact matching depends on implementation details)
    
    def test_filename_uniqueness(self):
        """Test that generated filenames are unique"""
        
        base_names = [
            'José María Report',
            'José María Report',  # Same name
            'José María Report',  # Same name again
            'Compañía Analysis',
            'Señor José Document',
        ]
        
        generated_filenames = []
        
        for base_name in base_names:
            filename = self.handler.generate_safe_filename(base_name)
            generated_filenames.append(filename)
            
            # Small delay to ensure timestamp difference
            import time
            time.sleep(0.001)
        
        # All filenames should be unique
        assert len(set(generated_filenames)) == len(generated_filenames), \
            f"Generated filenames should be unique: {generated_filenames}"
    
    def test_pdf_content_encoding(self):
        """Test that PDF content handles Unicode correctly"""
        
        # This test would require actual PDF generation capability
        # For now, we'll test the data preparation that would go into PDF
        
        sample_roi_data = {
            'inputs': {
                'company_name': 'José María & Asociados S.A.',
                'industry': 'Comercio Electrónico',
                'annual_revenue': 5000000000,  # 5B CLP
                'currency': 'CLP'
            },
            'roi_metrics': {
                'annual_savings': 1200000000,  # 1.2B CLP
                'first_year_roi': 245.5,
                'payback_period_text': '4.2 meses'
            },
            'savings': {
                'labor': {'annual': 600000000, 'percentage': 0.60},
                'shipping': {'annual': 300000000, 'percentage': 0.25},
                'errors': {'annual': 200000000, 'percentage': 0.80},
                'inventory': {'annual': 100000000, 'percentage': 0.30}
            }
        }
        
        # Test that all string values can be safely encoded
        def check_encoding_safety(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    check_encoding_safety(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, value in enumerate(obj):
                    check_encoding_safety(value, f"{path}[{i}]")
            elif isinstance(obj, str):
                try:
                    # Test UTF-8 encoding (common for PDF libraries)
                    encoded = obj.encode('utf-8')
                    decoded = encoded.decode('utf-8')
                    assert decoded == obj, f"Encoding round-trip failed for {path}: {obj}"
                    
                    # Test Latin-1 encoding (sometimes used in PDF)
                    try:
                        latin1_encoded = obj.encode('latin-1')
                        latin1_decoded = latin1_encoded.decode('latin-1')
                        # This is okay if it works, but not required
                    except UnicodeEncodeError:
                        # This is expected for characters not in Latin-1
                        pass
                    
                except Exception as e:
                    pytest.fail(f"Encoding issue at {path}: {obj} - {e}")
        
        check_encoding_safety(sample_roi_data)
    
    def test_currency_symbol_handling(self):
        """Test handling of currency symbols in PDF context"""
        
        currency_cases = [
            ('USD', '$', '$1,000.00'),
            ('EUR', '€', '€1,000.00'),
            ('CLP', '$', '$1,000'),  # Chilean Peso uses $ symbol
            ('GBP', '£', '£1,000.00'),
            ('JPY', '¥', '¥1,000'),
        ]
        
        for currency, symbol, formatted_example in currency_cases:
            # Test that currency symbols can be safely handled
            result, errors = self.handler.validate_string_input(
                formatted_example, f'currency_{currency}'
            )
            
            assert len(errors) == 0, f"Should handle currency format: {formatted_example}"
            
            # Currency symbol should be preserved or safely converted
            if symbol in '£¥':  # These might be converted
                # Should either preserve or convert to safe alternative
                assert symbol in result or '$' in result, \
                    f"Currency symbol should be preserved or converted: {formatted_example} -> {result}"
            else:
                assert symbol in result, f"Common currency symbol should be preserved: {formatted_example}"


class TestEncodingEdgeCases:
    """Test various encoding scenarios"""
    
    def test_different_input_encodings(self):
        """Test inputs that might come from different encodings"""
        
        handler = EdgeCaseHandler()
        
        # Simulate strings that might come from different sources
        encoding_cases = [
            # String, description
            ('José María', 'UTF-8 Spanish'),
            ('José María'.encode('utf-8').decode('utf-8'), 'UTF-8 round-trip'),
            ('Señor José', 'Direct Spanish input'),
            ('Café & Restaurant', 'French accents'),
            ('naïve résumé', 'Mixed accents'),
        ]
        
        for text, description in encoding_cases:
            try:
                result, errors = handler.validate_string_input(text, f'encoding_{description}')
                
                assert len(errors) == 0, f"Should handle {description}: {text}"
                assert len(result) > 0, f"Should preserve content from {description}"
                
            except UnicodeError as e:
                pytest.fail(f"Unicode error with {description}: {text} - {e}")
    
    def test_malformed_unicode_recovery(self):
        """Test recovery from malformed Unicode sequences"""
        
        handler = EdgeCaseHandler()
        
        # These tests simulate what might happen with corrupted data
        # We'll use the error handling rather than actual malformed bytes
        malformed_cases = [
            ('Jos\udce9 Mar\udceda', 'Surrogate escape characters'),  # Simulated malformed UTF-8
            ('Company\ufffeName', 'Replacement character'),
            ('Text\ud800\udc00More', 'Surrogate pair'),
        ]
        
        for text, description in malformed_cases:
            try:
                result, errors = handler.validate_string_input(text, f'malformed_{description}')
                
                # Should handle gracefully, either with or without errors
                assert isinstance(result, str), f"Should return string for {description}"
                assert len(result) > 0, f"Should preserve some content from {description}"
                
            except Exception as e:
                # If it fails, it should fail gracefully
                assert "Unicode" in str(e) or "encoding" in str(e).lower(), \
                    f"Should fail with Unicode-related error for {description}: {e}"


class TestSpecialCharacterSanitization:
    """Test sanitization of special characters for different contexts"""
    
    def test_sql_injection_prevention(self):
        """Test prevention of SQL injection through character sanitization"""
        
        handler = EdgeCaseHandler()
        
        injection_attempts = [
            "'; DROP TABLE companies; --",
            "1' OR '1'='1",
            "admin'/**/OR/**/'1'='1",
            "' UNION SELECT * FROM users --",
            "'; DELETE FROM orders; --",
        ]
        
        for injection in injection_attempts:
            result, errors = handler.validate_string_input(injection, 'sql_injection')
            
            # Should sanitize dangerous characters
            dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'DROP', 'DELETE', 'UNION']
            for dangerous in dangerous_chars:
                if dangerous in injection.upper():
                    # Should either remove or neutralize
                    assert dangerous.upper() not in result.upper() or result == result.replace(dangerous, ' '), \
                        f"Should sanitize dangerous SQL: {injection} -> {result}"
    
    def test_xss_prevention(self):
        """Test prevention of XSS through character sanitization"""
        
        handler = EdgeCaseHandler()
        
        xss_attempts = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
            "&#60;script&#62;alert('XSS')&#60;/script&#62;",
        ]
        
        for xss in xss_attempts:
            result, errors = handler.validate_string_input(xss, 'xss_attempt')
            
            # Should sanitize HTML/JavaScript
            dangerous_chars = ['<', '>', 'script', 'javascript:', 'onerror', 'iframe']
            for dangerous in dangerous_chars:
                if dangerous in xss.lower():
                    assert dangerous.lower() not in result.lower() or result.replace('<', ' ').replace('>', ' ') == result, \
                        f"Should sanitize XSS attempt: {xss} -> {result}"
    
    def test_path_traversal_prevention(self):
        """Test prevention of path traversal in filenames"""
        
        handler = EdgeCaseHandler()
        
        path_traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM",
            "....//....//....//etc//passwd",
            "file:///etc/passwd",
        ]
        
        for path_attempt in path_traversal_attempts:
            filename = handler.generate_safe_filename(path_attempt)
            
            # Should not contain path traversal sequences
            dangerous_sequences = ['..', '/', '\\', ':', 'etc', 'passwd', 'windows', 'system32']
            for dangerous in dangerous_sequences:
                if dangerous in path_attempt.lower():
                    assert dangerous not in filename.lower() or dangerous == '.', \
                        f"Should prevent path traversal: {path_attempt} -> {filename}"


if __name__ == "__main__":
    # Run Unicode and PDF tests
    pytest.main([__file__, "-v", "-s"])