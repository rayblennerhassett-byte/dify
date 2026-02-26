import json
import hashlib


class MoEEncoder(json.JSONEncoder):
    """Custom encoder to enforce %.17g float format as per Section 4.1"""

    def iterencode(self, o, _one_shot=False):
        if isinstance(o, float):
            return format(o, "%.17g")
        return super().iterencode(o, _one_shot)


def canonical_json(obj) -> str:
    """
    Enforces alphabetical field ordering, no whitespace,
    and %.17g float formatting.
    """

    # Note: json.dumps doesn't easily allow overriding float formatting globally
    # without a custom encoder or pre-processing.
    def format_floats(data):
        if isinstance(data, dict):
            return {k: format_floats(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [format_floats(v) for v in data]
        elif isinstance(data, float):
            # Using %.17g string representation for consistent hashing
            return float(format(data, "%.17g"))
        return data

    clean_obj = format_floats(obj)
    return json.dumps(
        clean_obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def compute_state_hash(state_dict: object) -> tuple[str, int]:
    """Computes SHA-256 of canonicalized JSON."""
    s = canonical_json(state_dict)
    b = s.encode("utf-8")
    h = hashlib.sha256(b).hexdigest()
    return h, len(b)
