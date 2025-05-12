import pytest
from backend.error_handling import (
    ErrorValidator, ValidationError, ICMPError,
    AuthenticationError, AuthorizationError
)

def test_error_validator_initialization():
    """Test error validator initialization."""
    validator = ErrorValidator()
    assert validator.schemas == {}
    assert validator.validators == {}

def test_register_error_schema():
    """Test registering an error schema."""
    validator = ErrorValidator()
    schema = {
        "type": "object",
        "required": ["code", "message"],
        "properties": {
            "code": {"type": "string"},
            "message": {"type": "string"}
        }
    }
    
    validator.register_schema("TEST_ERROR", schema)
    assert "TEST_ERROR" in validator.schemas
    assert validator.schemas["TEST_ERROR"] == schema

def test_validate_error():
    """Test validating an error against its schema."""
    validator = ErrorValidator()
    schema = {
        "type": "object",
        "required": ["code", "message"],
        "properties": {
            "code": {"type": "string"},
            "message": {"type": "string"}
        }
    }
    
    validator.register_schema("TEST_ERROR", schema)
    error = ICMPError("Test error", code="TEST_ERROR")
    
    assert validator.validate_error(error) is True

def test_validate_error_with_invalid_schema():
    """Test validating an error with invalid schema."""
    validator = ErrorValidator()
    schema = {
        "type": "object",
        "required": ["code", "message", "invalid_field"],
        "properties": {
            "code": {"type": "string"},
            "message": {"type": "string"},
            "invalid_field": {"type": "string"}
        }
    }
    
    validator.register_schema("TEST_ERROR", schema)
    error = ICMPError("Test error", code="TEST_ERROR")
    
    assert validator.validate_error(error) is False

def test_validate_error_with_custom_validator():
    """Test validating an error with custom validator."""
    validator = ErrorValidator()
    validation_results = []
    
    def custom_validator(error):
        validation_results.append(error)
        return True
    
    validator.register_validator("TEST_ERROR", custom_validator)
    error = ICMPError("Test error", code="TEST_ERROR")
    
    assert validator.validate_error(error) is True
    assert len(validation_results) == 1
    assert validation_results[0] == error

def test_validate_error_with_multiple_validators():
    """Test validating an error with multiple validators."""
    validator = ErrorValidator()
    validation_results = []
    
    def validator1(error):
        validation_results.append(("validator1", error))
        return True
    
    def validator2(error):
        validation_results.append(("validator2", error))
        return True
    
    validator.register_validator("TEST_ERROR", [validator1, validator2])
    error = ICMPError("Test error", code="TEST_ERROR")
    
    assert validator.validate_error(error) is True
    assert len(validation_results) == 2
    assert validation_results[0][0] == "validator1"
    assert validation_results[1][0] == "validator2"

def test_validate_error_with_failing_validator():
    """Test validating an error with failing validator."""
    validator = ErrorValidator()
    validation_results = []
    
    def failing_validator(error):
        validation_results.append(error)
        return False
    
    validator.register_validator("TEST_ERROR", failing_validator)
    error = ICMPError("Test error", code="TEST_ERROR")
    
    assert validator.validate_error(error) is False
    assert len(validation_results) == 1

def test_validate_error_with_validation_error():
    """Test validating a validation error."""
    validator = ErrorValidator()
    schema = {
        "type": "object",
        "required": ["code", "message", "field_errors"],
        "properties": {
            "code": {"type": "string"},
            "message": {"type": "string"},
            "field_errors": {"type": "object"}
        }
    }
    
    validator.register_schema("VALIDATION_ERROR", schema)
    error = ValidationError("Invalid input", field_errors={"field": "error"})
    
    assert validator.validate_error(error) is True

def test_validate_error_with_authentication_error():
    """Test validating an authentication error."""
    validator = ErrorValidator()
    schema = {
        "type": "object",
        "required": ["code", "message"],
        "properties": {
            "code": {"type": "string"},
            "message": {"type": "string"}
        }
    }
    
    validator.register_schema("AUTHENTICATION_ERROR", schema)
    error = AuthenticationError("Invalid token")
    
    assert validator.validate_error(error) is True

def test_validate_error_with_authorization_error():
    """Test validating an authorization error."""
    validator = ErrorValidator()
    schema = {
        "type": "object",
        "required": ["code", "message", "required_role"],
        "properties": {
            "code": {"type": "string"},
            "message": {"type": "string"},
            "required_role": {"type": "string"}
        }
    }
    
    validator.register_schema("AUTHORIZATION_ERROR", schema)
    error = AuthorizationError("Insufficient permissions", required_role="admin")
    
    assert validator.validate_error(error) is True

def test_validate_error_with_unknown_schema():
    """Test validating an error with unknown schema."""
    validator = ErrorValidator()
    error = ICMPError("Test error", code="UNKNOWN_ERROR")
    
    assert validator.validate_error(error) is True  # Default to True for unknown schemas

def test_validate_error_with_schema_update():
    """Test validating an error after schema update."""
    validator = ErrorValidator()
    schema1 = {
        "type": "object",
        "required": ["code", "message"],
        "properties": {
            "code": {"type": "string"},
            "message": {"type": "string"}
        }
    }
    
    schema2 = {
        "type": "object",
        "required": ["code", "message", "details"],
        "properties": {
            "code": {"type": "string"},
            "message": {"type": "string"},
            "details": {"type": "object"}
        }
    }
    
    validator.register_schema("TEST_ERROR", schema1)
    error = ICMPError("Test error", code="TEST_ERROR")
    assert validator.validate_error(error) is True
    
    validator.register_schema("TEST_ERROR", schema2)
    assert validator.validate_error(error) is False 