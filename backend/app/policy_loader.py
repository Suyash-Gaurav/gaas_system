import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from config.settings import get_settings

settings = get_settings()

class PolicyLoader:
    def __init__(self):
        self.policy_storage_path = Path(settings.policy_storage_path)
        self.policy_storage_path.mkdir(exist_ok=True)
        self._policies_cache: Dict[str, Dict[str, Any]] = {}
        self._load_all_policies()

    def _load_all_policies(self) -> None:
        """Load all policies from storage into memory cache."""
        try:
            for policy_file in self.policy_storage_path.glob("*.json"):
                with open(policy_file, 'r') as f:
                    policy_data = json.load(f)
                    policy_id = policy_data.get('policy_id')
                    if policy_id:
                        self._policies_cache[policy_id] = policy_data
        except Exception as e:
            print(f"Error loading policies: {e}")

    def load_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Load a specific policy by ID."""
        return self._policies_cache.get(policy_id)

    def save_policy(self, policy_data: Dict[str, Any]) -> bool:
        """Save a policy to storage."""
        try:
            policy_id = policy_data.get('policy_id')
            if not policy_id:
                return False

            # Validate policy structure
            if not self._validate_policy_structure(policy_data):
                return False

            # Save to file
            policy_file = self.policy_storage_path / f"{policy_id}.json"
            with open(policy_file, 'w') as f:
                json.dump(policy_data, f, indent=2, default=str)

            # Update cache
            self._policies_cache[policy_id] = policy_data
            return True
        except Exception as e:
            print(f"Error saving policy {policy_id}: {e}")
            return False

    def _validate_policy_structure(self, policy_data: Dict[str, Any]) -> bool:
        """Validate that policy has required structure."""
        required_fields = ['policy_id', 'policy_name', 'policy_type', 'policy_content', 'version']
        return all(field in policy_data for field in required_fields)

    def get_all_policies(self) -> Dict[str, Dict[str, Any]]:
        """Get all loaded policies."""
        return self._policies_cache.copy()

    def get_policies_by_type(self, policy_type: str) -> List[Dict[str, Any]]:
        """Get all policies of a specific type."""
        return [
            policy for policy in self._policies_cache.values()
            if policy.get('policy_type') == policy_type
        ]

    def is_policy_active(self, policy_id: str) -> bool:
        """Check if a policy is currently active."""
        policy = self.load_policy(policy_id)
        if not policy:
            return False

        now = datetime.now()
        effective_date = policy.get('effective_date')
        expiry_date = policy.get('expiry_date')

        if effective_date and isinstance(effective_date, str):
            effective_date = datetime.fromisoformat(effective_date.replace('Z', '+00:00'))
        if expiry_date and isinstance(expiry_date, str):
            expiry_date = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))

        if effective_date and now < effective_date:
            return False
        if expiry_date and now > expiry_date:
            return False

        return True

# Global policy loader instance
policy_loader = PolicyLoader()
