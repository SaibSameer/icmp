import pytest
from backend.error_handling import (
    ICMPError, ValidationError, AuthenticationError,
    AuthorizationError, NotFoundError, DatabaseError,
    ServiceError
)

def test_icmp_error():
    """Test ICMPError creation and properties."""
    error = ICMPError(
        message="Test error",
        code="TEST_ERROR",
        details={"field": "value"}
    )
    
    assert error.message == "Test error"
    assert error.code == "TEST_ERROR"
    assert error.details["field"] == "value"
    assert error.status_code == 500
    
    # Test error serialization
    error_dict = error.to_dict()
    assert error_dict["message"] == "Test error"
    assert error_dict["code"] == "TEST_ERROR"
    assert error_dict["details"]["field"] == "value"
    assert error_dict["status_code"] == 500

def test_validation_error():
    """Test ValidationError creation and properties."""
    error = ValidationError(
        message="Invalid input data",
        field_errors={"name": "Required field"}
    )
    
    assert error.message == "Invalid input data"
    assert error.code == "VALIDATION_ERROR"
    assert error.field_errors["name"] == "Required field"
    assert error.status_code == 400
    
    # Test error serialization
    error_dict = error.to_dict()
    assert error_dict["message"] == "Invalid input data"
    assert error_dict["code"] == "VALIDATION_ERROR"
    assert error_dict["field_errors"]["name"] == "Required field"
    assert error_dict["status_code"] == 400

def test_authentication_error():
    """Test AuthenticationError creation and properties."""
    error = AuthenticationError(
        message="Invalid authentication token",
        details={"token_type": "JWT"}
    )
    
    assert error.message == "Invalid authentication token"
    assert error.code == "AUTHENTICATION_ERROR"
    assert error.details["token_type"] == "JWT"
    assert error.status_code == 401
    
    # Test error serialization
    error_dict = error.to_dict()
    assert error_dict["message"] == "Invalid authentication token"
    assert error_dict["code"] == "AUTHENTICATION_ERROR"
    assert error_dict["details"]["token_type"] == "JWT"
    assert error_dict["status_code"] == 401

def test_authorization_error():
    """Test AuthorizationError creation and properties."""
    error = AuthorizationError(
        message="Insufficient permissions",
        required_role="admin",
        current_role="user"
    )
    
    assert error.message == "Insufficient permissions"
    assert error.code == "AUTHORIZATION_ERROR"
    assert error.details["required_role"] == "admin"
    assert error.details["current_role"] == "user"
    assert error.status_code == 403
    
    # Test error serialization
    error_dict = error.to_dict()
    assert error_dict["message"] == "Insufficient permissions"
    assert error_dict["code"] == "AUTHORIZATION_ERROR"
    assert error_dict["details"]["required_role"] == "admin"
    assert error_dict["details"]["current_role"] == "user"
    assert error_dict["status_code"] == 403

def test_not_found_error():
    """Test NotFoundError creation and properties."""
    error = NotFoundError(
        message="Resource not found",
        resource_id="123",
        resource_type="user"
    )
    
    assert error.message == "Resource not found"
    assert error.code == "NOT_FOUND_ERROR"
    assert error.details["resource_id"] == "123"
    assert error.details["resource_type"] == "user"
    assert error.status_code == 404
    
    # Test error serialization
    error_dict = error.to_dict()
    assert error_dict["message"] == "Resource not found"
    assert error_dict["code"] == "NOT_FOUND_ERROR"
    assert error_dict["details"]["resource_id"] == "123"
    assert error_dict["details"]["resource_type"] == "user"
    assert error_dict["status_code"] == 404

