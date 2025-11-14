from datetime import datetime

def to_iso(dt) -> str:
    if hasattr(dt, "isoformat"):
        return dt.isoformat()
    return str(dt)