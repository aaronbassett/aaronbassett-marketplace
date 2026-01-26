#!/usr/bin/env python3
"""
Simple YAML frontmatter parser with no external dependencies.

Supports basic YAML structures:
- Strings (quoted and unquoted)
- Numbers (integers and floats)
- Booleans (true/false)
- Lists (- item syntax)
- Dictionaries (key: value with indentation)

Does NOT support:
- Anchors and aliases
- Multi-line strings with | or >
- Complex nested structures beyond 2-3 levels
- YAML 1.2 advanced features

This is intentionally simple to avoid external dependencies.
"""

import re
from typing import Any, Dict, Optional


def parse_yaml_value(value: str) -> Any:
    """
    Parse a YAML value to Python type.

    Args:
        value: String value to parse

    Returns:
        Parsed value (str, int, float, bool, or None)
    """
    value = value.strip()

    # Handle quoted strings
    if (value.startswith('"') and value.endswith('"')) or \
       (value.startswith("'") and value.endswith("'")):
        return value[1:-1]

    # Handle booleans
    if value.lower() in ('true', 'yes', 'on'):
        return True
    if value.lower() in ('false', 'no', 'off'):
        return False

    # Handle null/none
    if value.lower() in ('null', 'none', '~', ''):
        return None

    # Handle numbers
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        pass

    # Return as string
    return value


def parse_simple_yaml(yaml_content: str) -> Dict[str, Any]:
    """
    Parse simple YAML content to dictionary.

    Supports:
    - key: value pairs
    - nested dictionaries with indentation
    - lists with - syntax
    - basic types (str, int, float, bool)

    Args:
        yaml_content: YAML string to parse

    Returns:
        Dictionary of parsed values
    """
    result = {}
    lines = yaml_content.split('\n')

    # Pre-process to identify list parents
    list_parent_keys = set()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('- ') and i > 0:
            # Find the parent key
            prev_line = lines[i - 1].strip()
            if ':' in prev_line and not prev_line.split(':', 1)[1].strip():
                key = prev_line.split(':', 1)[0].strip()
                list_parent_keys.add(key)

    current_dict = result
    dict_stack = [result]
    current_list_key = None
    current_indent = 0

    for line in lines:
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith('#'):
            continue

        # Calculate indentation
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        # Handle list items
        if stripped.startswith('- '):
            if current_list_key:
                item_value = stripped[2:].strip()
                parsed_value = parse_yaml_value(item_value)

                # Get the list to append to
                target = dict_stack[-1]
                if current_list_key not in target:
                    target[current_list_key] = []

                if not isinstance(target[current_list_key], list):
                    target[current_list_key] = [target[current_list_key]]

                target[current_list_key].append(parsed_value)
            continue

        # Handle key-value pairs
        if ':' in stripped:
            # Split on first colon only
            parts = stripped.split(':', 1)
            key = parts[0].strip()
            value = parts[1].strip() if len(parts) > 1 else ''

            # Adjust stack based on indentation
            if indent < current_indent:
                # Pop back to appropriate level
                levels_to_pop = (current_indent - indent) // 2
                for _ in range(levels_to_pop):
                    if len(dict_stack) > 1:
                        dict_stack.pop()

            current_indent = indent
            current_dict = dict_stack[-1]

            # Check if this is a list parent
            if key in list_parent_keys and not value:
                # This key will contain a list
                current_dict[key] = []
                current_list_key = key
            elif not value:
                # This key will contain a nested dict
                current_dict[key] = {}
                dict_stack.append(current_dict[key])
                current_list_key = None
            else:
                # Regular key-value pair
                current_dict[key] = parse_yaml_value(value)
                current_list_key = None

    return result


def extract_yaml_frontmatter(content: str) -> Optional[Dict[str, Any]]:
    """
    Extract and parse YAML frontmatter from content.

    Frontmatter must be at the start of the file between --- markers:
    ---
    key: value
    ---

    Args:
        content: File content with potential frontmatter

    Returns:
        Dictionary of parsed frontmatter, or None if no frontmatter found
    """
    # Check for frontmatter at start
    if not content.startswith('---'):
        return None

    # Find the closing ---
    # Split on newline to handle properly
    lines = content.split('\n')

    # Skip first --- line
    yaml_lines = []
    found_closing = False

    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            found_closing = True
            break
        yaml_lines.append(line)

    if not found_closing:
        return None

    # Parse the YAML content
    yaml_content = '\n'.join(yaml_lines)

    try:
        return parse_simple_yaml(yaml_content)
    except Exception:
        # If parsing fails, return None rather than crashing
        return None


def load_config_file(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a .md file with YAML frontmatter.

    Args:
        config_path: Path to config file

    Returns:
        Dictionary of configuration values (empty if file not found or invalid)
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()

        config = extract_yaml_frontmatter(content)
        return config if config is not None else {}

    except (OSError, UnicodeDecodeError):
        return {}


if __name__ == '__main__':
    # Simple test
    test_yaml = """---
defaults:
  license: MIT
  author_name: Test User
badges:
  enabled: true
  style: flat-square
  include:
    - license
    - ci-status
---
# Config file
"""

    result = extract_yaml_frontmatter(test_yaml)
    print("Parsed YAML:")
    print(result)
