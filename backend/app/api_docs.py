"""API documentation and schema generation utilities."""
from datetime import datetime
from typing import Any, dict, list, Optional

from app.logger import get_logger

logger = get_logger(__name__)


class APIDocGenerator:
    """Generate API documentation automatically."""
    
    def __init__(self):
        """Initialize API doc generator."""
        self.endpoints: list[dict[str, Any]] = []
        self.generated_at = datetime.utcnow()
    
    def register_endpoint(
        self,
        method: str,
        path: str,
        summary: str,
        description: str = "",
        tags: Optional[list[str]] = None,
        request_schema: Optional[dict[str, Any]] = None,
        response_schema: Optional[dict[str, Any]] = None,
        status_codes: Optional[dict[int, str]] = None,
        example_request: Optional[dict[str, Any]] = None,
        example_response: Optional[dict[str, Any]] = None,
    ) -> None:
        """Register an API endpoint for documentation."""
        endpoint = {
            "method": method,
            "path": path,
            "summary": summary,
            "description": description,
            "tags": tags or [],
            "request_schema": request_schema,
            "response_schema": response_schema,
            "status_codes": status_codes or {200: "Success"},
            "example_request": example_request,
            "example_response": example_response,
            "registered_at": datetime.utcnow().isoformat(),
        }
        self.endpoints.append(endpoint)
        logger.info(f"Endpoint registered: {method} {path}")
    
    def get_markdown_doc(self) -> str:
        """Generate Markdown documentation."""
        doc = "# API Documentation\n\n"
        doc += f"Generated: {self.generated_at.isoformat()}\n"
        doc += f"Total Endpoints: {len(self.endpoints)}\n\n"
        
        # Group by tag
        by_tag: dict[str, list] = {}
        for endpoint in self.endpoints:
            for tag in endpoint["tags"] or ["Other"]:
                if tag not in by_tag:
                    by_tag[tag] = []
                by_tag[tag].append(endpoint)
        
        # Generate documentation by tag
        for tag in sorted(by_tag.keys()):
            doc += f"## {tag}\n\n"
            for endpoint in by_tag[tag]:
                doc += self._endpoint_to_markdown(endpoint)
                doc += "\n---\n\n"
        
        return doc
    
    def _endpoint_to_markdown(self, endpoint: dict[str, Any]) -> str:
        """Convert endpoint to Markdown."""
        doc = f"### {endpoint['method']} {endpoint['path']}\n\n"
        doc += f"**Summary:** {endpoint['summary']}\n\n"
        
        if endpoint['description']:
            doc += f"**Description:** {endpoint['description']}\n\n"
        
        if endpoint['request_schema']:
            doc += "**Request Schema:**\n```json\n"
            doc += str(endpoint['request_schema']).replace("'", '"') + "\n```\n\n"
        
        if endpoint['response_schema']:
            doc += "**Response Schema:**\n```json\n"
            doc += str(endpoint['response_schema']).replace("'", '"') + "\n```\n\n"
        
        if endpoint['status_codes']:
            doc += "**Status Codes:**\n"
            for code, message in endpoint['status_codes'].items():
                doc += f"- `{code}` - {message}\n"
            doc += "\n"
        
        if endpoint['example_request']:
            doc += "**Example Request:**\n```json\n"
            doc += str(endpoint['example_request']).replace("'", '"') + "\n```\n\n"
        
        if endpoint['example_response']:
            doc += "**Example Response:**\n```json\n"
            doc += str(endpoint['example_response']).replace("'", '"') + "\n```\n\n"
        
        return doc
    
    def get_openapi_schema(self) -> dict[str, Any]:
        """Generate OpenAPI 3.0 schema."""
        schema = {
            "openapi": "3.0.0",
            "info": {
                "title": "Bus Ticket Booking System API",
                "version": "1.1.4",
                "description": "Production-ready API for bus ticket booking",
            },
            "servers": [
                {"url": "http://localhost:8000", "description": "Development"},
                {"url": "https://api.example.com", "description": "Production"},
            ],
            "paths": {},
        }
        
        for endpoint in self.endpoints:
            path = endpoint["path"]
            method = endpoint["method"].lower()
            
            if path not in schema["paths"]:
                schema["paths"][path] = {}
            
            schema["paths"][path][method] = {
                "summary": endpoint["summary"],
                "description": endpoint["description"],
                "tags": endpoint["tags"],
                "responses": {
                    str(code): {"description": msg}
                    for code, msg in endpoint["status_codes"].items()
                },
            }
        
        return schema
    
    def export_to_file(self, filename: str, format: str = "markdown") -> bool:
        """Export documentation to file."""
        try:
            if format == "markdown":
                content = self.get_markdown_doc()
            elif format == "openapi":
                import json
                content = json.dumps(self.get_openapi_schema(), indent=2)
            else:
                logger.error(f"Unknown format: {format}")
                return False
            
            with open(filename, "w") as f:
                f.write(content)
            
            logger.info(f"Documentation exported to {filename}")
            return True
        
        except Exception as exc:
            logger.error(f"Export failed: {exc}")
            return False


# Global documentation generator
doc_generator = APIDocGenerator()


def get_doc_generator() -> APIDocGenerator:
    """Get global API documentation generator."""
    return doc_generator
