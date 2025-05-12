from flask import Blueprint, request, jsonify
from backend.template_management.template_manager import TemplateManager
from backend.message_processing.template_variables import TemplateVariableProvider
from backend.db import get_db_pool
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('template_test', __name__)

@bp.route('/', methods=['POST'])
def test_template():
    try:
        data = request.get_json()
        business_id = data.get('business_id')
        template_content = data.get('template_content')
        test_mode = data.get('test_mode', False)

        if not business_id:
            return jsonify({'error': 'Missing required parameters'}), 400

        if test_mode and not template_content:
            return jsonify({'error': 'Template content is required for testing'}), 400

        # Get database connection
        conn = get_db_pool().getconn()
        try:
            # Initialize services
            template_manager = TemplateManager(conn)
            variable_provider = TemplateVariableProvider(conn)

            if test_mode:
                # Test single template content
                context = variable_provider.get_test_context(business_id, None)
                result = template_manager.render_template(template_content, context)
                return jsonify({
                    'success': True,
                    'content': result
                })
            else:
                # Test all templates for the business/agent
                templates = template_manager.get_templates(business_id)
                context = variable_provider.get_test_context(business_id, None)
                
                results = {}
                for template in templates:
                    try:
                        substituted_content = template_manager.render_template(template['content'], context)
                        results[template['template_type']] = {
                            'content': substituted_content
                        }
                    except Exception as e:
                        logger.error(f"Error processing template {template['template_type']}: {str(e)}")
                        results[template['template_type']] = {
                            'error': str(e)
                        }

                return jsonify({
                    'success': True,
                    'results': results
                })

        finally:
            get_db_pool().putconn(conn)

    except Exception as e:
        logger.error(f"Error in template test: {str(e)}")
        return jsonify({'error': str(e)}), 500 