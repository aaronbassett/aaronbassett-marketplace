#!/usr/bin/env python3
"""
Render templates with variable substitution.

Simple template engine using {{variable}} syntax.
Supports:
- Variable substitution: {{variable_name}}
- Missing variable handling: Shows warning, uses placeholder
- Template validation: Detects unused and missing variables
- Dry-run mode: Validate without rendering
- Local config: Load defaults from .claude/readme-and-co.local.md

Does NOT support (per requirements):
- Conditionals
- Loops
- Filters
- Complex logic

Configuration:
    Create .claude/readme-and-co.local.md with YAML frontmatter:
    ---
    defaults:
      project_name: MyProject
      author_name: John Doe
      license: MIT
    ---

    CLI variables override config defaults.

Usage:
    # Render template
    python render_template.py --template path/to/template.md --vars '{"name":"value"}' [--output path/to/output.md]

    # Preview mode (output to stdout)
    python render_template.py --template path/to/template.md --vars '{"name":"value"}' --preview

    # Validate without rendering (dry-run)
    python render_template.py --template path/to/template.md --vars '{"name":"value"}' --validate

    # Treat warnings as errors
    python render_template.py --template path/to/template.md --vars '{}' --warnings-as-errors
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Import local YAML parser
try:
    from yaml_parser import load_config_file
except ImportError:
    # If running from different directory, try absolute import
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from yaml_parser import load_config_file


def find_template_variables(content: str) -> set[str]:
    """
    Find all {{variable}} placeholders in template content.

    Args:
        content: Template content with {{placeholders}}

    Returns:
        Set of variable names found in template
    """
    pattern = r'\{\{([^}]+)\}\}'
    matches = re.findall(pattern, content)
    return {match.strip() for match in matches}


def substitute_variables(content: str, variables: Dict[str, str]) -> tuple[str, List[str]]:
    """
    Replace {{variable}} placeholders with values.

    Args:
        content: Template content with {{placeholders}}
        variables: Dictionary of variable_name -> value

    Returns:
        Tuple of (rendered_content, list_of_warnings)
    """
    warnings = []

    # Find all {{variable}} patterns
    pattern = r'\{\{([^}]+)\}\}'

    def replace_var(match):
        var_name = match.group(1).strip()

        if var_name in variables:
            return str(variables[var_name])
        else:
            # Missing variable - use placeholder and warn
            warnings.append(f"Missing variable: {var_name}")
            return f"[MISSING: {var_name}]"

    rendered = re.sub(pattern, replace_var, content)

    return rendered, warnings


def validate_template(content: str, variables: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Validate template and variables without rendering.

    Args:
        content: Template content with {{placeholders}}
        variables: Dictionary of variable_name -> value

    Returns:
        Dictionary with 'errors', 'warnings', and 'info' lists
    """
    validation = {
        'errors': [],
        'warnings': [],
        'info': []
    }

    # Find all variables in template
    template_vars = find_template_variables(content)
    provided_vars = set(variables.keys())

    # Check for missing variables (required but not provided)
    missing_vars = template_vars - provided_vars
    if missing_vars:
        validation['errors'].extend(
            f"Missing required variable: '{var}'" for var in sorted(missing_vars)
        )

    # Check for unused variables (provided but not used)
    unused_vars = provided_vars - template_vars
    if unused_vars:
        validation['warnings'].extend(
            f"Unused variable provided: '{var}'" for var in sorted(unused_vars)
        )

    # Info messages
    if template_vars:
        validation['info'].append(
            f"Template uses {len(template_vars)} variable(s): {', '.join(sorted(template_vars))}"
        )
    else:
        validation['info'].append("Template contains no variables")

    if provided_vars:
        validation['info'].append(
            f"Provided {len(provided_vars)} variable(s): {', '.join(sorted(provided_vars))}"
        )
    else:
        validation['info'].append("No variables provided")

    return validation


def read_template(template_path: Path) -> str:
    """Read template file content."""
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_output(content: str, output_path: Optional[Path] = None):
    """Write rendered content to file or stdout."""
    if output_path:
        # Create parent directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        # Write to stdout
        print(content)


