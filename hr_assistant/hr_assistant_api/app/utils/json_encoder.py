"""Custom JSON encoder to handle date formatting consistently."""

import json
from datetime import date, datetime
from typing import Any


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that formats dates consistently."""
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, date):
            # Format date as MM/DD/YYYY without timezone conversion
            return f"{obj.month:02d}/{obj.day:02d}/{obj.year}"
        elif isinstance(obj, datetime):
            # Format datetime as ISO string
            return obj.isoformat()
        return super().default(obj)
