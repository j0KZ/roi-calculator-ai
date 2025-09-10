"""
Version Control System for ROI Calculator
Tracks changes, maintains history, and enables rollback functionality
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from database.connection import get_session
from database.models import Calculation
import difflib


@dataclass
class VersionEntry:
    """Represents a single version entry"""
    version_id: str
    calculation_id: int
    version_number: int
    inputs: Dict
    results: Dict
    changes: List[Dict]
    notes: str
    created_at: str
    created_by: str
    checksum: str


class VersionControl:
    """Manages versioning and change tracking for ROI calculations"""
    
    def __init__(self):
        self.current_versions = {}  # calculation_id -> latest_version_number
    
    def create_version(self, calculation_id: int, inputs: Dict, results: Dict, 
                      notes: str = "", created_by: str = "user") -> VersionEntry:
        """Create a new version of a calculation"""
        try:
            session = get_session()
            
            # Get the calculation
            calculation = session.query(Calculation).get(calculation_id)
            if not calculation:
                raise Exception("Calculation not found")
            
            # Determine version number
            version_number = self._get_next_version_number(calculation_id)
            
            # Get previous version for comparison
            previous_version = self._get_latest_version(calculation_id)
            changes = []
            
            if previous_version:
                changes = self._calculate_changes(previous_version.inputs, inputs)
            else:
                changes = [{"type": "initial", "description": "Initial version created"}]
            
            # Generate version ID and checksum
            version_id = self._generate_version_id(calculation_id, version_number)
            checksum = self._calculate_checksum(inputs, results)
            
            # Create version entry
            version = VersionEntry(
                version_id=version_id,
                calculation_id=calculation_id,
                version_number=version_number,
                inputs=inputs.copy(),
                results=results.copy(),
                changes=changes,
                notes=notes,
                created_at=datetime.now().isoformat(),
                created_by=created_by,
                checksum=checksum
            )
            
            # Store version (in a real implementation, this would go to a versions table)
            # For now, we'll store it in the calculation's metadata
            if not calculation.metadata:
                calculation.metadata = {}
            
            if 'versions' not in calculation.metadata:
                calculation.metadata['versions'] = []
            
            calculation.metadata['versions'].append(asdict(version))
            calculation.updated_at = datetime.utcnow()
            
            session.commit()
            session.close()
            
            # Update current versions cache
            self.current_versions[calculation_id] = version_number
            
            return version
            
        except Exception as e:
            if 'session' in locals():
                session.rollback()
                session.close()
            raise Exception(f"Error creating version: {str(e)}")
    
    def get_version_history(self, calculation_id: int) -> List[VersionEntry]:
        """Get complete version history for a calculation"""
        try:
            session = get_session()
            
            calculation = session.query(Calculation).get(calculation_id)
            if not calculation:
                raise Exception("Calculation not found")
            
            versions = []
            if calculation.metadata and 'versions' in calculation.metadata:
                version_data = calculation.metadata['versions']
                for v_data in version_data:
                    version = VersionEntry(**v_data)
                    versions.append(version)
            
            session.close()
            
            # Sort by version number (newest first)
            versions.sort(key=lambda x: x.version_number, reverse=True)
            
            return versions
            
        except Exception as e:
            if 'session' in locals():
                session.close()
            raise Exception(f"Error getting version history: {str(e)}")
    
    def get_version(self, calculation_id: int, version_number: int) -> Optional[VersionEntry]:
        """Get a specific version"""
        try:
            versions = self.get_version_history(calculation_id)
            
            for version in versions:
                if version.version_number == version_number:
                    return version
            
            return None
            
        except Exception as e:
            raise Exception(f"Error getting version: {str(e)}")
    
    def _get_latest_version(self, calculation_id: int) -> Optional[VersionEntry]:
        """Get the latest version for a calculation"""
        try:
            versions = self.get_version_history(calculation_id)
            return versions[0] if versions else None
            
        except Exception as e:
            return None
    
    def compare_versions(self, calculation_id: int, version1: int, version2: int) -> Dict:
        """Compare two versions and show differences"""
        try:
            v1 = self.get_version(calculation_id, version1)
            v2 = self.get_version(calculation_id, version2)
            
            if not v1 or not v2:
                raise Exception("One or both versions not found")
            
            # Compare inputs
            input_diff = self._compare_inputs(v1.inputs, v2.inputs)
            
            # Compare key results
            results_diff = self._compare_results(v1.results, v2.results)
            
            # Generate summary
            summary = self._generate_comparison_summary(v1, v2, input_diff, results_diff)
            
            return {
                'version1': {
                    'number': v1.version_number,
                    'created_at': v1.created_at,
                    'notes': v1.notes
                },
                'version2': {
                    'number': v2.version_number,
                    'created_at': v2.created_at,
                    'notes': v2.notes
                },
                'input_differences': input_diff,
                'results_differences': results_diff,
                'summary': summary
            }
            
        except Exception as e:
            raise Exception(f"Error comparing versions: {str(e)}")
    
    def rollback_to_version(self, calculation_id: int, target_version: int, 
                          notes: str = "") -> VersionEntry:
        """Rollback calculation to a previous version"""
        try:
            # Get target version
            target = self.get_version(calculation_id, target_version)
            if not target:
                raise Exception(f"Version {target_version} not found")
            
            # Get current calculation
            session = get_session()
            calculation = session.query(Calculation).get(calculation_id)
            if not calculation:
                raise Exception("Calculation not found")
            
            # Update calculation with target version data
            for field, value in target.inputs.items():
                if hasattr(calculation, field):
                    setattr(calculation, field, value)
            
            # Update results
            calculation.results = target.results.copy()
            calculation.updated_at = datetime.utcnow()
            
            # Add rollback note
            rollback_notes = f"Rolled back to version {target_version}. {notes}".strip()
            
            session.commit()
            session.close()
            
            # Create new version to record the rollback
            from roi_calculator import ROICalculator
            calculator = ROICalculator()
            recalculated_results = calculator.calculate_roi(target.inputs)
            
            new_version = self.create_version(
                calculation_id=calculation_id,
                inputs=target.inputs,
                results=recalculated_results,
                notes=rollback_notes,
                created_by="system_rollback"
            )
            
            return new_version
            
        except Exception as e:
            if 'session' in locals():
                session.rollback()
                session.close()
            raise Exception(f"Error rolling back: {str(e)}")
    
    def get_audit_trail(self, calculation_id: int, limit: int = 50) -> List[Dict]:
        """Get audit trail for a calculation"""
        try:
            versions = self.get_version_history(calculation_id)
            
            audit_entries = []
            for version in versions[:limit]:
                entry = {
                    'version_number': version.version_number,
                    'action': self._determine_action_type(version),
                    'created_at': version.created_at,
                    'created_by': version.created_by,
                    'notes': version.notes,
                    'changes_count': len(version.changes),
                    'significant_changes': self._get_significant_changes(version.changes)
                }
                audit_entries.append(entry)
            
            return audit_entries
            
        except Exception as e:
            raise Exception(f"Error getting audit trail: {str(e)}")
    
    def _calculate_changes(self, old_inputs: Dict, new_inputs: Dict) -> List[Dict]:
        """Calculate changes between two input sets"""
        changes = []
        
        # Check for modified fields
        for field, new_value in new_inputs.items():
            old_value = old_inputs.get(field)
            
            if old_value != new_value:
                change = {
                    "type": "modified",
                    "field": field,
                    "old_value": old_value,
                    "new_value": new_value,
                    "change_type": self._classify_change(field, old_value, new_value)
                }
                changes.append(change)
        
        # Check for removed fields
        for field, old_value in old_inputs.items():
            if field not in new_inputs:
                changes.append({
                    "type": "removed",
                    "field": field,
                    "old_value": old_value
                })
        
        # Check for added fields
        for field, new_value in new_inputs.items():
            if field not in old_inputs:
                changes.append({
                    "type": "added",
                    "field": field,
                    "new_value": new_value
                })
        
        return changes
    
    def _classify_change(self, field: str, old_value: Any, new_value: Any) -> str:
        """Classify the type of change"""
        try:
            old_num = float(old_value) if old_value is not None else 0
            new_num = float(new_value) if new_value is not None else 0
            
            if old_num == 0 and new_num != 0:
                return "initialized"
            elif old_num != 0 and new_num == 0:
                return "cleared"
            elif old_num < new_num:
                percent_change = ((new_num - old_num) / old_num) * 100
                if percent_change > 50:
                    return "major_increase"
                elif percent_change > 10:
                    return "moderate_increase"
                else:
                    return "minor_increase"
            elif old_num > new_num:
                percent_change = ((old_num - new_num) / old_num) * 100
                if percent_change > 50:
                    return "major_decrease"
                elif percent_change > 10:
                    return "moderate_decrease"
                else:
                    return "minor_decrease"
            else:
                return "no_change"
                
        except (ValueError, TypeError, ZeroDivisionError):
            return "text_change" if str(old_value) != str(new_value) else "no_change"
    
    def _compare_inputs(self, inputs1: Dict, inputs2: Dict) -> List[Dict]:
        """Compare inputs between two versions"""
        differences = []
        
        all_fields = set(inputs1.keys()) | set(inputs2.keys())
        
        for field in all_fields:
            value1 = inputs1.get(field)
            value2 = inputs2.get(field)
            
            if value1 != value2:
                diff = {
                    "field": field,
                    "field_label": field.replace('_', ' ').title(),
                    "value1": value1,
                    "value2": value2,
                    "change_type": self._classify_change(field, value1, value2),
                    "difference": self._calculate_difference(value1, value2)
                }
                differences.append(diff)
        
        return differences
    
    def _compare_results(self, results1: Dict, results2: Dict) -> List[Dict]:
        """Compare key results between two versions"""
        differences = []
        
        # Key metrics to compare
        key_metrics = {
            'roi_metrics.first_year_roi': 'First Year ROI',
            'roi_metrics.annual_savings': 'Annual Savings',
            'roi_metrics.payback_period_months': 'Payback Period (Months)',
            'financial_metrics.npv': 'Net Present Value',
            'financial_metrics.irr': 'Internal Rate of Return'
        }
        
        for metric_path, label in key_metrics.items():
            value1 = self._get_nested_value(results1, metric_path)
            value2 = self._get_nested_value(results2, metric_path)
            
            if value1 != value2:
                diff = {
                    "metric": metric_path,
                    "label": label,
                    "value1": value1,
                    "value2": value2,
                    "difference": self._calculate_difference(value1, value2),
                    "percent_change": self._calculate_percent_change(value1, value2)
                }
                differences.append(diff)
        
        return differences
    
    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """Get nested value from dictionary using dot notation"""
        try:
            keys = path.split('.')
            value = data
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return None
    
    def _calculate_difference(self, value1: Any, value2: Any) -> Optional[float]:
        """Calculate numerical difference between two values"""
        try:
            num1 = float(value1) if value1 is not None else 0
            num2 = float(value2) if value2 is not None else 0
            return num2 - num1
        except (ValueError, TypeError):
            return None
    
    def _calculate_percent_change(self, old_value: Any, new_value: Any) -> Optional[float]:
        """Calculate percent change between two values"""
        try:
            old_num = float(old_value) if old_value is not None else 0
            new_num = float(new_value) if new_value is not None else 0
            
            if old_num == 0:
                return None
            
            return ((new_num - old_num) / old_num) * 100
            
        except (ValueError, TypeError, ZeroDivisionError):
            return None
    
    def _generate_comparison_summary(self, v1: VersionEntry, v2: VersionEntry, 
                                   input_diff: List[Dict], results_diff: List[Dict]) -> str:
        """Generate human-readable comparison summary"""
        summary_parts = []
        
        # Version info
        time_diff = datetime.fromisoformat(v2.created_at) - datetime.fromisoformat(v1.created_at)
        days_diff = time_diff.days
        
        summary_parts.append(f"Comparing version {v1.version_number} to version {v2.version_number} ({days_diff} days apart)")
        
        # Input changes summary
        if input_diff:
            summary_parts.append(f"\nInput Changes ({len(input_diff)} fields modified):")
            for diff in input_diff[:5]:  # Show top 5 changes
                field_name = diff['field_label']
                change_type = diff['change_type']
                if change_type in ['major_increase', 'major_decrease']:
                    summary_parts.append(f"  • {field_name}: {change_type.replace('_', ' ')}")
        
        # Results impact summary
        if results_diff:
            summary_parts.append(f"\nResults Impact ({len(results_diff)} metrics changed):")
            for diff in results_diff:
                label = diff['label']
                percent_change = diff['percent_change']
                if percent_change and abs(percent_change) > 10:
                    direction = "increased" if percent_change > 0 else "decreased"
                    summary_parts.append(f"  • {label}: {direction} by {abs(percent_change):.1f}%")
        
        return '\n'.join(summary_parts)
    
    def _get_next_version_number(self, calculation_id: int) -> int:
        """Get the next version number for a calculation"""
        try:
            versions = self.get_version_history(calculation_id)
            if not versions:
                return 1
            
            max_version = max(v.version_number for v in versions)
            return max_version + 1
            
        except Exception:
            return 1
    
    def _generate_version_id(self, calculation_id: int, version_number: int) -> str:
        """Generate unique version ID"""
        timestamp = datetime.now().isoformat()
        data = f"{calculation_id}:{version_number}:{timestamp}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def _calculate_checksum(self, inputs: Dict, results: Dict) -> str:
        """Calculate checksum for version integrity"""
        data = json.dumps({"inputs": inputs, "results": results}, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _determine_action_type(self, version: VersionEntry) -> str:
        """Determine the type of action based on version data"""
        if "rollback" in version.created_by.lower():
            return "rollback"
        elif version.version_number == 1:
            return "created"
        elif "batch" in version.notes.lower():
            return "batch_update"
        else:
            return "modified"
    
    def _get_significant_changes(self, changes: List[Dict]) -> List[str]:
        """Extract significant changes for audit trail"""
        significant = []
        
        for change in changes:
            if change.get('change_type') in ['major_increase', 'major_decrease', 'initialized', 'cleared']:
                field_name = change.get('field', '').replace('_', ' ').title()
                change_type = change.get('change_type', '').replace('_', ' ')
                significant.append(f"{field_name}: {change_type}")
        
        return significant[:3]  # Limit to top 3 significant changes
    
    def export_version_history(self, calculation_id: int, format: str = 'json') -> str:
        """Export version history in specified format"""
        try:
            versions = self.get_version_history(calculation_id)
            
            if format.lower() == 'json':
                history_data = {
                    'calculation_id': calculation_id,
                    'total_versions': len(versions),
                    'exported_at': datetime.now().isoformat(),
                    'versions': [asdict(v) for v in versions]
                }
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"version_history_{calculation_id}_{timestamp}.json"
                
                with open(filename, 'w') as f:
                    json.dump(history_data, f, indent=2)
                
                return filename
            
            else:
                raise Exception(f"Unsupported export format: {format}")
                
        except Exception as e:
            raise Exception(f"Error exporting version history: {str(e)}")
    
    def validate_version_integrity(self, calculation_id: int) -> Dict:
        """Validate integrity of all versions for a calculation"""
        try:
            versions = self.get_version_history(calculation_id)
            validation_results = {
                'total_versions': len(versions),
                'valid_versions': 0,
                'invalid_versions': 0,
                'errors': []
            }
            
            for version in versions:
                # Verify checksum
                expected_checksum = self._calculate_checksum(version.inputs, version.results)
                
                if version.checksum == expected_checksum:
                    validation_results['valid_versions'] += 1
                else:
                    validation_results['invalid_versions'] += 1
                    validation_results['errors'].append({
                        'version': version.version_number,
                        'error': 'Checksum mismatch',
                        'expected': expected_checksum,
                        'actual': version.checksum
                    })
            
            validation_results['integrity_score'] = (
                validation_results['valid_versions'] / len(versions) * 100 
                if versions else 100
            )
            
            return validation_results
            
        except Exception as e:
            raise Exception(f"Error validating version integrity: {str(e)}")