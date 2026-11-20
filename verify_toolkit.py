"""Pre-release toolkit verification script."""

import os
import sys
import re
import glob
import json

def verify_tools_and_schemas():
    print("=== 1. Checking MCP Tools and Schemas ===")
    with open("mcp_server.py", "r", encoding="utf-8") as f:
        code = f.read()

    tools = re.findall(r'@mcp\.tool\(name=[\'"]([^\'"]+)[\'"]\)', code)
    schemas = [os.path.basename(f)[:-5] for f in glob.glob("mcp_schemas/*.json")]

    print(f"Found {len(tools)} tools in mcp_server.py:")
    for t in sorted(tools):
        print(f"  - {t}")

    print(f"\nFound {len(schemas)} schemas in mcp_schemas/:")
    for s in sorted(schemas):
        print(f"  - {s}")

    assert len(tools) == 13, f"Expected 13 tools, found {len(tools)}"
    assert len(schemas) == 13, f"Expected 13 schemas, found {len(schemas)}"
    assert set(tools) == set(schemas), f"Mismatch: {set(tools) ^ set(schemas)}"
    print("\n[PASS] MCP tools and schemas are 100% consistent (all 13 match).")

def verify_readme():
    print("\n=== 2. Checking README Documentation ===")
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    with open("mcp_server.py", "r", encoding="utf-8") as f:
        code = f.read()

    tools = re.findall(r'@mcp\.tool\(name=[\'"]([^\'"]+)[\'"]\)', code)
    for t in tools:
        assert f"`{t}`" in readme, f"Tool `{t}` is missing in README.md table!"

    print(f"[PASS] All {len(tools)} tools are documented in README.md.")

def verify_archive():
    print("\n=== 3. Checking project-archive and .gitignore ===")
    with open(".gitignore", "r", encoding="utf-8") as f:
        gitignore = f.read()

    assert "project-archive" in gitignore, "project-archive not in .gitignore!"
    assert os.path.exists("project-archive"), "project-archive folder missing!"

    archive_files = os.listdir("project-archive")
    print(f"project-archive exists with {len(archive_files)} entries.")
    print("[PASS] Archive is preserved and excluded by .gitignore.")

if __name__ == "__main__":
    verify_tools_and_schemas()
    verify_readme()
    verify_archive()
