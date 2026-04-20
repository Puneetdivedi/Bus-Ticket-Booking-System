"""Security scanning and vulnerability detection utilities."""
from typing import Any, Optional

from app.logger import get_logger
from app.sanitizers import InputValidator, Sanitizer

logger = get_logger(__name__)


class SecurityScanResult:
    """Result of a security scan."""
    
    def __init__(self, scan_type: str, severity: str = "INFO"):
        """Initialize scan result."""
        self.scan_type = scan_type
        self.severity = severity
        self.issues: list[dict[str, Any]] = []
    
    def add_issue(
        self,
        category: str,
        description: str,
        severity: str = "INFO",
        remediation: Optional[str] = None,
    ) -> None:
        """Add a security issue."""
        self.issues.append({
            "category": category,
            "description": description,
            "severity": severity,
            "remediation": remediation,
        })
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scan_type": self.scan_type,
            "issues_found": len(self.issues),
            "severity": self.severity,
            "issues": self.issues,
        }


class SecurityScanner:
    """Scan for common security vulnerabilities."""
    
    @staticmethod
    def scan_input_injection(input_string: str) -> SecurityScanResult:
        """Scan for injection vulnerabilities."""
        result = SecurityScanResult("input_injection")
        
        # Check for SQL injection patterns
        sql_patterns = ["' OR ", "'; DROP", "UNION SELECT", "--", "/*", "*/"]
        for pattern in sql_patterns:
            if pattern.lower() in input_string.lower():
                result.add_issue(
                    "SQL Injection",
                    f"Potential SQL injection detected: {pattern}",
                    severity="CRITICAL",
                    remediation="Use parameterized queries and input validation",
                )
        
        # Check for script injection
        script_patterns = ["<script>", "javascript:", "onerror=", "onclick="]
        for pattern in script_patterns:
            if pattern.lower() in input_string.lower():
                result.add_issue(
                    "XSS Injection",
                    f"Potential XSS detected: {pattern}",
                    severity="HIGH",
                    remediation="Escape and validate all user inputs",
                )
        
        return result
    
    @staticmethod
    def scan_password_strength(password: str) -> SecurityScanResult:
        """Scan password for strength issues."""
        result = SecurityScanResult("password_strength")
        
        if len(password) < 12:
            result.add_issue(
                "Weak Length",
                f"Password too short: {len(password)} characters",
                severity="HIGH",
                remediation="Use at least 12 characters",
            )
        
        if not any(c.isupper() for c in password):
            result.add_issue(
                "No Uppercase",
                "Password missing uppercase letters",
                severity="MEDIUM",
            )
        
        if not any(c.isdigit() for c in password):
            result.add_issue(
                "No Numbers",
                "Password missing numeric characters",
                severity="MEDIUM",
            )
        
        if not any(c in "!@#$%^&*" for c in password):
            result.add_issue(
                "No Symbols",
                "Password missing special characters",
                severity="MEDIUM",
            )
        
        return result
    
    @staticmethod
    def scan_api_endpoint(method: str, path: str, params: dict) -> SecurityScanResult:
        """Scan API endpoint for security issues."""
        result = SecurityScanResult("api_endpoint")
        
        # Check for exposed sensitive data in path
        sensitive_keywords = ["password", "token", "secret", "key", "admin"]
        if any(keyword in path.lower() for keyword in sensitive_keywords):
            result.add_issue(
                "Exposed Sensitive Data",
                f"Path contains sensitive keyword: {path}",
                severity="MEDIUM",
                remediation="Avoid exposing sensitive terms in API paths",
            )
        
        # Check for unencrypted communication
        if method in ["POST", "PUT"] and not path.startswith("https"):
            result.add_issue(
                "Unencrypted Communication",
                "Sensitive data transmitted without HTTPS",
                severity="HIGH",
                remediation="Use HTTPS for all API endpoints",
            )
        
        # Scan parameters for injection
        for param_name, param_value in params.items():
            if isinstance(param_value, str):
                injection_scan = SecurityScanner.scan_input_injection(param_value)
                for issue in injection_scan.issues:
                    result.add_issue(
                        issue["category"],
                        f"Parameter '{param_name}': {issue['description']}",
                        severity=issue["severity"],
                    )
        
        return result
    
    @staticmethod
    def scan_configuration(config: dict[str, Any]) -> SecurityScanResult:
        """Scan configuration for security issues."""
        result = SecurityScanResult("configuration")
        
        # Check debug mode in production
        if config.get("DEBUG") and config.get("ENVIRONMENT") == "production":
            result.add_issue(
                "Debug Mode",
                "DEBUG enabled in production",
                severity="CRITICAL",
                remediation="Disable DEBUG in production environment",
            )
        
        # Check for default credentials
        if config.get("API_KEY") == "your-secret-key":
            result.add_issue(
                "Default Credentials",
                "Using default API key",
                severity="CRITICAL",
                remediation="Change to a secure random key",
            )
        
        # Check CORS configuration
        cors_origins = config.get("CORS_ORIGINS", [])
        if "*" in cors_origins:
            result.add_issue(
                "Open CORS",
                "CORS allows all origins",
                severity="MEDIUM",
                remediation="Restrict CORS to specific trusted origins",
            )
        
        # Check SSL/TLS settings
        if not config.get("SSL_ENABLED"):
            result.add_issue(
                "No SSL/TLS",
                "SSL/TLS not enabled",
                severity="CRITICAL",
                remediation="Enable HTTPS with valid SSL certificates",
            )
        
        return result


def scan_input_for_threats(input_string: str) -> dict[str, Any]:
    """Scan input string for security threats."""
    scanner = SecurityScanner()
    result = scanner.scan_input_injection(input_string)
    
    if result.issues:
        logger.warning(
            f"Security threats detected in input: {len(result.issues)} issues"
        )
    
    return result.to_dict()
