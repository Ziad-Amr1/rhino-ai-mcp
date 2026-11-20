"""Example 03: Inspect and filter layers and objects."""

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rhino_client import RhinoClient

def main():
    client = RhinoClient()

    # 1. Query all layers
    print("Listing document layers:")
    layers_data = client.list_layers()
    for lyr in layers_data.get("layers", []):
        print(f"  - Layer [{lyr.get('index')}]: {lyr.get('name')} (Color: {lyr.get('color')}, Visible: {lyr.get('visible')})")

    # 2. Query objects
    print("\nQuerying first 10 objects:")
    objects_data = client.query_objects(limit=10)
    for obj in objects_data.get("objects", []):
        print(f"  - Object: {obj.get('name', 'Unnamed')} (Type: {obj.get('type')}, Layer: {obj.get('layer')})")

if __name__ == "__main__":
    main()
