#!/usr/bin/env python3
"""
Bug Fix Validation Script for Chilean E-commerce Sales Toolkit
Validates that all identified bugs have been properly fixed
"""

import sys
import os
import ast
import re
from typing import List, Dict, Tuple
import importlib.util

# Add project directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pages'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))


class BugFixValidator:
    """Validates that identified bugs have been fixed"""
    
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(__file__))
        self.validation_results = []
        
    def validate_all_fixes(self) -> List[Dict]:
        """Run all bug fix validations"""
        
        print("🔍 VALIDATING BUG FIXES")
        print("="*50)
        
        # Validate each category of fixes
        self.validate_import_fixes()
        self.validate_variable_fixes()
        self.validate_chart_theme_fixes()
        self.validate_session_state_fixes()
        self.validate_function_calls()
        
        return self.validation_results
    
    def validate_import_fixes(self):
        """Validate that all import statement issues are fixed"""
        
        print("\n📦 Validating Import Statement Fixes...")
        
        files_to_check = [
            'pages/roi_calculator.py',
            'pages/assessment_tool.py', 
            'pages/proposal_generator.py'
        ]
        
        for file_path in files_to_check:
            full_path = os.path.join(self.project_root, file_path)
            if not os.path.exists(full_path):
                self.add_validation_result(
                    "Import Fixes", f"❌ File not found: {file_path}", False
                )
                continue
                
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for chart theme imports
            if 'from chart_theme import' in content or 'import chart_theme' in content:
                self.add_validation_result(
                    "Import Fixes", f"✅ {file_path}: Chart theme import added", True
                )
            else:
                # Check for fallback import handling
                if 'try:' in content and 'chart_theme' in content and 'except ImportError:' in content:
                    self.add_validation_result(
                        "Import Fixes", f"✅ {file_path}: Fallback import handling implemented", True
                    )
                else:
                    self.add_validation_result(
                        "Import Fixes", f"⚠️ {file_path}: No chart theme import or fallback found", False
                    )
    
    def validate_variable_fixes(self):
        """Validate that undefined variable issues are fixed"""
        
        print("\n🔧 Validating Variable Definition Fixes...")
        
        # Check ROI calculator for investment variable fix
        roi_calc_path = os.path.join(self.project_root, 'pages/roi_calculator.py')
        if os.path.exists(roi_calc_path):
            with open(roi_calc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for investment_amount variable definition
            if 'investment_amount =' in content and 'session_state' in content:
                self.add_validation_result(
                    "Variable Fixes", "✅ ROI Calculator: investment variable properly defined", True
                )
            else:
                self.add_validation_result(
                    "Variable Fixes", "❌ ROI Calculator: investment variable still undefined", False
                )
        
        # Check proposal generator for undefined variables
        prop_gen_path = os.path.join(self.project_root, 'pages/proposal_generator.py')
        if os.path.exists(prop_gen_path):
            with open(prop_gen_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for proper variable definition before use
            company_name_fixes = content.count("company_name = st.session_state.client_data.get('company_name'")
            email_fixes = content.count("email = st.session_state.client_data.get('email'")
            
            if company_name_fixes > 0:
                self.add_validation_result(
                    "Variable Fixes", f"✅ Proposal Generator: company_name variable fixes ({company_name_fixes} instances)", True
                )
            else:
                self.add_validation_result(
                    "Variable Fixes", "❌ Proposal Generator: company_name variable not fixed", False
                )
                
            if email_fixes > 0:
                self.add_validation_result(
                    "Variable Fixes", f"✅ Proposal Generator: email variable fixes ({email_fixes} instances)", True
                )
            else:
                self.add_validation_result(
                    "Variable Fixes", "❌ Proposal Generator: email variable not fixed", False
                )
    
    def validate_chart_theme_fixes(self):
        """Validate that chart theming issues are fixed"""
        
        print("\n🎨 Validating Chart Theme Fixes...")
        
        # Check chart theme utility file
        chart_theme_path = os.path.join(self.project_root, 'utils/chart_theme.py')
        if os.path.exists(chart_theme_path):
            with open(chart_theme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for proper dark theme implementation
            if 'paper_bgcolor=\'#0a0a0a\'' in content and 'plot_bgcolor=\'#1a1a1a\'' in content:
                self.add_validation_result(
                    "Chart Theme", "✅ Dark theme colors properly configured", True
                )
            else:
                self.add_validation_result(
                    "Chart Theme", "❌ Dark theme colors not properly configured", False
                )
            
            # Check for enhanced theme features
            if 'update_traces' in content and 'marker_line_color' in content:
                self.add_validation_result(
                    "Chart Theme", "✅ Enhanced theme features implemented", True
                )
            else:
                self.add_validation_result(
                    "Chart Theme", "⚠️ Enhanced theme features missing", False
                )
        else:
            self.add_validation_result(
                "Chart Theme", "❌ Chart theme utility file not found", False
            )
        
        # Check that pages are using theme functions
        files_to_check = [
            'pages/roi_calculator.py',
            'pages/assessment_tool.py',
            'pages/proposal_generator.py'
        ]
        
        for file_path in files_to_check:
            full_path = os.path.join(self.project_root, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                apply_dark_theme_count = content.count('apply_dark_theme(')
                get_dark_colors_count = content.count('get_dark_color_sequence()')
                
                if apply_dark_theme_count > 0:
                    self.add_validation_result(
                        "Chart Theme", f"✅ {file_path}: apply_dark_theme used ({apply_dark_theme_count} times)", True
                    )
                else:
                    self.add_validation_result(
                        "Chart Theme", f"⚠️ {file_path}: apply_dark_theme not used", False
                    )
                
                if get_dark_colors_count > 0:
                    self.add_validation_result(
                        "Chart Theme", f"✅ {file_path}: get_dark_color_sequence used ({get_dark_colors_count} times)", True
                    )
    
    def validate_session_state_fixes(self):
        """Validate that session state issues are fixed"""
        
        print("\n💾 Validating Session State Fixes...")
        
        # Check main app.py for proper session state initialization
        app_path = os.path.join(self.project_root, 'app.py')
        if os.path.exists(app_path):
            with open(app_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for comprehensive session state initialization
            required_keys = ['client_data', 'company_name', 'contact_name', 'email', 'investment_clp']
            session_state_init_found = 0
            
            for key in required_keys:
                if f"'{key}'" in content and 'session_state' in content:
                    session_state_init_found += 1
            
            if session_state_init_found >= 3:
                self.add_validation_result(
                    "Session State", f"✅ app.py: Comprehensive session state initialization ({session_state_init_found}/5 keys)", True
                )
            else:
                self.add_validation_result(
                    "Session State", f"❌ app.py: Incomplete session state initialization ({session_state_init_found}/5 keys)", False
                )
    
    def validate_function_calls(self):
        """Validate that function calls are properly structured"""
        
        print("\n🔧 Validating Function Call Fixes...")
        
        # Check for proper function parameter handling
        files_to_check = [
            'pages/roi_calculator.py',
            'pages/assessment_tool.py',
            'pages/proposal_generator.py'
        ]
        
        for file_path in files_to_check:
            full_path = os.path.join(self.project_root, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for try-catch blocks around risky operations
                try_except_count = content.count('try:') + content.count('except')
                if try_except_count > 0:
                    self.add_validation_result(
                        "Function Calls", f"✅ {file_path}: Error handling implemented ({try_except_count//2} blocks)", True
                    )
                else:
                    self.add_validation_result(
                        "Function Calls", f"⚠️ {file_path}: Limited error handling", False
                    )
    
    def validate_syntax_and_imports(self):
        """Validate that all Python files have valid syntax and imports"""
        
        print("\n🔍 Validating Syntax and Import Structure...")
        
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Skip __pycache__ and .git directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        syntax_valid_count = 0
        syntax_error_files = []
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check syntax
                ast.parse(content)
                syntax_valid_count += 1
                
            except SyntaxError as e:
                rel_path = os.path.relpath(file_path, self.project_root)
                syntax_error_files.append(f"{rel_path}:{e.lineno}")
            except Exception as e:
                rel_path = os.path.relpath(file_path, self.project_root)
                syntax_error_files.append(f"{rel_path}:Unknown error")
        
        if syntax_error_files:
            self.add_validation_result(
                "Syntax", f"❌ Syntax errors in {len(syntax_error_files)} files", False
            )
            for error_file in syntax_error_files[:5]:  # Show first 5 errors
                self.add_validation_result(
                    "Syntax", f"  └─ {error_file}", False
                )
        else:
            self.add_validation_result(
                "Syntax", f"✅ All {len(python_files)} Python files have valid syntax", True
            )
    
    def add_validation_result(self, category: str, message: str, success: bool):
        """Add a validation result"""
        self.validation_results.append({
            'category': category,
            'message': message,
            'success': success
        })
        print(f"  {message}")
    
    def generate_report(self) -> Dict:
        """Generate summary report of validation results"""
        
        total_checks = len(self.validation_results)
        successful_checks = sum(1 for result in self.validation_results if result['success'])
        failed_checks = total_checks - successful_checks
        
        categories = {}
        for result in self.validation_results:
            category = result['category']
            if category not in categories:
                categories[category] = {'total': 0, 'success': 0}
            categories[category]['total'] += 1
            if result['success']:
                categories[category]['success'] += 1
        
        return {
            'total_checks': total_checks,
            'successful_checks': successful_checks,
            'failed_checks': failed_checks,
            'success_rate': (successful_checks / total_checks * 100) if total_checks > 0 else 0,
            'categories': categories,
            'all_results': self.validation_results
        }


def main():
    """Run bug fix validation"""
    
    print("🔧 CHILEAN E-COMMERCE SALES TOOLKIT - BUG FIX VALIDATION")
    print("="*70)
    
    validator = BugFixValidator()
    
    # Run all validations
    validator.validate_all_fixes()
    validator.validate_syntax_and_imports()
    
    # Generate report
    report = validator.generate_report()
    
    print("\n" + "="*70)
    print("📊 VALIDATION SUMMARY")
    print("="*70)
    print(f"Total Checks: {report['total_checks']}")
    print(f"Successful: {report['successful_checks']}")
    print(f"Failed: {report['failed_checks']}")
    print(f"Success Rate: {report['success_rate']:.1f}%")
    
    print(f"\n📋 BY CATEGORY")
    print("-"*40)
    for category, stats in report['categories'].items():
        success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
        status_icon = "✅" if success_rate == 100 else "⚠️" if success_rate >= 70 else "❌"
        print(f"{status_icon} {category}: {stats['success']}/{stats['total']} ({success_rate:.0f}%)")
    
    # Show failed checks
    failed_results = [r for r in report['all_results'] if not r['success']]
    if failed_results:
        print(f"\n🚨 REMAINING ISSUES ({len(failed_results)})")
        print("-"*40)
        for result in failed_results:
            print(f"  {result['message']}")
    
    print(f"\n{'='*70}")
    print("🎯 RECOMMENDATIONS")
    print("="*70)
    
    if report['success_rate'] == 100:
        print("🎉 All bug fixes have been successfully validated!")
        print("📈 The application should now be more stable and reliable.")
    elif report['success_rate'] >= 80:
        print("✅ Most bug fixes have been successfully implemented.")
        print("🔧 Address the remaining issues to achieve full stability.")
    elif report['success_rate'] >= 60:
        print("⚠️ Some bug fixes are in place, but significant issues remain.")
        print("🚨 Prioritize fixing the failed validation checks.")
    else:
        print("❌ Many bug fixes still need attention.")
        print("🛠️ Review the validation results and implement the necessary fixes.")
    
    # Specific recommendations based on failed categories
    failed_categories = [cat for cat, stats in report['categories'].items() 
                        if stats['success'] < stats['total']]
    
    if 'Import Fixes' in failed_categories:
        print("\n📦 Import Issues: Ensure all chart_theme imports are properly handled with fallbacks")
    
    if 'Variable Fixes' in failed_categories:
        print("\n🔧 Variable Issues: Define all variables before use, especially from session_state")
    
    if 'Chart Theme' in failed_categories:
        print("\n🎨 Chart Theme Issues: Apply dark theme consistently across all charts")
    
    if 'Session State' in failed_categories:
        print("\n💾 Session State Issues: Initialize all required session state variables in app.py")
    
    if 'Syntax' in failed_categories:
        print("\n🔍 Syntax Issues: Fix Python syntax errors before deployment")
    
    print(f"\n{'='*70}")
    
    return report['success_rate'] == 100


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)