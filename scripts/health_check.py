#!/usr/bin/env python3
"""
Health Check Script for monitoring and alerting
"""

import sys
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path

def check_streamlit_health():
    """Check if Streamlit is responding"""
    try:
        # Run process manager status check
        result = subprocess.run(
            ['python3', 'scripts/process_manager.py', 'status'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return False, "Process manager failed"
        
        health = json.loads(result.stdout)
        
        # Check status
        if health['status'] != 'running':
            return False, f"Status: {health['status']}"
        
        # Check memory usage
        if health['memory_mb'] > 1024:
            return False, f"High memory: {health['memory_mb']:.1f}MB"
        
        # Check port availability
        try:
            response = requests.get(f"http://localhost:{health['port']}", timeout=5)
            if response.status_code != 200:
                return False, f"HTTP {response.status_code}"
        except requests.RequestException as e:
            return False, f"Connection failed: {str(e)}"
        
        return True, "Healthy"
        
    except Exception as e:
        return False, str(e)

def check_data_integrity():
    """Check data files are accessible"""
    data_dir = Path('data')
    history_dir = data_dir / 'history'
    
    if not data_dir.exists():
        return False, "Data directory missing"
    
    if not history_dir.exists():
        return False, "History directory missing"
    
    # Check if history files are readable
    try:
        history_files = list(history_dir.glob('*.json'))
        if history_files:
            # Try to read the most recent file
            latest_file = max(history_files, key=lambda p: p.stat().st_mtime)
            with open(latest_file) as f:
                json.load(f)
    except Exception as e:
        return False, f"Data integrity issue: {str(e)}"
    
    return True, "Data OK"

def main():
    """Run all health checks"""
    checks = {
        'streamlit': check_streamlit_health(),
        'data': check_data_integrity()
    }
    
    all_healthy = all(status for status, _ in checks.values())
    
    # Create health report
    report = {
        'timestamp': datetime.now().isoformat(),
        'healthy': all_healthy,
        'checks': {
            name: {'status': 'OK' if status else 'FAIL', 'message': msg}
            for name, (status, msg) in checks.items()
        }
    }
    
    # Output JSON report
    print(json.dumps(report, indent=2))
    
    # Exit with appropriate code
    sys.exit(0 if all_healthy else 1)

if __name__ == '__main__':
    main()