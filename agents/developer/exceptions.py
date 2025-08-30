"""Custom exceptions for the Developer Agent.

This module defines specific exceptions for developer operations,
providing detailed context for error handling and debugging.
"""

from typing import List, Optional, Dict, Any


class DeveloperError(Exception):
    """Base exception for Developer Agent errors."""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Initialize with message and optional context.
        
        Args:
            message: Human-readable error description
            context: Additional context information
        """
        super().__init__(message)
        self.context = context or {}


class CodeGenerationError(DeveloperError):
    """Exception raised when code generation fails."""
    
    def __init__(
        self,
        message: str,
        language: Optional[str] = None,
        requirements: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """Initialize code generation error.
        
        Args:
            message: Error description
            language: Programming language being generated
            requirements: Requirements that couldn't be satisfied
            context: Additional context
        """
        super().__init__(message, context)
        self.language = language
        self.requirements = requirements or []
        
    def get_diagnostic_info(self) -> Dict[str, Any]:
        """Get diagnostic information for debugging."""
        return {
            "error_type": "CodeGenerationError",
            "language": self.language,
            "requirements_count": len(self.requirements),
            "requirements": self.requirements[:3],  # First 3 for brevity
            "context": self.context
        }


class SyntaxValidationError(DeveloperError):
    """Exception raised when generated code has syntax errors."""
    
    def __init__(
        self,
        message: str,
        file_path: str,
        syntax_errors: List[str],
        language: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """Initialize syntax validation error.
        
        Args:
            message: Error description
            file_path: Path to file with syntax errors
            syntax_errors: List of syntax error descriptions
            language: Programming language
            context: Additional context
        """
        super().__init__(message, context)
        self.file_path = file_path
        self.syntax_errors = syntax_errors
        self.language = language
        
    def get_diagnostic_info(self) -> Dict[str, Any]:
        """Get diagnostic information for debugging."""
        return {
            "error_type": "SyntaxValidationError",
            "file_path": self.file_path,
            "language": self.language,
            "syntax_error_count": len(self.syntax_errors),
            "syntax_errors": self.syntax_errors,
            "context": self.context
        }


class FileOperationError(DeveloperError):
    """Exception raised when file operations fail."""
    
    def __init__(
        self,
        message: str,
        operation: str,
        file_path: str,
        underlying_error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """Initialize file operation error.
        
        Args:
            message: Error description
            operation: Operation that failed (read, write, create, etc.)
            file_path: Path to file involved in operation
            underlying_error: The underlying exception that caused this
            context: Additional context
        """
        super().__init__(message, context)
        self.operation = operation
        self.file_path = file_path
        self.underlying_error = underlying_error
        
    def get_diagnostic_info(self) -> Dict[str, Any]:
        """Get diagnostic information for debugging."""
        return {
            "error_type": "FileOperationError",
            "operation": self.operation,
            "file_path": self.file_path,
            "underlying_error": str(self.underlying_error) if self.underlying_error else None,
            "context": self.context
        }


class DisasterPreventionError(DeveloperError):
    """Exception raised when disaster prevention checks fail.
    
    This is thrown when the agent detects that it might be about to
    perform a dangerous operation like PR #23 (deleting entire files
    when only small changes were requested).
    """
    
    def __init__(
        self,
        message: str,
        dangerous_operation: str,
        file_path: str,
        prevention_check: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Initialize disaster prevention error.
        
        Args:
            message: Error description
            dangerous_operation: The dangerous operation that was detected
            file_path: File that would be affected
            prevention_check: Which prevention check failed
            context: Additional context
        """
        super().__init__(message, context)
        self.dangerous_operation = dangerous_operation
        self.file_path = file_path
        self.prevention_check = prevention_check
        
    def get_diagnostic_info(self) -> Dict[str, Any]:
        """Get diagnostic information for debugging."""
        return {
            "error_type": "DisasterPreventionError",
            "dangerous_operation": self.dangerous_operation,
            "file_path": self.file_path,
            "prevention_check": self.prevention_check,
            "context": self.context
        }


