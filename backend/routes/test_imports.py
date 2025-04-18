import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from routes.businesses import bp
    print("SUCCESS: Imported bp from businesses.py")
    print(f"Blueprint details: name={bp.name}, url_prefix={bp.url_prefix}")
except ImportError as e:
    print(f"FAILED: {str(e)}")
    print("Trying to debug...")
    
    from importlib.util import find_spec
    print(f"Module found: {find_spec('routes.businesses')}")
    
    if find_spec('routes.businesses'):
        from routes import businesses
        print(f"Contents of businesses.py: {dir(businesses)}")
        if hasattr(businesses, 'bp'):
            print("Blueprint exists but couldn't be imported directly!")