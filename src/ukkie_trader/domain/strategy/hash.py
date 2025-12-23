import json
import hashlib
from typing import Any, Dict

def compute_definition_hash(definition: Dict[str, Any]) -> str:
    """
    Computes a deterministic SHA256 hash for a strategy definition.
    
    Rules:
    - Keys are sorted alphabetically.
    - None values are converted to "null" string.
    - Floats are rounded to 8 decimal places.
    - Nested dicts are recursively processed.
    """
    def canonicalize(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: canonicalize(v) for k, v in sorted(obj.items())}
        elif isinstance(obj, list):
            return [canonicalize(x) for x in obj]
        elif isinstance(obj, float):
            return round(obj, 8)
        elif obj is None:
            return "null"
        elif hasattr(obj, "dict"): # Pydantic model
            return canonicalize(obj.dict())
        return obj

    canonical_json = json.dumps(
        canonicalize(definition),
        sort_keys=True,
        separators=(',', ':')
    )
    
    return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
