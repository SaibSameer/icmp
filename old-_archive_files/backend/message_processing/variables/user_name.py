"""
User name variable provider.
"""
import logging
from ..template_variables import TemplateVariableProvider

log = logging.getLogger(__name__)

@TemplateVariableProvider.register_provider('user_name')
def provide_user_name(conn, user_id: str, **kwargs) -> str:
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT first_name, last_name
            FROM users 
            WHERE user_id = %s
            """,
            (user_id,)
        )
        
        user = cursor.fetchone()
        if not user:
            return "Guest"
            
        return f"{user['first_name']} {user['last_name']}".strip()
        
    except Exception as e:
        log.error(f"Error providing user_name: {str(e)}")
        return "Guest"