from app import create_app
from flask import url_for

app = create_app()

def check_routes():
    with app.test_request_context():
        print("\n=== Route Details ===")
        for rule in app.url_map.iter_rules():
            print(f"\nRoute: {rule}")
            print(f"Endpoint: {rule.endpoint}")
            print(f"Methods: {', '.join(rule.methods)}")
            try:
                print(f"URL: {url_for(rule.endpoint)}")
            except:
                print("URL: Requires parameters")
        print("\n=== Route Count ===")
        print(f"Total routes: {len(list(app.url_map.iter_rules()))}")

if __name__ == '__main__':
    check_routes()