from flask import Blueprint, request
from backend.utils.error_handler import handle_api_errors
from backend.utils.request_validator import RequestValidator
from backend.utils.response_handler import APIResponse

bp = Blueprint('example', __name__)

@bp.route('/example', methods=['POST'])
@handle_api_errors
def example_endpoint():
    """Example endpoint demonstrating the new utilities."""
    # Get request data
    data = request.get_json()
    
    # Validate request data
    RequestValidator.validate_all(
        data=data,
        required_fields=['name', 'age'],
        type_map={
            'name': str,
            'age': int
        },
        length_map={
            'name': {'min': 2, 'max': 50}
        },
        range_map={
            'age': {'min': 0, 'max': 120}
        }
    )
    
    # Process the request (example)
    result = {
        'message': f"Hello, {data['name']}!",
        'age': data['age']
    }
    
    # Return standardized response
    return APIResponse.success(
        data=result,
        message="Example request processed successfully"
    )

@bp.route('/example/<id>', methods=['GET'])
@handle_api_errors
def get_example(id):
    """Example GET endpoint."""
    # Validate ID format
    RequestValidator.validate_pattern(
        data={'id': id},
        pattern_map={'id': r'^[a-zA-Z0-9-]+$'}
    )
    
    # Example data retrieval
    result = {
        'id': id,
        'name': 'Example Item',
        'created_at': '2024-01-01T00:00:00Z'
    }
    
    return APIResponse.success(data=result) 