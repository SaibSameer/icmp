"""
Business Information Variable Provider

Provides detailed information about a business including:
- Basic info (name, description)
- Contact details (phone, website)
- Address
- Metadata (creation date, owner, etc.)
"""
import logging
from backend.message_processing.template_variables import TemplateVariableProvider
from backend.db import get_db_connection

log = logging.getLogger(__name__)

@TemplateVariableProvider.register_provider(
    'business_info',
    description='Provides detailed information about a business including name, description, contact details, and address',
    auth_requirement='business_key'
)
def provide_business_info(business_id, **kwargs):
    """
    Generate business information based on the business ID.
    
    Args:
        business_id: UUID of the business
        **kwargs: Additional arguments (e.g., format='text' or 'json')
        
    Returns:
        Formatted business information
    """
    log.info(f"Starting business_info provider for business_id: {business_id}")
    log.info(f"Additional arguments: {kwargs}")
    
    # Default configuration
    config = {
        'include_address': True,
        'include_contact': True,
        'format': kwargs.get('format', 'text')
    }
    log.info(f"Configuration: {config}")
    
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Query business details
            cursor.execute("""
                SELECT
                    business_id,
                    api_key,
                    internal_api_key,
                    owner_id,
                    business_name,
                    business_description,
                    address,
                    phone_number,
                    website,
                    first_stage_id,
                    facebook_page_id,
                    created_at,
                    updated_at,
                    business_information
                FROM businesses
                WHERE business_id = %s
            """, (business_id,))
            
            business_data = cursor.fetchone()
            if not business_data:
                return "Business not found"
                
            log.info(f"Retrieved business data: {business_data}")
            
            # Prepare structured data
            prepared_data = {
                'id': business_data['business_id'],
                'name': business_data['business_name'],
                'description': business_data['business_description'],
                'additional_info': business_data['business_information'],
                'metadata': {
                    'created_at': business_data['created_at'].isoformat(),
                    'updated_at': business_data['updated_at'].isoformat(),
                    'owner_id': business_data['owner_id'],
                    'first_stage_id': business_data['first_stage_id'],
                    'facebook_page_id': business_data['facebook_page_id'],
                    'api_key': business_data['api_key'],
                    'internal_api_key': business_data['internal_api_key']
                }
            }
            
            # Add contact info if requested
            if config['include_contact']:
                prepared_data['contact'] = {
                    'phone': business_data['phone_number'],
                    'website': business_data['website']
                }
            
            # Add address if requested
            if config['include_address']:
                prepared_data['address'] = business_data['address']
            
            log.info(f"Prepared business data: {prepared_data}")
            
            # Format output based on requested format
            if config['format'] == 'json':
                return prepared_data
            else:
                # Default to text format
                text_output = f"""=== Business Information ===
Name: {prepared_data['name']}
Description: {prepared_data['description']}
Additional Information: {prepared_data['additional_info']}"""
                
                if 'address' in prepared_data:
                    text_output += f"\nAddress: {prepared_data['address']}"
                    
                if 'contact' in prepared_data:
                    if prepared_data['contact']['phone']:
                        text_output += f"\nPhone: {prepared_data['contact']['phone']}"
                    if prepared_data['contact']['website']:
                        text_output += f"\nWebsite: {prepared_data['contact']['website']}"
                
                text_output += f"""
Created: {prepared_data['metadata']['created_at']}
Last Updated: {prepared_data['metadata']['updated_at']}
==========================="""
                
                log.info("Final text output:\n" + text_output)
                return text_output
                
    except Exception as e:
        log.error(f"Error in business_info provider: {str(e)}", exc_info=True)
        return f"Error retrieving business information: {str(e)}"
    finally:
        if 'conn' in locals():
            conn.close() 