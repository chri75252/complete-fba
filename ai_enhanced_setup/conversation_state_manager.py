#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversation State Manager - Full Implementation

Manages conversation state persistence with resume capability.

Features:
- Save/load conversation state
- Detect incomplete sessions
- Resume from interruption
- Atomic writes for state files

Session 5 Implementation
"""

import json
import logging
import uuid
from pathlib import Path
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
import tempfile
import shutil

logger = logging.getLogger(__name__)


class ConversationStateManager:
    """
    Manages conversation state persistence and recovery.
    """
    
    def __init__(self, workspace_root: str = "."):
        """
        Initialize state manager.
        
        Args:
            workspace_root: Root directory of the workspace
        """
        self.workspace_root = Path(workspace_root)
        self.states_dir = self.workspace_root / "OUTPUTS" / "CACHE" / "conversation_states"
        self.states_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ConversationStateManager initialized: {self.states_dir}")
    
    def generate_session_id(self) -> str:
        """
        Generate unique session ID.
        
        Returns:
            Session ID string
        """
        return f"session_{uuid.uuid4().hex[:12]}"
    
    def save_state(self, session_id: str, state: Dict[str, Any]) -> None:
        """
        Save conversation state atomically.
        
        Args:
            session_id: Session identifier
            state: State dictionary to save
        """
        state_file = self.states_dir / f"{session_id}_state.json"
        
        # Add timestamp
        state["last_updated"] = datetime.now().isoformat()
        
        try:
            # Atomic write
            self._atomic_write_json(state_file, state)
            logger.debug(f"Saved state for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to save state for {session_id}: {e}")
            raise
    
    def load_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load conversation state.
        
        Args:
            session_id: Session identifier
            
        Returns:
            State dict or None if not found
        """
        state_file = self.states_dir / f"{session_id}_state.json"
        
        if not state_file.exists():
            logger.warning(f"State file not found: {state_file}")
            return None
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            logger.info(f"Loaded state for session: {session_id}")
            return state
        except Exception as e:
            logger.error(f"Failed to load state for {session_id}: {e}")
            return None
    
    def detect_incomplete_session(self, max_age_hours: int = 24) -> Optional[str]:
        """
        Detect most recent incomplete session.
        
        Args:
            max_age_hours: Maximum age for sessions to consider (hours)
            
        Returns:
            Session ID of most recent incomplete session, or None
        """
        if not self.states_dir.exists():
            return None
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        incomplete_sessions = []
        
        for state_file in self.states_dir.glob("session_*_state.json"):
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                # Check if incomplete
                if not state.get("complete", False):
                    # Check age
                    last_updated = datetime.fromisoformat(state.get("last_updated", ""))
                    if last_updated >= cutoff_time:
                        incomplete_sessions.append({
                            "session_id": state_file.stem.replace("_state", ""),
                            "last_updated": last_updated,
                            "collected_data": state.get("collected_data", {})
                        })
            except Exception as e:
                logger.warning(f"Failed to check state file {state_file}: {e}")
                continue
        
        if not incomplete_sessions:
            return None
        
        # Return most recent
        incomplete_sessions.sort(key=lambda x: x["last_updated"], reverse=True)
        most_recent = incomplete_sessions[0]
        
        logger.info(f"Found incomplete session: {most_recent['session_id']}")
        return most_recent["session_id"]
    
    def resume_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Resume incomplete session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Loaded state dict or None
        """
        state = self.load_state(session_id)
        
        if state:
            logger.info(f"Resuming session: {session_id}")
            print(f"\n📂 Resuming session from {state.get('last_updated')}")
            print(f"   Progress: {self._format_progress(state)}")
            print()
        
        return state
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete session state file.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted successfully
        """
        state_file = self.states_dir / f"{session_id}_state.json"
        
        try:
            if state_file.exists():
                state_file.unlink()
                logger.info(f"Deleted session: {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False
    
    def _format_progress(self, state: Dict[str, Any]) -> str:
        """Format progress summary for display."""
        collected = state.get("collected_data", {})
        parts = []
        
        if collected.get("supplier_domain"):
            parts.append(f"Domain: {collected['supplier_domain']}")
        
        categories = collected.get("categories", [])
        if categories:
            parts.append(f"{len(categories)} categories")
        
        if collected.get("field_mappings"):
            parts.append("Selectors collected")
        
        result: str = ", ".join(parts) if parts else "Just started"
        return result
    
    def _atomic_write_json(self, file_path: Path, data: Any) -> None:
        """
        Write JSON file atomically using temp file pattern.
        
        Args:
            file_path: Target file path
            data: Data to write
        """
        temp_fd, temp_path = tempfile.mkstemp(
            suffix='.json',
            dir=file_path.parent,
            text=True
        )
        
        try:
            with open(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Validate
            with open(temp_path, 'r', encoding='utf-8') as f:
                json.load(f)
            
            # Atomic move
            shutil.move(temp_path, str(file_path))
            
        except Exception as e:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except:
                pass
            raise RuntimeError(f"Atomic write failed for {file_path}: {e}")


if __name__ == "__main__":
    # Test implementation
    logging.basicConfig(level=logging.INFO)
    
    manager = ConversationStateManager()
    
    # Test session
    session_id = manager.generate_session_id()
    print(f"Generated session ID: {session_id}")
    
    # Save state
    test_state = {
        "collected_data": {
            "supplier_domain": "example.co.uk",
            "categories": [{"name": "Test", "url": "https://example.co.uk/test"}]
        },
        "conversation_history": [],
        "cost_tracker": 0.05,
        "complete": False
    }
    
    manager.save_state(session_id, test_state)
    print(f"✅ Saved test state")
    
    # Load state
    loaded = manager.load_state(session_id)
    print(f"✅ Loaded state: {loaded is not None}")
    
    # Detect incomplete
    incomplete = manager.detect_incomplete_session()
    print(f"✅ Detected incomplete session: {incomplete}")
    
    # Clean up
    manager.delete_session(session_id)
    print(f"✅ Cleaned up test session")
