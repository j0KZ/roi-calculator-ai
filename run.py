#!/usr/bin/env python3
"""
ROI Calculator - Main Entry Point
Supports both CLI and web interface modes
"""

import sys
import os
import argparse
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))


def run_cli():
    """Run command line interface"""
    try:
        from cli_interface import main as cli_main
        cli_main()
    except ImportError as e:
        print(f"Error importing CLI interface: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)


def run_web():
    """Run web interface"""
    try:
        from web_interface import app
        
        # Set correct template and static folders
        app.template_folder = str(current_dir / 'templates')
        app.static_folder = str(current_dir / 'static')
        
        print("Starting ROI Calculator Web Interface...")
        print(f"Templates directory: {app.template_folder}")
        print(f"Static files directory: {app.static_folder}")
        print("Access the calculator at: http://localhost:5000")
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except ImportError as e:
        print(f"Error importing web interface: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)


def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask', 'reportlab', 'matplotlib', 
        'numpy', 'pandas', 'PIL'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall missing packages with:")
        print("  pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="E-commerce Operations ROI Calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                    # Run web interface (default)
  python run.py --web              # Run web interface
  python run.py --cli              # Run command line interface
  python run.py --check-deps       # Check dependencies
        """
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Run command line interface'
    )
    
    parser.add_argument(
        '--web',
        action='store_true',
        help='Run web interface (default)'
    )
    
    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='Check if required dependencies are installed'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='ROI Calculator v1.0.0'
    )
    
    args = parser.parse_args()
    
    # Check dependencies if requested
    if args.check_deps:
        if check_dependencies():
            print("All required dependencies are installed!")
        sys.exit(0)
    
    # Check dependencies before running
    if not check_dependencies():
        sys.exit(1)
    
    # Determine which interface to run
    if args.cli:
        run_cli()
    else:
        # Default to web interface
        run_web()


if __name__ == "__main__":
    main()