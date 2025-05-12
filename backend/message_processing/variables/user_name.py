"""
User name variable provider.

Provides the full name of a user based on their user_id.
"""

import logging
from ..template_variables import TemplateVariableProvider
from .database_utils import DatabaseUtils

log = logging.getLogger(__name__)

@TemplateVariableProvider.register_provider(
    'user_name',
    description='Provides the full name of a user based on their user_id',
    auth_requirement='business_key'
)
def provide_user_name(conn, user_id: str, **kwargs) -> str:
    """
    Get the full name of a user.
    
    Args:
        conn: Database connection
        user_id: UUID of the user
        **kwargs: Additional context parameters (ignored)
        
    Returns:
        User's full name or 'Guest' if not found
    """
    try:
        # Execute query
        results = DatabaseUtils.execute_query(
            conn,
            """
            SELECT first_name, last_name
            FROM users 
            WHERE user_id = %s
            """,
            (user_id,)
        )
        
        # Process results
        if not results:
            return "Guest"
            
        user = results[0]
        first_name = user.get('first_name', '').strip()
        last_name = user.get('last_name', '').strip()
        
        if not first_name and not last_name:
            return "Guest"
            
        return f"{first_name} {last_name}".strip()
    except Exception as e:
        log.error(f"Error providing user_name: {str(e)}", exc_info=True)
        return "Guest"