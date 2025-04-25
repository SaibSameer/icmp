import sys
import os

# Add the 'backend' directory to the Python path
project_root = os.path.dirname(__file__)
backend_dir = os.path.join(project_root, 'backend') # Construct path to backend
sys.path.insert(0, backend_dir)

# You can also define project-wide fixtures here later if needed