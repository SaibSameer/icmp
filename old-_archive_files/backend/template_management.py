from db import get_db_connection, release_db_connection
import logging
import uuid

log = logging.getLogger(__name__)

class TemplateManager:
    @staticmethod
    def get(template_id: str) -> dict:
        """Retrieve template with validation metadata"""
        conn = get_db_connection()
        try:
            with conn.cursor() as c:
                c.execute('''
                    SELECT template_id, template_text, variables
                    FROM default_templates
                    WHERE template_id = %s;
                ''', (template_id,))
                result = c.fetchone()
                if not result:
                    raise ValueError(f"Template {template_id} not found")
                return {
                    'id': result[0],
                    'text': result[1],
                    'variables': result[2]
                }
        except Exception as e:
            log.error(f"Template fetch failed: {str(e)}")
            raise
        finally:
            release_db_connection(conn)

    @staticmethod
    def validate_placeholders(template_id: str, context: dict) -> bool:
        """Verify all required placeholders are provided"""
        template = TemplateManager.get(template_id)
        if template is None:
            raise ValueError(f"No Template found for: {template_id}")

        required_vars = set(template['variables'])
        provided_vars = set(context.keys())

        missing = required_vars - provided_vars
        if missing:
            raise ValueError(f"Missing variables for template {template_id}: {missing}")
        return True

    @staticmethod
    def render(template_id: str, context: dict) -> str:
        """Render template with context after validation"""
        TemplateManager.validate_placeholders(template_id, context)
        template = TemplateManager.get(template_id)
        if template is None:
             raise ValueError(f"No Template found for: {template_id}")
        return template['text'].format(**context)