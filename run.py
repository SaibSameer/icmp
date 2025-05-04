import os
import sys

# Add the root directory to Python path
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)

# Now import and run the app
from backend.app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) 