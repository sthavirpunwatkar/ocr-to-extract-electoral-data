import sys
import os

# Add the backend path to sys.path
sys.path.append(os.path.abspath("backend"))

from app.core.templates import engine

def test_template_loading():
    template = engine.get_template("maharashtra_voter_roll")
    if template:
        print(f"Successfully loaded template: {template.template_name}")
        print(f"Region: {template.region}")
        print(f"Fields: {list(template.fields.keys())}")
        return True
    else:
        print("Failed to load template 'maharashtra_voter_roll'")
        print(f"Available templates: {engine.list_templates()}")
        return False

if __name__ == "__main__":
    success = test_template_loading()
    sys.exit(0 if success else 1)
