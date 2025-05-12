from typing import Any, Dict, List, Optional, Union
from .error_handler import ValidationError

class RequestValidator:
    """Utility for validating request data."""
    
    @staticmethod
    def validate_required(data: Dict, required_fields: List[str]) -> None:
        """Validate that all required fields are present."""
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
    
    @staticmethod
    def validate_types(data: Dict, type_map: Dict[str, type]) -> None:
        """Validate that fields have the correct types."""
        for field, expected_type in type_map.items():
            if field in data and not isinstance(data[field], expected_type):
                raise ValidationError(
                    f"Invalid type for field '{field}'. Expected {expected_type.__name__}, got {type(data[field]).__name__}"
                )
    
    @staticmethod
    def validate_values(data: Dict, value_map: Dict[str, List[Any]]) -> None:
        """Validate that fields have allowed values."""
        for field, allowed_values in value_map.items():
            if field in data and data[field] not in allowed_values:
                raise ValidationError(
                    f"Invalid value for field '{field}'. Allowed values: {', '.join(map(str, allowed_values))}"
                )
    
    @staticmethod
    def validate_length(data: Dict, length_map: Dict[str, Dict[str, int]]) -> None:
        """Validate field lengths."""
        for field, constraints in length_map.items():
            if field in data:
                value = str(data[field])
                if 'min' in constraints and len(value) < constraints['min']:
                    raise ValidationError(
                        f"Field '{field}' is too short. Minimum length: {constraints['min']}"
                    )
                if 'max' in constraints and len(value) > constraints['max']:
                    raise ValidationError(
                        f"Field '{field}' is too long. Maximum length: {constraints['max']}"
                    )
    
    @staticmethod
    def validate_numeric_range(
        data: Dict,
        range_map: Dict[str, Dict[str, Union[int, float]]]
    ) -> None:
        """Validate numeric ranges."""
        for field, constraints in range_map.items():
            if field in data:
                value = data[field]
                if not isinstance(value, (int, float)):
                    raise ValidationError(f"Field '{field}' must be numeric")
                
                if 'min' in constraints and value < constraints['min']:
                    raise ValidationError(
                        f"Field '{field}' is too small. Minimum value: {constraints['min']}"
                    )
                if 'max' in constraints and value > constraints['max']:
                    raise ValidationError(
                        f"Field '{field}' is too large. Maximum value: {constraints['max']}"
                    )
    
    @staticmethod
    def validate_pattern(data: Dict, pattern_map: Dict[str, str]) -> None:
        """Validate field patterns using regular expressions."""
        import re
        for field, pattern in pattern_map.items():
            if field in data:
                value = str(data[field])
                if not re.match(pattern, value):
                    raise ValidationError(
                        f"Field '{field}' does not match required pattern"
                    )
    
    @staticmethod
    def validate_all(
        data: Dict,
        required_fields: Optional[List[str]] = None,
        type_map: Optional[Dict[str, type]] = None,
        value_map: Optional[Dict[str, List[Any]]] = None,
        length_map: Optional[Dict[str, Dict[str, int]]] = None,
        range_map: Optional[Dict[str, Dict[str, Union[int, float]]]] = None,
        pattern_map: Optional[Dict[str, str]] = None
    ) -> None:
        """Perform all validations in one call."""
        if required_fields:
            RequestValidator.validate_required(data, required_fields)
        if type_map:
            RequestValidator.validate_types(data, type_map)
        if value_map:
            RequestValidator.validate_values(data, value_map)
        if length_map:
            RequestValidator.validate_length(data, length_map)
        if range_map:
            RequestValidator.validate_numeric_range(data, range_map)
        if pattern_map:
            RequestValidator.validate_pattern(data, pattern_map) 