"""
Session Manager for Streamlit Dashboard
======================================
Handles session state management, data persistence, and cross-page communication.
"""

import streamlit as st
import json
import datetime
from typing import Dict, Any, Optional
import uuid


class SessionManager:
    """Manages session state and data persistence across Streamlit pages"""
    
    def __init__(self):
        """Initialize session manager"""
        self.session_id = self._get_or_create_session_id()
        self._initialize_session_state()
    
    def _get_or_create_session_id(self) -> str:
        """Get existing session ID or create a new one"""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        return st.session_state.session_id
    
    def _initialize_session_state(self):
        """Initialize default session state variables"""
        defaults = {
            'user_data': {},
            'roi_data': {},
            'assessment_data': {},
            'proposal_data': {},
            'calculations': {},
            'session_created': datetime.datetime.now().isoformat(),
            'last_updated': datetime.datetime.now().isoformat(),
            'page_history': [],
            'form_states': {},
            'export_history': []
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def save_data(self, key: str, data: Any, update_timestamp: bool = True):
        """
        Save data to session state
        
        Args:
            key: The key to store data under
            data: The data to store
            update_timestamp: Whether to update the last_updated timestamp
        """
        try:
            st.session_state[key] = data
            
            if update_timestamp:
                st.session_state.last_updated = datetime.datetime.now().isoformat()
            
            # Track page if not already tracked
            current_page = getattr(st.session_state, 'current_page', 'unknown')
            if current_page not in st.session_state.page_history:
                st.session_state.page_history.append(current_page)
                
        except Exception as e:
            st.error(f"Error saving data: {str(e)}")
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """
        Retrieve data from session state
        
        Args:
            key: The key to retrieve data for
            default: Default value if key doesn't exist
            
        Returns:
            The stored data or default value
        """
        return st.session_state.get(key, default)
    
    def update_roi_data(self, roi_data: Dict[str, Any]):
        """Update ROI calculation data"""
        current_roi = st.session_state.get('roi_data', {})
        current_roi.update(roi_data)
        self.save_data('roi_data', current_roi)
    
    def get_roi_data(self) -> Dict[str, Any]:
        """Get ROI calculation data"""
        return self.get_data('roi_data', {})
    
    def update_assessment_data(self, assessment_data: Dict[str, Any]):
        """Update assessment tool data"""
        current_assessment = st.session_state.get('assessment_data', {})
        current_assessment.update(assessment_data)
        self.save_data('assessment_data', current_assessment)
    
    def get_assessment_data(self) -> Dict[str, Any]:
        """Get assessment tool data"""
        return self.get_data('assessment_data', {})
    
    def update_proposal_data(self, proposal_data: Dict[str, Any]):
        """Update proposal generator data"""
        current_proposal = st.session_state.get('proposal_data', {})
        current_proposal.update(proposal_data)
        self.save_data('proposal_data', current_proposal)
    
    def get_proposal_data(self) -> Dict[str, Any]:
        """Get proposal generator data"""
        return self.get_data('proposal_data', {})
    
    def save_form_state(self, form_name: str, form_data: Dict[str, Any]):
        """Save form state for later restoration"""
        form_states = st.session_state.get('form_states', {})
        form_states[form_name] = {
            'data': form_data,
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.save_data('form_states', form_states)
    
    def get_form_state(self, form_name: str) -> Optional[Dict[str, Any]]:
        """Get saved form state"""
        form_states = st.session_state.get('form_states', {})
        form_state = form_states.get(form_name)
        return form_state['data'] if form_state else None
    
    def clear_form_state(self, form_name: str):
        """Clear specific form state"""
        form_states = st.session_state.get('form_states', {})
        if form_name in form_states:
            del form_states[form_name]
            self.save_data('form_states', form_states)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session"""
        roi_data = self.get_roi_data()
        assessment_data = self.get_assessment_data()
        proposal_data = self.get_proposal_data()
        
        return {
            'session_id': self.session_id,
            'created': st.session_state.get('session_created'),
            'last_updated': st.session_state.get('last_updated'),
            'pages_visited': st.session_state.get('page_history', []),
            'has_roi_data': bool(roi_data),
            'has_assessment_data': bool(assessment_data),
            'has_proposal_data': bool(proposal_data),
            'total_calculations': len(st.session_state.get('calculations', {})),
            'export_count': len(st.session_state.get('export_history', []))
        }
    
    def export_session_data(self) -> Dict[str, Any]:
        """Export all session data for backup or analysis"""
        return {
            'session_info': {
                'session_id': self.session_id,
                'created': st.session_state.get('session_created'),
                'last_updated': st.session_state.get('last_updated'),
                'pages_visited': st.session_state.get('page_history', [])
            },
            'roi_data': self.get_roi_data(),
            'assessment_data': self.get_assessment_data(),
            'proposal_data': self.get_proposal_data(),
            'calculations': st.session_state.get('calculations', {}),
            'form_states': st.session_state.get('form_states', {}),
            'export_history': st.session_state.get('export_history', [])
        }
    
    def import_session_data(self, session_data: Dict[str, Any]):
        """Import session data from backup"""
        try:
            # Validate data structure
            required_keys = ['session_info', 'roi_data', 'assessment_data', 'proposal_data']
            if not all(key in session_data for key in required_keys):
                raise ValueError("Invalid session data structure")
            
            # Import data
            self.save_data('roi_data', session_data['roi_data'], False)
            self.save_data('assessment_data', session_data['assessment_data'], False)
            self.save_data('proposal_data', session_data['proposal_data'], False)
            self.save_data('calculations', session_data.get('calculations', {}), False)
            self.save_data('form_states', session_data.get('form_states', {}), False)
            self.save_data('export_history', session_data.get('export_history', []), False)
            
            # Update timestamp
            st.session_state.last_updated = datetime.datetime.now().isoformat()
            
            return True
            
        except Exception as e:
            st.error(f"Error importing session data: {str(e)}")
            return False
    
    def clear_session(self, keep_session_info: bool = False):
        """Clear all session data"""
        keys_to_clear = [
            'user_data', 'roi_data', 'assessment_data', 'proposal_data',
            'calculations', 'form_states', 'export_history'
        ]
        
        if not keep_session_info:
            keys_to_clear.extend(['page_history'])
        
        for key in keys_to_clear:
            if key in st.session_state:
                if isinstance(st.session_state[key], dict):
                    st.session_state[key] = {}
                elif isinstance(st.session_state[key], list):
                    st.session_state[key] = []
                else:
                    del st.session_state[key]
        
        # Reset timestamps
        st.session_state.session_created = datetime.datetime.now().isoformat()
        st.session_state.last_updated = datetime.datetime.now().isoformat()
    
    def get_session_data(self) -> Dict[str, Any]:
        """Get all relevant session data for display"""
        return {
            'roi_data': self.get_roi_data(),
            'assessment_data': self.get_assessment_data(),
            'proposal_data': self.get_proposal_data(),
            'calculations': st.session_state.get('calculations', {}),
            'summary': self.get_session_summary()
        }
    
    def log_export(self, export_type: str, filename: str, success: bool = True):
        """Log export activity"""
        export_history = st.session_state.get('export_history', [])
        export_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'type': export_type,
            'filename': filename,
            'success': success,
            'session_id': self.session_id
        }
        export_history.append(export_entry)
        self.save_data('export_history', export_history)
    
    def get_export_history(self) -> list:
        """Get export history"""
        return st.session_state.get('export_history', [])
    
    def validate_data_integrity(self) -> Dict[str, bool]:
        """Validate data integrity across modules"""
        results = {
            'roi_data_valid': self._validate_roi_data(),
            'assessment_data_valid': self._validate_assessment_data(),
            'proposal_data_valid': self._validate_proposal_data(),
            'session_consistent': self._validate_session_consistency()
        }
        return results
    
    def _validate_roi_data(self) -> bool:
        """Validate ROI data structure"""
        roi_data = self.get_roi_data()
        if not roi_data:
            return True  # Empty is valid
        
        required_fields = ['monthly_revenue', 'monthly_costs', 'implementation_cost']
        return all(isinstance(roi_data.get(field), (int, float)) for field in required_fields if field in roi_data)
    
    def _validate_assessment_data(self) -> bool:
        """Validate assessment data structure"""
        assessment_data = self.get_assessment_data()
        if not assessment_data:
            return True  # Empty is valid
        
        # Check if responses are valid
        responses = assessment_data.get('responses', {})
        return all(isinstance(v, (str, int, float, bool)) for v in responses.values())
    
    def _validate_proposal_data(self) -> bool:
        """Validate proposal data structure"""
        proposal_data = self.get_proposal_data()
        if not proposal_data:
            return True  # Empty is valid
        
        # Check basic structure
        return isinstance(proposal_data.get('client_info', {}), dict)
    
    def _validate_session_consistency(self) -> bool:
        """Validate session consistency"""
        try:
            # Check timestamps
            created = st.session_state.get('session_created')
            updated = st.session_state.get('last_updated')
            
            if created and updated:
                created_dt = datetime.datetime.fromisoformat(created)
                updated_dt = datetime.datetime.fromisoformat(updated)
                return created_dt <= updated_dt
            
            return True
        except Exception:
            return False