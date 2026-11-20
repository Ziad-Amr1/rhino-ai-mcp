"""Example 02: Parametric geometric primitives creation in Rhino."""

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rhino_client import RhinoClient

def main():
    client = RhinoClient()

    # 1. Create a Box
    print("Creating parametric Box (20 x 10 x 5) at (0, 0, 0)...")
    box_res = client.create_geometry("box", origin=[0, 0, 0], size=[20, 10, 5])
    print("Box creation result:", box_res)

    # 2. Create a Cylinder
    print("Creating parametric Cylinder (radius 4, height 12) at (30, 0, 0)...")
    cyl_res = client.create_geometry("cylinder", origin=[30, 0, 0], radius=4.0, height=12.0)
    print("Cylinder creation result:", cyl_res)

    # 3. Create a Sphere
    print("Creating parametric Sphere (radius 6) at (50, 0, 0)...")
    sph_res = client.create_geometry("sphere", origin=[50, 0, 0], radius=6.0)
    print("Sphere creation result:", sph_res)

if __name__ == "__main__":
    main()