def test_database_error():
    """Test DatabaseError creation and properties."""
    error = DatabaseError(
        message="Database operation failed",
        operation="insert",
        table="users",
        details={"constraint": "unique_email"}
    )
    
    assert error.message == "Database operation failed"
    assert error.code == "DATABASE_ERROR"
    assert error.details["operation"] == "insert"
    assert error.details["table"] == "users"
    assert error.details["constraint"] == "unique_email"
    assert error.status_code == 500
    
    # Test error serialization
    error_dict = error.to_dict()
    assert error_dict["message"] == "Database operation failed"
    assert error_dict["code"] == "DATABASE_ERROR"
    assert error_dict["details"]["operation"] == "insert"
    assert error_dict["details"]["table"] == "users"
    assert error_dict["details"]["constraint"] == "unique_email"
    assert error_dict["status_code"] == 500

def test_service_error():
    """Test ServiceError creation and properties."""
    error = ServiceError(
        message="External service failed",
        service_name="payment",
        operation="process_payment",
        details={"error_code": "INSUFFICIENT_FUNDS"}
    )
    
    assert error.message == "External service failed"
    assert error.code == "SERVICE_ERROR"
    assert error.details["service_name"] == "payment"
    assert error.details["operation"] == "process_payment"
    assert error.details["error_code"] == "INSUFFICIENT_FUNDS"
    assert error.status_code == 500
    
    # Test error serialization
    error_dict = error.to_dict()
    assert error_dict["message"] == "External service failed"
    assert error_dict["code"] == "SERVICE_ERROR"
    assert error_dict["details"]["service_name"] == "payment"
    assert error_dict["details"]["operation"] == "process_payment"
    assert error_dict["details"]["error_code"] == "INSUFFICIENT_FUNDS"
    assert error_dict["status_code"] == 500

def test_error_inheritance():
    """Test error class inheritance."""
    # Test ValidationError inheritance
    validation_error = ValidationError("Invalid input")
    assert isinstance(validation_error, ICMPError)
    assert validation_error.status_code == 400
    
    # Test AuthenticationError inheritance
    auth_error = AuthenticationError("Invalid token")
    assert isinstance(auth_error, ICMPError)
    assert auth_error.status_code == 401
    
    # Test AuthorizationError inheritance
    authz_error = AuthorizationError("Insufficient permissions")
    assert isinstance(authz_error, ICMPError)
    assert authz_error.status_code == 403
    
    # Test NotFoundError inheritance
    not_found_error = NotFoundError("Resource not found")
    assert isinstance(not_found_error, ICMPError)
    assert not_found_error.status_code == 404
    
    # Test DatabaseError inheritance
    db_error = DatabaseError("Database operation failed")
    assert isinstance(db_error, ICMPError)
    assert db_error.status_code == 500
    
    # Test ServiceError inheritance
    service_error = ServiceError("External service failed")
    assert isinstance(service_error, ICMPError)
    assert service_error.status_code == 500

def test_error_customization():
    """Test error customization."""
    # Test custom status code
    error = ICMPError("Test error", status_code=418)
    assert error.status_code == 418
    
    # Test custom error code
    error = ICMPError("Test error", code="CUSTOM_ERROR")
    assert error.code == "CUSTOM_ERROR"
    
    # Test custom details
    error = ICMPError("Test error", details={"custom": "value"})
    assert error.details["custom"] == "value"
    
    # Test custom field errors
    error = ValidationError("Invalid input", field_errors={"custom": "error"})
    assert error.field_errors["custom"] == "error"

def test_error_equality():
    """Test error equality comparison."""
    error1 = ICMPError("Test error", code="TEST_ERROR")
    error2 = ICMPError("Test error", code="TEST_ERROR")
    error3 = ICMPError("Different error", code="DIFFERENT_ERROR")
    
    assert error1 == error2
    assert error1 != error3
    
    # Test different error types
    validation_error = ValidationError("Invalid input")
    auth_error = AuthenticationError("Invalid token")
    assert validation_error != auth_error

def test_error_string_representation():
    """Test error string representation."""
    error = ICMPError("Test error", code="TEST_ERROR")
    error_str = str(error)
    
    assert "Test error" in error_str
    assert "TEST_ERROR" in error_str
    
    # Test with details
    error = ICMPError("Test error", details={"field": "value"})
    error_str = str(error)
    
    assert "Test error" in error_str
    assert "field" in error_str
    assert "value" in error_str 