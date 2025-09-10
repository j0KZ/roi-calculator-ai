#!/usr/bin/env python3
"""
History Manager - Manages calculation history and saved results
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class HistoryManager:
    """Manages calculation history and saved results"""
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize history manager
        
        Args:
            storage_dir: Directory for storing history files
        """
        if storage_dir is None:
            storage_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'history')
        
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        
        self.history_file = os.path.join(self.storage_dir, 'calculation_history.json')
        self.history = self._load_history()
        
    def _load_history(self) -> List[Dict]:
        """Load history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading history: {e}")
        
        return []
    
    def _save_history(self) -> None:
        """Save history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving history: {e}")
    
    def add_calculation(self, calculation_type: str, inputs: Dict, results: Dict, 
                       metadata: Optional[Dict] = None) -> str:
        """
        Add a new calculation to history
        
        Args:
            calculation_type: Type of calculation (roi, tax, assessment, etc.)
            inputs: Input parameters used
            results: Calculation results
            metadata: Additional metadata
            
        Returns:
            Unique ID for the calculation
        """
        calculation_id = f"{calculation_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        entry = {
            'id': calculation_id,
            'type': calculation_type,
            'timestamp': datetime.now().isoformat(),
            'inputs': inputs,
            'results': results,
            'metadata': metadata or {}
        }
        
        self.history.append(entry)
        self._save_history()
        
        logger.info(f"Added calculation to history: {calculation_id}")
        return calculation_id
    
    def get_calculation(self, calculation_id: str) -> Optional[Dict]:
        """
        Get a specific calculation from history
        
        Args:
            calculation_id: Unique ID of the calculation
            
        Returns:
            Calculation data or None if not found
        """
        for entry in self.history:
            if entry['id'] == calculation_id:
                return entry
        return None
    
    def get_recent_calculations(self, limit: int = 10, 
                               calculation_type: Optional[str] = None) -> List[Dict]:
        """
        Get recent calculations from history
        
        Args:
            limit: Maximum number of calculations to return
            calculation_type: Filter by calculation type
            
        Returns:
            List of recent calculations
        """
        filtered = self.history
        
        if calculation_type:
            filtered = [e for e in filtered if e['type'] == calculation_type]
        
        # Sort by timestamp (most recent first)
        filtered.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return filtered[:limit]
    
    def search_history(self, query: str, field: str = 'all') -> List[Dict]:
        """
        Search history for matching calculations
        
        Args:
            query: Search query
            field: Field to search in ('all', 'inputs', 'results', 'metadata')
            
        Returns:
            List of matching calculations
        """
        results = []
        query_lower = query.lower()
        
        for entry in self.history:
            if field == 'all':
                # Search in all fields
                entry_str = json.dumps(entry, default=str).lower()
                if query_lower in entry_str:
                    results.append(entry)
            elif field in entry:
                # Search in specific field
                field_str = json.dumps(entry[field], default=str).lower()
                if query_lower in field_str:
                    results.append(entry)
        
        return results
    
    def delete_calculation(self, calculation_id: str) -> bool:
        """
        Delete a calculation from history
        
        Args:
            calculation_id: Unique ID of the calculation
            
        Returns:
            True if deleted, False if not found
        """
        for i, entry in enumerate(self.history):
            if entry['id'] == calculation_id:
                del self.history[i]
                self._save_history()
                logger.info(f"Deleted calculation from history: {calculation_id}")
                return True
        
        return False
    
    def clear_history(self, calculation_type: Optional[str] = None) -> int:
        """
        Clear calculation history
        
        Args:
            calculation_type: Clear only specific type of calculations
            
        Returns:
            Number of calculations cleared
        """
        if calculation_type:
            original_count = len(self.history)
            self.history = [e for e in self.history if e['type'] != calculation_type]
            cleared = original_count - len(self.history)
        else:
            cleared = len(self.history)
            self.history = []
        
        self._save_history()
        logger.info(f"Cleared {cleared} calculations from history")
        return cleared
    
    def export_history(self, format: str = 'json', 
                       calculation_type: Optional[str] = None) -> str:
        """
        Export history in specified format
        
        Args:
            format: Export format ('json', 'csv')
            calculation_type: Filter by calculation type
            
        Returns:
            Exported data as string
        """
        data = self.history
        
        if calculation_type:
            data = [e for e in data if e['type'] == calculation_type]
        
        if format == 'json':
            return json.dumps(data, indent=2, default=str)
        
        elif format == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            
            if data:
                # Get all unique keys from all entries
                all_keys = set()
                for entry in data:
                    all_keys.update(self._flatten_dict(entry).keys())
                
                writer = csv.DictWriter(output, fieldnames=sorted(all_keys))
                writer.writeheader()
                
                for entry in data:
                    flattened = self._flatten_dict(entry)
                    writer.writerow(flattened)
            
            return output.getvalue()
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """
        Flatten nested dictionary for CSV export
        
        Args:
            d: Dictionary to flatten
            parent_key: Parent key for nested items
            sep: Separator for keys
            
        Returns:
            Flattened dictionary
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                items.append((new_key, json.dumps(v, default=str)))
            else:
                items.append((new_key, v))
        
        return dict(items)
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about calculation history
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_calculations': len(self.history),
            'calculations_by_type': {},
            'calculations_by_date': {},
            'average_results': {}
        }
        
        for entry in self.history:
            # Count by type
            calc_type = entry['type']
            stats['calculations_by_type'][calc_type] = \
                stats['calculations_by_type'].get(calc_type, 0) + 1
            
            # Count by date
            date = entry['timestamp'][:10]  # Extract date part
            stats['calculations_by_date'][date] = \
                stats['calculations_by_date'].get(date, 0) + 1
        
        return stats


def main():
    """Test the history manager"""
    manager = HistoryManager()
    
    # Add test calculation
    calc_id = manager.add_calculation(
        calculation_type='roi',
        inputs={'investment': 1000000, 'revenue': 500000},
        results={'roi': 50, 'payback_months': 24},
        metadata={'company': 'Test Corp', 'user': 'test_user'}
    )
    
    print(f"Added calculation: {calc_id}")
    
    # Get recent calculations
    recent = manager.get_recent_calculations(limit=5)
    print(f"Recent calculations: {len(recent)}")
    
    # Get statistics
    stats = manager.get_statistics()
    print(f"Statistics: {stats}")


if __name__ == "__main__":
    main()