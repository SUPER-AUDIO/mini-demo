#!/usr/bin/env python3
"""
Helper script to add new tool configurations to tools_config.json
Usage: python add_tool_config.py
"""

import json
import os
from typing import Dict, Any, List

def load_existing_config() -> Dict[str, Any]:
    """Load existing tools configuration."""
    if os.path.exists("tools_config.json"):
        with open("tools_config.json", "r") as f:
            return json.load(f)
    return {}

def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to tools_config.json."""
    with open("tools_config.json", "w") as f:
        json.dump(config, f, indent=2)
    print("Configuration saved to tools_config.json")

def add_new_tool() -> Dict[str, Any]:
    """Interactive tool to add a new tool configuration."""
    print("\n=== Add New Audio Tool Configuration ===")
    
    # Get basic info
    tool_name = input("Tool name (as registered in @tool decorator): ").strip()
    description = input("Tool description: ").strip()
    
    # Get parameters
    print("\nParameters (press Enter when done):")
    parameters = {}
    while True:
        param_name = input("  Parameter name (or Enter to finish): ").strip()
        if not param_name:
            break
        param_desc = input(f"  Description for '{param_name}': ").strip()
        parameters[param_name] = param_desc
    
    # Get use cases
    print("\nUse cases (enter one per line, press Enter twice when done):")
    use_cases = []
    while True:
        use_case = input("  Use case: ").strip()
        if not use_case:
            break
        use_cases.append(use_case)
    
    # Get examples
    print("\nExamples (enter one per line, press Enter twice when done):")
    examples = []
    while True:
        example = input("  Example: ").strip()
        if not example:
            break
        examples.append(example)
    
    # Create tool config
    tool_config = {
        "name": tool_name,
        "description": description,
        "parameters": parameters,
        "use_cases": use_cases,
        "examples": examples
    }
    
    return tool_name, tool_config

def main():
    """Main function."""
    print("Audio Tool Configuration Manager")
    print("================================")
    
    # Load existing config
    config = load_existing_config()
    
    if config:
        print(f"\nFound existing configuration with {len(config)} tools:")
        for tool_name in config.keys():
            print(f"  - {tool_name}")
    
    while True:
        print("\nOptions:")
        print("1. Add new tool")
        print("2. List existing tools")
        print("3. View tool details")
        print("4. Remove tool")
        print("5. Save and exit")
        print("6. Exit without saving")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            tool_name, tool_config = add_new_tool()
            if tool_name in config:
                overwrite = input(f"Tool '{tool_name}' already exists. Overwrite? (y/n): ")
                if overwrite.lower() != 'y':
                    continue
            config[tool_name] = tool_config
            print(f"✅ Added tool '{tool_name}'")
            
        elif choice == "2":
            if not config:
                print("No tools configured.")
            else:
                print(f"\nConfigured tools ({len(config)}):")
                for tool_name in config.keys():
                    print(f"  - {tool_name}")
                    
        elif choice == "3":
            if not config:
                print("No tools configured.")
                continue
            tool_name = input("Enter tool name to view: ").strip()
            if tool_name in config:
                print(f"\nTool: {tool_name}")
                print(json.dumps(config[tool_name], indent=2))
            else:
                print(f"Tool '{tool_name}' not found.")
                
        elif choice == "4":
            if not config:
                print("No tools configured.")
                continue
            tool_name = input("Enter tool name to remove: ").strip()
            if tool_name in config:
                confirm = input(f"Remove tool '{tool_name}'? (y/n): ")
                if confirm.lower() == 'y':
                    del config[tool_name]
                    print(f"✅ Removed tool '{tool_name}'")
            else:
                print(f"Tool '{tool_name}' not found.")
                
        elif choice == "5":
            save_config(config)
            break
            
        elif choice == "6":
            print("Exiting without saving.")
            break
            
        else:
            print("Invalid choice. Please enter 1-6.")

if __name__ == "__main__":
    main()
