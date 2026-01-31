#!/usr/bin/env python3
"""
Populate license templates with project-specific variables.

Handles variable substitution for license files with smart defaults from:
- Git config (user.name, user.email)
- package.json (name, author)
- Current year

Usage:
    python populate_license.py --license MIT --holder "Jane Doe" --year 2026 --output LICENSE
    python populate_license.py --license FSL-1.1-MIT --holder "MyCompany Inc" --output LICENSE.md
    python populate_license.py --license Apache-2.0 --auto-detect --output LICENSE
    python populate_license.py --license MIT --auto-detect --preview
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


def get_git_config(key: str) -> Optional[str]:
    """Get value from git config."""
    try:
        result = subprocess.run(
            ['git', 'config', '--get', key],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def get_package_json_info(root: Path = None) -> Dict[str, str]:
    """Extract information from package.json if it exists."""
    if root is None:
        root = Path.cwd()

    package_json = root / 'package.json'
    if not package_json.exists():
        return {}

    try:
        with open(package_json, 'r') as f:
            data = json.load(f)

        info = {}

        # Project name
        if 'name' in data:
            info['project_name'] = data['name']

        # Author
        if 'author' in data:
            if isinstance(data['author'], str):
                info['author_name'] = data['author']
            elif isinstance(data['author'], dict):
                if 'name' in data['author']:
                    info['author_name'] = data['author']['name']
                if 'email' in data['author']:
                    info['author_email'] = data['author']['email']

        return info
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}


def get_smart_defaults() -> Dict[str, str]:
    """Get smart defaults from git config and package.json."""
    defaults = {}

    # Current year
    defaults['year'] = str(datetime.now().year)

    # Git config
    git_name = get_git_config('user.name')
    if git_name:
        defaults['author_name'] = git_name
        defaults['copyright_holder'] = git_name
        defaults['licensor_name'] = git_name

    git_email = get_git_config('user.email')
    if git_email:
        defaults['author_email'] = git_email

    # package.json
    pkg_info = get_package_json_info()
    if pkg_info:
        # Package.json takes precedence over git config for project-specific info
        defaults.update(pkg_info)

    return defaults


def normalize_license_name(license_name: str) -> str:
    """Normalize license name to match template filename."""
    # Convert to uppercase, handle common variations
    normalized = license_name.upper()

    # Map common aliases
    aliases = {
        'MIT': 'MIT',
        'APACHE': 'Apache-2.0',
        'APACHE-2': 'Apache-2.0',
        'APACHE2': 'Apache-2.0',
        'GPL': 'GPL-3.0',
        'GPL-3': 'GPL-3.0',
        'GPL3': 'GPL-3.0',
        'AGPL': 'AGPL-3.0',
        'AGPL-3': 'AGPL-3.0',
        'BSD': 'BSD-3-Clause',
        'BSD-3': 'BSD-3-Clause',
        'FSL': 'FSL-1.1-MIT',
        'FSL-MIT': 'FSL-1.1-MIT',
    }

    return aliases.get(normalized, license_name)


def find_license_template(license_name: str, plugin_root: Path) -> Optional[Path]:
    """Find license template file."""
    templates_dir = plugin_root / 'templates' / 'LICENSE'

    # Try github/ directory first (most common)
    github_path = templates_dir / 'github' / f'{license_name}.template.txt'
    if github_path.exists():
        return github_path

    # Try fsl/ directory
    fsl_path = templates_dir / 'fsl' / f'{license_name}.template.md'
    if fsl_path.exists():
        return fsl_path

    # Try creative-commons/ directory
    cc_path = templates_dir / 'creative-commons' / f'{license_name}.template.txt'
    if cc_path.exists():
        return cc_path

    # Try root templates/LICENSE/ directory
    root_path = templates_dir / f'{license_name}.template.txt'
    if root_path.exists():
        return root_path

    root_md_path = templates_dir / f'{license_name}.template.md'
    if root_md_path.exists():
        return root_md_path

    return None


def substitute_license_variables(content: str, variables: Dict[str, str]) -> str:
    """
    Substitute variables in license template.

    Supports ${variable}, {{variable}}, and [variable] syntax.
    """
    import re

    # Map common GitHub template variables to our variable names
    variable_mappings = {
        'year': variables.get('year', ''),
        'fullname': variables.get('copyright_holder', variables.get('licensor_name', variables.get('author_name', ''))),
        'project': variables.get('project_name', ''),
        'email': variables.get('author_email', ''),
    }

    # Also include all original variables
    all_vars = {**variable_mappings, **variables}

    # First try [variable] syntax (GitHub API format)
    def replace_bracket(match):
        var_name = match.group(1)
        return all_vars.get(var_name, match.group(0))

    content = re.sub(r'\[([^\]]+)\]', replace_bracket, content)

    # Then try ${variable} syntax (common in other templates)
    def replace_dollar(match):
        var_name = match.group(1)
        return all_vars.get(var_name, match.group(0))

    content = re.sub(r'\$\{([^}]+)\}', replace_dollar, content)

    # Then try {{variable}} syntax
    def replace_brace(match):
        var_name = match.group(1).strip()
        return all_vars.get(var_name, match.group(0))

    content = re.sub(r'\{\{([^}]+)\}\}', replace_brace, content)

    return content


def populate_license(
    license_name: str,
    holder: Optional[str] = None,
    year: Optional[str] = None,
    organization: Optional[str] = None,
    auto_detect: bool = False,
    plugin_root: Optional[Path] = None,
    output_path: Optional[Path] = None
) -> str:
    """
    Populate license template with variables.

    Args:
        license_name: License identifier (MIT, Apache-2.0, etc.)
        holder: Copyright holder name
        year: Copyright year
        organization: Organization name (for some licenses)
        auto_detect: Use smart defaults from git/package.json
        plugin_root: Plugin root directory
        output_path: Where to write output

    Returns:
        Rendered license text
    """
    # Determine plugin root
    if plugin_root is None:
        plugin_root = Path(__file__).parent.parent

    # Normalize license name
    license_name = normalize_license_name(license_name)

    # Find template
    template_path = find_license_template(license_name, plugin_root)
    if not template_path:
        raise FileNotFoundError(f"License template not found for: {license_name}")

    # Read template
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()

    # Build variables dictionary
    variables = {}

    if auto_detect:
        variables.update(get_smart_defaults())

    # Override with explicit values
    if year:
        variables['year'] = year
    if holder:
        variables['copyright_holder'] = holder
        variables['licensor_name'] = holder  # For FSL
        variables['author_name'] = holder
    if organization:
        variables['organization'] = organization

    # Ensure year is set
    if 'year' not in variables:
        variables['year'] = str(datetime.now().year)

    # Substitute variables
    rendered = substitute_license_variables(template_content, variables)

    # Write output
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered)
    else:
        print(rendered)

    return rendered


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Populate license templates with project-specific variables'
    )

    parser.add_argument(
        '--license',
        required=True,
        help='License name (MIT, Apache-2.0, GPL-3.0, FSL-1.1-MIT, etc.)'
    )

    parser.add_argument(
        '--holder',
        help='Copyright holder name'
    )

    parser.add_argument(
        '--year',
        help='Copyright year (default: current year)'
    )

    parser.add_argument(
        '--organization',
        help='Organization name (for some licenses)'
    )

    parser.add_argument(
        '--auto-detect',
        action='store_true',
        help='Auto-detect holder and year from git config and package.json'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (default: stdout)'
    )

    parser.add_argument(
        '--plugin-root',
        type=str,
        help='Plugin root directory (default: computed from script location)'
    )

    parser.add_argument(
        '--preview',
        action='store_true',
        help='Preview mode: output to stdout instead of file (ignores --output)'
    )

    args = parser.parse_args()

    try:
        plugin_root = Path(args.plugin_root) if args.plugin_root else None
        output_path = Path(args.output) if args.output else None

        # Handle preview mode
        if args.preview:
            print("Preview mode: output to stdout", file=sys.stderr)
            output_path = None

        rendered = populate_license(
            license_name=args.license,
            holder=args.holder,
            year=args.year,
            organization=args.organization,
            auto_detect=args.auto_detect,
            plugin_root=plugin_root,
            output_path=output_path
        )

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
