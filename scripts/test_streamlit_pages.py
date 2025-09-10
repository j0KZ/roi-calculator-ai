#!/usr/bin/env python3
"""
Test script to verify Streamlit pages are working correctly
"""

import subprocess
import time
import sys
import os

def test_page(page_file, page_name):
    """Test a single Streamlit page"""
    print(f"\n🔍 Testing {page_name}...")
    
    # Start the Streamlit app
    process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", page_file, "--server.headless", "true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for startup
    time.sleep(3)
    
    # Check if process is still running
    if process.poll() is None:
        print(f"✅ {page_name} started successfully")
        # Terminate the process
        process.terminate()
        process.wait(timeout=5)
        return True
    else:
        # Get error output
        _, stderr = process.communicate()
        print(f"❌ {page_name} failed to start")
        print(f"Error: {stderr[:500]}")
        return False

def main():
    print("=" * 70)
    print("🚀 STREAMLIT PAGES TEST")
    print("=" * 70)
    
    # Test pages
    pages = [
        ("app.py", "Main Application"),
        ("pages/roi_calculator.py", "ROI Calculator"),
        ("pages/assessment_tool.py", "Assessment Tool"),
        ("pages/proposal_generator.py", "Proposal Generator"),
        ("pages/history.py", "History Page"),
        ("pages/templates.py", "Templates Page")
    ]
    
    results = []
    
    for page_file, page_name in pages:
        if os.path.exists(page_file):
            success = test_page(page_file, page_name)
            results.append((page_name, success))
        else:
            print(f"❌ {page_name}: File not found")
            results.append((page_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{name}: {status}")
    
    print("-" * 70)
    print(f"Total: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL PAGES WORKING CORRECTLY!")
        print("✅ Ready to run: streamlit run app.py")
    else:
        print(f"\n⚠️ {failed} pages have issues")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)