def render_template(
    template_path: Optional[Path] = None,
    variables: Dict[str, str] = None,
    output_path: Optional[Path] = None,
    validate_only: bool = False
) -> tuple[str, List[str], Optional[Dict[str, List[str]]]]:
    """
    Main rendering function.

    Args:
        template_path: Path to single template file
        variables: Dictionary of variables for substitution
        output_path: Where to write output (None = stdout)
        validate_only: If True, only validate without rendering or writing output

    Returns:
        Tuple of (rendered_content, list_of_warnings, validation_results)
        - rendered_content: Empty string if validate_only=True
        - list_of_warnings: Warnings from substitution (empty if validate_only=True)
        - validation_results: Dict with errors/warnings/info (None if validate_only=False)
    """
    if variables is None:
        variables = {}

    # Get content from template
    if template_path:
        content = read_template(template_path)
    else:
        raise ValueError("Must provide template_path")

    # Validation mode - check template without rendering
    if validate_only:
        validation = validate_template(content, variables)
        return '', [], validation

    # Normal rendering mode
    rendered, warnings = substitute_variables(content, variables)

    # Write output
    write_output(rendered, output_path)

    return rendered, warnings, None


def load_local_config(project_root: Optional[Path] = None) -> Dict[str, str]:
    """
    Load configuration from .claude/readme-and-co.local.md.

    Args:
        project_root: Project root directory (default: current directory)

    Returns:
        Dictionary of configuration values from 'defaults' section
    """
    if project_root is None:
        project_root = Path.cwd()

    config_path = project_root / ".claude" / "readme-and-co.local.md"

    if not config_path.exists():
        return {}

    # Load config file with YAML frontmatter
    config = load_config_file(str(config_path))

    # Extract defaults section if it exists
    if 'defaults' in config and isinstance(config['defaults'], dict):
        return config['defaults']

    return {}


def parse_variables(vars_json: str) -> Dict[str, str]:
    """Parse variables from JSON string."""
    if not vars_json or vars_json.strip() == '':
        return {}

    try:
        variables = json.loads(vars_json)
        if not isinstance(variables, dict):
            raise ValueError("Variables must be a JSON object/dict")
        return variables
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON for variables: {e}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Render templates with variable substitution'
    )

    # Template input
    parser.add_argument(
        '--template',
        type=str,
        required=True,
        help='Path to template file'
    )

    # Variables
    parser.add_argument(
        '--vars',
        type=str,
        default='{}',
        help='JSON string of variables (default: "{}")'
    )

    # Output
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file path (default: stdout)'
    )

    # Validation and error handling
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate template and variables without rendering (dry-run mode)'
    )

    parser.add_argument(
        '--warnings-as-errors',
        action='store_true',
        help='Treat missing variables as errors (exit code 1)'
    )

    parser.add_argument(
        '--preview',
        action='store_true',
        help='Preview mode: output to stdout instead of file (ignores --output)'
    )

    args = parser.parse_args()

    try:
        # Load local config for defaults
        config_defaults = load_local_config()

        # Parse CLI variables
        cli_variables = parse_variables(args.vars)

        # Merge: config defaults < CLI args (CLI overrides config)
        variables = {**config_defaults, **cli_variables}

        # Log if config was loaded
        if config_defaults:
            print(f"Loaded {len(config_defaults)} default(s) from .claude/readme-and-co.local.md", file=sys.stderr)

        # Prepare paths
        template_path = Path(args.template) if args.template else None
        output_path = Path(args.output) if args.output else None

        # Handle preview mode
        if args.preview:
            print("Preview mode: output to stdout", file=sys.stderr)
            output_path = None

        # Render or validate
        rendered, warnings, validation = render_template(
            template_path=template_path,
            variables=variables,
            output_path=output_path,
            validate_only=args.validate
        )

        # Handle validation mode
        if args.validate:
            print("=== Template Validation ===", file=sys.stderr)
            print(file=sys.stderr)

            # Show info messages
            if validation['info']:
                for info in validation['info']:
                    print(f"ℹ️  {info}", file=sys.stderr)
                print(file=sys.stderr)

            # Show warnings
            if validation['warnings']:
                print("⚠️  Warnings:", file=sys.stderr)
                for warning in validation['warnings']:
                    print(f"  - {warning}", file=sys.stderr)
                print(file=sys.stderr)

            # Show errors
            if validation['errors']:
                print("❌ Errors:", file=sys.stderr)
                for error in validation['errors']:
                    print(f"  - {error}", file=sys.stderr)
                print(file=sys.stderr)
                print("Validation failed: template has missing required variables", file=sys.stderr)
                return 1

            # Success
            if not validation['warnings']:
                print("✅ Validation passed: template is ready to render", file=sys.stderr)
            else:
                print("✅ Validation passed with warnings", file=sys.stderr)
                if args.warnings_as_errors:
                    return 1

            return 0

        # Handle normal rendering mode
        if warnings:
            for warning in warnings:
                print(f"Warning: {warning}", file=sys.stderr)

            if args.warnings_as_errors:
                return 1

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
