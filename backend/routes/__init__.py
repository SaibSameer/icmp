# file: C:\icmp_events_api\backend\routes\__init__.py
# This file can optionally be used to expose blueprints 
# but avoid importing 'app' here to prevent circular dependencies.

import logging

# Import blueprints so they can be accessed via routes.<n>
from . import businesses
from . import conversations
from . import health
from . import message_handling
from . import ping
from . import stages
from . import template_management
from . import users
from . import templates
from . import agents
from . import business_management # Still need to import the module
from . import transitions  # Add the transitions module
from . import debug

log = logging.getLogger(__name__)

# print("Executing routes/__init__.py") # Keep for debugging if needed, remove later

# DO NOT register blueprints here using an imported 'app' object.
# Registration should happen in app.py AFTER 'app' is created.