"""Custom response utilities for consistent date formatting."""

from fastapi.responses import JSONResponse
from app.utils.json_encoder import CustomJSONEncoder


class CustomJSONResponse(JSONResponse):
    """JSONResponse with custom date formatting."""
    
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=CustomJSONEncoder,
        ).encode("utf-8")
