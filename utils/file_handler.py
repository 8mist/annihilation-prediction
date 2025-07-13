import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any


class FileHandler:
    """Handles all file I/O operations with caching and error handling."""

    def __init__(self):
        self._cache = {}

    def load_json(self, filepath: Path, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """Load JSON with caching and error handling."""
        cache_key = str(filepath)

        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]

        if not filepath.exists():
            return None

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                if use_cache:
                    self._cache[cache_key] = data
                return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading {filepath}: {e}")
            return None

    def save_json(self, filepath: Path, data: Any) -> bool:
        """Save JSON with error handling and cache invalidation."""
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)

            cache_key = str(filepath)
            if cache_key in self._cache:
                del self._cache[cache_key]

            return True
        except IOError as e:
            print(f"Error saving {filepath}: {e}")
            return False

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
