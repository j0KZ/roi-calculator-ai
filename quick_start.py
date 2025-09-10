#!/usr/bin/env python3
"""
Quick Start Script for Sales Toolkit
Launches the integrated revenue generation tools
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'numpy',
        'pandas',
        'scipy',
        'reportlab',
        'pptx',
        'openpyxl',
        'rich'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("⚠️  Missing required packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\nInstalling missing packages...")
        
        # Install missing packages
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_sales_toolkit.txt"])
        print("✅ Dependencies installed successfully!\n")

def main():
    """Main entry point"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     SALES TOOLKIT - E-COMMERCE CONSULTING CHILE         ║
    ║         Herramientas de Venta Rápida v2.0              ║
    ╚══════════════════════════════════════════════════════════╝
    
    🚀 Iniciando herramientas de venta...
    """)
    
    # Check dependencies
    check_dependencies()
    
    # Import and run the toolkit
    try:
        from src.sales_toolkit_launcher import SalesToolkitLauncher
        
        launcher = SalesToolkitLauncher()
        launcher.run()
        
    except ImportError as e:
        print(f"❌ Error importing toolkit: {e}")
        print("\nAsegúrese de estar en el directorio correcto:")
        print("  cd tools/roi-calculator")
        print("  python quick_start.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Gracias por usar Sales Toolkit!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()