class RequirementsInsufficientError(DeveloperError):
    """Exception raised when requirements are insufficient for implementation."""
    
    def __init__(
        self,
        message: str,
        missing_requirements: List[str],
        available_requirements: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """Initialize requirements insufficient error.
        
        Args:
            message: Error description
            missing_requirements: List of missing requirement types/areas
            available_requirements: Requirements that were available
            context: Additional context
        """
        super().__init__(message, context)
        self.missing_requirements = missing_requirements
        self.available_requirements = available_requirements or []
        
    def get_diagnostic_info(self) -> Dict[str, Any]:
        """Get diagnostic information for debugging."""
        return {
            "error_type": "RequirementsInsufficientError",
            "missing_requirements": self.missing_requirements,
            "available_requirements_count": len(self.available_requirements),
            "context": self.context
        }


class GitHubIntegrationError(DeveloperError):
    """Exception raised when GitHub integration fails."""
    
    def __init__(
        self,
        message: str,
        operation: str,
        repository: Optional[str] = None,
        underlying_error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """Initialize GitHub integration error.
        
        Args:
            message: Error description
            operation: GitHub operation that failed
            repository: Repository identifier
            underlying_error: The underlying exception
            context: Additional context
        """
        super().__init__(message, context)
        self.operation = operation
        self.repository = repository
        self.underlying_error = underlying_error
        
    def get_diagnostic_info(self) -> Dict[str, Any]:
        """Get diagnostic information for debugging."""
        return {
            "error_type": "GitHubIntegrationError",
            "operation": self.operation,
            "repository": self.repository,
            "underlying_error": str(self.underlying_error) if self.underlying_error else None,
            "context": self.context
        }


class ImplementationTimeoutError(DeveloperError):
    """Exception raised when implementation takes too long."""
    
    def __init__(
        self,
        message: str,
        timeout_seconds: int,
        elapsed_seconds: float,
        context: Optional[Dict[str, Any]] = None
    ):
        """Initialize implementation timeout error.
        
        Args:
            message: Error description
            timeout_seconds: Timeout limit in seconds
            elapsed_seconds: Actual elapsed time
            context: Additional context
        """
        super().__init__(message, context)
        self.timeout_seconds = timeout_seconds
        self.elapsed_seconds = elapsed_seconds
        
    def get_diagnostic_info(self) -> Dict[str, Any]:
        """Get diagnostic information for debugging."""
        return {
            "error_type": "ImplementationTimeoutError",
            "timeout_seconds": self.timeout_seconds,
            "elapsed_seconds": self.elapsed_seconds,
            "context": self.context
        }


class ArtifactValidationError(DeveloperError):
    """Exception raised when artifact validation fails."""
    
    def __init__(
        self,
        message: str,
        artifact_path: str,
        validation_errors: List[str],
        context: Optional[Dict[str, Any]] = None
    ):
        """Initialize artifact validation error.
        
        Args:
            message: Error description
            artifact_path: Path to artifact that failed validation
            validation_errors: List of specific validation errors
            context: Additional context
        """
        super().__init__(message, context)
        self.artifact_path = artifact_path
        self.validation_errors = validation_errors
        
    def get_diagnostic_info(self) -> Dict[str, Any]:
        """Get diagnostic information for debugging."""
        return {
            "error_type": "ArtifactValidationError",
            "artifact_path": self.artifact_path,
            "validation_error_count": len(self.validation_errors),
            "validation_errors": self.validation_errors,
            "context": self.context
        }


# Validation and utility functions

def validate_developer_context(context: Dict[str, Any]) -> None:
    """Validate that developer context contains required fields.
    
    Args:
        context: Context dictionary to validate
        
    Raises:
        DeveloperError: If context is invalid
    """
    required_fields = ["task", "repository"]
    
    for field in required_fields:
        if field not in context:
            raise DeveloperError(f"Missing required context field: {field}")
        
        if not context[field]:
            raise DeveloperError(f"Empty required context field: {field}")


def validate_file_path_safety(file_path: str) -> None:
    """Validate that a file path is safe for operations.
    
    Args:
        file_path: Path to validate
        
    Raises:
        DisasterPreventionError: If path is potentially dangerous
    """
    if not file_path or not file_path.strip():
        raise DisasterPreventionError(
            "Empty file path detected",
            dangerous_operation="file_operation_on_empty_path",
            file_path="",
            prevention_check="path_not_empty"
        )
    
    # Check for dangerous path patterns
    dangerous_patterns = ["../", "..\\", "/etc/", "/root/", "/home/"]
    normalized_path = file_path.lower().replace("\\", "/")
    
    for pattern in dangerous_patterns:
        if pattern in normalized_path:
            raise DisasterPreventionError(
                f"Dangerous path pattern detected: {pattern}",
                dangerous_operation=f"access_dangerous_path_{pattern}",
                file_path=file_path,
                prevention_check="no_dangerous_path_patterns"
            )
    
    # Check for system files
    system_files = [
        "passwd", "shadow", "hosts", "fstab", 
        ".ssh/", ".aws/", ".env", ".secrets"
    ]
    
    for system_file in system_files:
        if system_file in normalized_path:
            raise DisasterPreventionError(
                f"System file access detected: {system_file}",
                dangerous_operation=f"access_system_file_{system_file}",
                file_path=file_path,
                prevention_check="no_system_file_access"
            )


def validate_code_modification_safety(
    file_path: str,
    original_content: str,
    new_content: str,
    intended_change: str
) -> None:
    """Validate that a code modification is safe (prevents PR #23 disasters).
    
    Args:
        file_path: Path to file being modified
        original_content: Original file content
        new_content: New file content
        intended_change: Description of intended change
        
    Raises:
        DisasterPreventionError: If modification appears dangerous
    """
    # Check if entire file is being deleted when only small change intended
    if len(original_content) > 100 and len(new_content) < 50:
        if "delete" not in intended_change.lower() and "remove file" not in intended_change.lower():
            raise DisasterPreventionError(
                "Detected potential file deletion when only modification intended",
                dangerous_operation="complete_file_deletion",
                file_path=file_path,
                prevention_check="preserve_substantial_content",
                context={
                    "original_length": len(original_content),
                    "new_length": len(new_content),
                    "intended_change": intended_change
                }
            )
    
    # Check if we're removing important sections accidentally
    important_markers = [
        "# README", "## ", "### ", "LICENSE", "Copyright",
        "class ", "def ", "function ", "import ", "package.json"
    ]
    
    removed_markers = []
    for marker in important_markers:
        if marker in original_content and marker not in new_content:
            removed_markers.append(marker)
    
    if len(removed_markers) > 3:  # Too many important things removed
        if "remove" not in intended_change.lower() and "delete" not in intended_change.lower():
            raise DisasterPreventionError(
                f"Detected removal of important content: {', '.join(removed_markers)}",
                dangerous_operation="remove_important_content",
                file_path=file_path,
                prevention_check="preserve_important_markers",
                context={
                    "removed_markers": removed_markers,
                    "intended_change": intended_change
                }
            )


def assess_implementation_risk(
    artifacts: List[Dict[str, Any]],
    modifications: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Assess the risk level of an implementation.
    
    Args:
        artifacts: List of artifacts being created
        modifications: List of file modifications
        
    Returns:
        Risk assessment with score and details
    """
    risk_score = 0
    risk_factors = []
    
    # Count files being modified vs created
    files_created = sum(1 for art in artifacts if art.get("modification_type") == "create")
    files_modified = sum(1 for art in artifacts if art.get("modification_type") == "update")
    files_deleted = sum(1 for art in artifacts if art.get("modification_type") == "delete")
    
    # Risk factors
    if files_deleted > 0:
        risk_score += files_deleted * 30
        risk_factors.append(f"Deleting {files_deleted} files")
    
    if files_modified > 5:
        risk_score += (files_modified - 5) * 10
        risk_factors.append(f"Modifying {files_modified} files")
    
    if files_created > 10:
        risk_score += (files_created - 10) * 5
        risk_factors.append(f"Creating {files_created} files")
    
    # Check for critical file modifications
    critical_files = ["README.md", "package.json", "requirements.txt", "setup.py", ".gitignore"]
    for mod in modifications:
        file_path = mod.get("file_path", "")
        filename = file_path.split("/")[-1]
        if filename in critical_files and mod.get("modification_type") == "update":
            risk_score += 20
            risk_factors.append(f"Modifying critical file: {filename}")
    
    # Determine risk level
    if risk_score >= 100:
        risk_level = "very_high"
    elif risk_score >= 60:
        risk_level = "high"
    elif risk_score >= 30:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "files_created": files_created,
        "files_modified": files_modified,
        "files_deleted": files_deleted
    }