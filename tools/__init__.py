"""
SuperAudio Mini Tools Package

This package contains all audio processing tools for the SuperAudio Mini system.
Each tool is implemented in its own module for better organization and maintainability.

To add a new tool:
1. Create a new .py file in this directory
2. Import the necessary types and decorator from api
3. Define your function with the @tool() decorator
4. The tool will be automatically discovered and registered
"""

import os
import importlib.util
import sys
from pathlib import Path

def discover_and_load_tools():
    """
    Automatically discover and load all tools in the tools directory.
    
    This function:
    1. Scans the tools directory for .py files
    2. Dynamically imports each module
    3. Tools with @tool decorators are automatically registered
    """
    tools_dir = Path(__file__).parent
    loaded_tools = []
    
    # Get all .py files in the tools directory (except __init__.py and the template)
    tool_files = [
        f for f in tools_dir.glob("*.py")
        if f.name not in ("__init__.py", "tool_template.py")
    ]
    
    for tool_file in tool_files:
        try:
            # Create module name from filename
            module_name = f"tools.{tool_file.stem}"
            
            # Load the module
            spec = importlib.util.spec_from_file_location(module_name, tool_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                
                # Add to sys.modules so relative imports work
                sys.modules[module_name] = module
                
                # Execute the module (this will trigger @tool decorators)
                spec.loader.exec_module(module)
                
                loaded_tools.append(tool_file.stem)
                print(f"✅ Loaded tool: {tool_file.stem}")
                
        except Exception as e:
            print(f"❌ Error loading tool {tool_file.stem}: {e}")
    
    if loaded_tools:
        print(f"📦 Successfully loaded {len(loaded_tools)} tools: {', '.join(loaded_tools)}")
    else:
        print("⚠️ No tools were loaded")
    
    return loaded_tools

# Automatically load all tools when this package is imported
print("🔍 Discovering audio processing tools...")
discover_and_load_tools()
