import pytest
from flask import Flask
from backend.error_handling import (
    ErrorConfig, ErrorHandler, ErrorTracker,
    ErrorMonitor, ErrorLogger, ErrorResponse,
    ErrorValidator, ErrorRecovery
)

def test_error_config_initialization():
    """Test error configuration initialization."""
    config = ErrorConfig()
    assert config.default_status_code == 500
    assert config.default_error_code == "INTERNAL_ERROR"
    assert config.error_tracker is None
    assert config.error_monitor is None
    assert config.error_logger is None
    assert config.error_response is None
    assert config.error_validator is None
    assert config.error_recovery is None

def test_error_config_with_custom_values():
    """Test error configuration with custom values."""
    config = ErrorConfig(
        default_status_code=400,
        default_error_code="CUSTOM_ERROR",
        error_tracker=ErrorTracker(),
        error_monitor=ErrorMonitor(),
        error_logger=ErrorLogger(),
        error_response=ErrorResponse(),
        error_validator=ErrorValidator(),
        error_recovery=ErrorRecovery()
    )
    
    assert config.default_status_code == 400
    assert config.default_error_code == "CUSTOM_ERROR"
    assert isinstance(config.error_tracker, ErrorTracker)
    assert isinstance(config.error_monitor, ErrorMonitor)
    assert isinstance(config.error_logger, ErrorLogger)
    assert isinstance(config.error_response, ErrorResponse)
    assert isinstance(config.error_validator, ErrorValidator)
    assert isinstance(config.error_recovery, ErrorRecovery)

def test_error_config_with_flask_app():
    """Test error configuration with Flask app."""
    app = Flask(__name__)
    config = ErrorConfig()
    
    # Configure app with error handling
    config.init_app(app)
    
    assert hasattr(app, 'error_handler')
    assert isinstance(app.error_handler, ErrorHandler)
    assert app.error_handler.error_tracker == config.error_tracker
    assert app.error_handler.error_monitor == config.error_monitor
    assert app.error_handler.error_logger == config.error_logger
    assert app.error_handler.error_response == config.error_response
    assert app.error_handler.error_validator == config.error_validator
    assert app.error_handler.error_recovery == config.error_recovery

def test_error_config_with_custom_components():
    """Test error configuration with custom components."""
    app = Flask(__name__)
    tracker = ErrorTracker()
    monitor = ErrorMonitor(error_tracker=tracker)
    logger = ErrorLogger()
    response = ErrorResponse()
    validator = ErrorValidator()
    recovery = ErrorRecovery()
    
    config = ErrorConfig(
        error_tracker=tracker,
        error_monitor=monitor,
        error_logger=logger,
        error_response=response,
        error_validator=validator,
        error_recovery=recovery
    )
    
    config.init_app(app)
    
    assert app.error_handler.error_tracker == tracker
    assert app.error_handler.error_monitor == monitor
    assert app.error_handler.error_logger == logger
    assert app.error_handler.error_response == response
    assert app.error_handler.error_validator == validator
    assert app.error_handler.error_recovery == recovery

def test_error_config_with_error_schemas():
    """Test error configuration with error schemas."""
    config = ErrorConfig()
    validator = ErrorValidator()
    
    # Register error schemas
    schemas = {
        "VALIDATION_ERROR": {
            "type": "object",
            "required": ["code", "message", "field_errors"],
            "properties": {
                "code": {"type": "string"},
                "message": {"type": "string"},
                "field_errors": {"type": "object"}
            }
        },
        "AUTHENTICATION_ERROR": {
            "type": "object",
            "required": ["code", "message"],
            "properties": {
                "code": {"type": "string"},
                "message": {"type": "string"}
            }
        }
    }
    
    for error_code, schema in schemas.items():
        validator.register_schema(error_code, schema)
    
    config.error_validator = validator
    
    assert "VALIDATION_ERROR" in config.error_validator.schemas
    assert "AUTHENTICATION_ERROR" in config.error_validator.schemas

def test_error_config_with_alert_thresholds():
    """Test error configuration with alert thresholds."""
    config = ErrorConfig()
    monitor = ErrorMonitor()
    
    # Set alert thresholds
    thresholds = {
        "VALIDATION_ERROR": {"rate": 0.5, "window_minutes": 5},
        "AUTHENTICATION_ERROR": {"rate": 0.3, "window_minutes": 10}
    }
    
    for error_type, threshold in thresholds.items():
        monitor.set_alert_threshold(
            error_type,
            rate=threshold["rate"],
            window_minutes=threshold["window_minutes"]
        )
    
    config.error_monitor = monitor
    
    assert "VALIDATION_ERROR" in config.error_monitor.alert_thresholds
    assert "AUTHENTICATION_ERROR" in config.error_monitor.alert_thresholds

def test_error_config_with_custom_formatters():
    """Test error configuration with custom formatters."""
    config = ErrorConfig()
    response = ErrorResponse()
    
    # Define custom formatters
    def validation_formatter(error):
        return {
            "status": "error",
            "type": error.code,
            "message": error.message,
            "fields": error.field_errors
        }
    
    def auth_formatter(error):
        return {
            "status": "error",
            "type": error.code,
            "message": error.message
        }
    
    response.register_formatter("VALIDATION_ERROR", validation_formatter)
    response.register_formatter("AUTHENTICATION_ERROR", auth_formatter)
    
    config.error_response = response
    
    assert "VALIDATION_ERROR" in config.error_response.formatters
    assert "AUTHENTICATION_ERROR" in config.error_response.formatters

def test_error_config_with_error_handlers():
    """Test error configuration with error handlers."""
    config = ErrorConfig()
    recovery = ErrorRecovery()
    
    # Define error handlers
    def validation_handler(error):
        return {"status": "recovered", "error": error.code}
    
    def auth_handler(error):
        return {"status": "recovered", "error": error.code}
    
    recovery.register_handler("VALIDATION_ERROR", validation_handler)
    recovery.register_handler("AUTHENTICATION_ERROR", auth_handler)
    
    config.error_recovery = recovery
    
    assert "VALIDATION_ERROR" in config.error_recovery.handlers
    assert "AUTHENTICATION_ERROR" in config.error_recovery.handlers

def test_error_config_with_logging_config():
    """Test error configuration with logging configuration."""
    config = ErrorConfig()
    logger = ErrorLogger()
    
    # Configure logging
    logger.configure(
        level="ERROR",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=["console", "file"]
    )
    
    config.error_logger = logger
    
    assert config.error_logger.logger.level == "ERROR"
    assert config.error_logger.logger.handlers is not None

def test_error_config_with_monitoring_config():
    """Test error configuration with monitoring configuration."""
    config = ErrorConfig()
    monitor = ErrorMonitor()
    
    # Configure monitoring
    monitor.configure(
        check_interval=60,
        alert_cooldown=300,
        max_alerts=10
    )
    
    config.error_monitor = monitor
    
    assert config.error_monitor.check_interval == 60
    assert config.error_monitor.alert_cooldown == 300
    assert config.error_monitor.max_alerts == 10 