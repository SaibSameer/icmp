"""
Variable providers package.

Import all variable providers to ensure they are registered.
"""
# Import all variable providers to ensure they're registered
from . import user_name
from . import last_10_messages
from . import available_stages
from .. import standard_variables  # Import standard variables to ensure all providers are registered