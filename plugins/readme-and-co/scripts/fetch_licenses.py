#!/usr/bin/env python3
"""
Fetch license templates from external sources.

Downloads:
- All 13 GitHub-approved licenses from GitHub API
- All 7 Creative Commons licenses from creativecommons.org
- FSL-1.1-MIT from fsl.software

Stores in templates/LICENSE/ directory with proper organization.

This script should be run:
- During plugin setup (first time)
- Manually when user wants to refresh licenses
- NOT automatically on every use (licenses rarely change)

Usage:
    python fetch_licenses.py [--plugin-root /path/to/plugin]
    python fetch_licenses.py --dry-run  # Show what would be fetched
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional


# GitHub licenses to fetch
GITHUB_LICENSES = [
    'agpl-3.0',
    'apache-2.0',
    'bsd-2-clause',
    'bsd-3-clause',
    'bsl-1.0',
    'cc0-1.0',
    'epl-2.0',
    'gpl-2.0',
    'gpl-3.0',
    'lgpl-2.1',
    'mit',
    'mpl-2.0',
    'unlicense',
]

# Creative Commons licenses to fetch
CC_LICENSES = [
    ('CC-BY-4.0', 'https://creativecommons.org/licenses/by/4.0/legalcode.txt'),
    ('CC-BY-SA-4.0', 'https://creativecommons.org/licenses/by-sa/4.0/legalcode.txt'),
    ('CC-BY-NC-4.0', 'https://creativecommons.org/licenses/by-nc/4.0/legalcode.txt'),
    ('CC-BY-NC-SA-4.0', 'https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.txt'),
    ('CC-BY-ND-4.0', 'https://creativecommons.org/licenses/by-nd/4.0/legalcode.txt'),
    ('CC-BY-NC-ND-4.0', 'https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode.txt'),
    ('CC0-1.0', 'https://creativecommons.org/publicdomain/zero/1.0/legalcode.txt'),
]

# FSL license
FSL_URL = 'https://fsl.software/FSL-1.1-MIT.template.md'


def fetch_url(url: str, timeout: int = 10) -> Optional[str]:
    """Fetch content from URL."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.read().decode('utf-8')
    except urllib.error.URLError as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error fetching {url}: {e}", file=sys.stderr)
        return None


def fetch_github_license(license_key: str) -> Optional[Dict]:
    """
    Fetch license from GitHub API.

    Returns dict with 'body' (license text) and 'spdx_id'.
    """
    url = f'https://api.github.com/licenses/{license_key}'
    content = fetch_url(url)

    if not content:
        return None

    try:
        data = json.loads(content)
        return {
            'body': data.get('body', ''),
            'spdx_id': data.get('spdx_id', license_key.upper()),
            'name': data.get('name', ''),
        }
    except json.JSONDecodeError:
        print(f"Error parsing JSON for {license_key}", file=sys.stderr)
        return None


def fetch_cc_license(name: str, url: str) -> Optional[str]:
    """Fetch Creative Commons license text."""
    return fetch_url(url)


def fetch_fsl_license() -> Optional[str]:
    """Fetch FSL-1.1-MIT license."""
    return fetch_url(FSL_URL)


def save_license(content: str, path: Path, dry_run: bool = False):
    """Save license content to file."""
    if dry_run:
        print(f"Would save to: {path}")
        return

    # Create parent directory
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Saved: {path}")


def fetch_all_licenses(plugin_root: Path, dry_run: bool = False) -> Dict[str, int]:
    """
    Fetch all licenses and save to templates directory.

    Returns dict with counts: {'github': N, 'cc': N, 'fsl': N, 'failed': N}
    """
    templates_dir = plugin_root / 'templates' / 'LICENSE'
    counts = {'github': 0, 'cc': 0, 'fsl': 0, 'failed': 0}

    # Fetch GitHub licenses
    print("Fetching GitHub licenses...")
    github_dir = templates_dir / 'github'

    for license_key in GITHUB_LICENSES:
        print(f"  Fetching {license_key}...")
        license_data = fetch_github_license(license_key)

        if license_data and license_data['body']:
            # Save with SPDX ID as filename
            spdx_id = license_data['spdx_id']
            filename = f"{spdx_id}.template.txt"
            path = github_dir / filename

            save_license(license_data['body'], path, dry_run)
            counts['github'] += 1
        else:
            print(f"  Failed to fetch {license_key}", file=sys.stderr)
            counts['failed'] += 1

    # Fetch Creative Commons licenses
    print("\nFetching Creative Commons licenses...")
    cc_dir = templates_dir / 'creative-commons'

    for name, url in CC_LICENSES:
        print(f"  Fetching {name}...")
        content = fetch_cc_license(name, url)

        if content:
            filename = f"{name}.template.txt"
            path = cc_dir / filename

            save_license(content, path, dry_run)
            counts['cc'] += 1
        else:
            print(f"  Failed to fetch {name}", file=sys.stderr)
            counts['failed'] += 1

    # Fetch FSL license
    print("\nFetching FSL-1.1-MIT license...")
    fsl_dir = templates_dir / 'fsl'

    content = fetch_fsl_license()
    if content:
        path = fsl_dir / 'FSL-1.1-MIT.template.md'
        save_license(content, path, dry_run)
        counts['fsl'] += 1
    else:
        print("  Failed to fetch FSL-1.1-MIT", file=sys.stderr)
        counts['failed'] += 1

    return counts


def create_metadata_file(plugin_root: Path, dry_run: bool = False):
    """Create metadata.json with license information."""
    # This would be a large file with license metadata
    # For now, create a minimal version

    metadata = {
        "github": {
            "MIT": {
                "spdx_id": "MIT",
                "category": "permissive",
                "osi_approved": True,
                "description": "Permissive license with minimal restrictions"
            },
            "Apache-2.0": {
                "spdx_id": "Apache-2.0",
                "category": "permissive",
                "osi_approved": True,
                "description": "Permissive license with patent grant"
            },
            # Add more as needed...
        },
        "creative_commons": {
            "CC-BY-4.0": {
                "spdx_id": "CC-BY-4.0",
                "category": "creative-commons",
                "osi_approved": False,
                "description": "Creative Commons Attribution"
            },
            # Add more as needed...
        },
        "fsl": {
            "FSL-1.1-MIT": {
                "spdx_id": None,
                "category": "time-delayed-open-source",
                "osi_approved": False,
                "description": "Functional Source License with automatic MIT transition after 2 years"
            }
        }
    }

    path = plugin_root / 'templates' / 'LICENSE' / 'metadata.json'

    if dry_run:
        print(f"Would create metadata at: {path}")
        return

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"Created metadata: {path}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Fetch license templates from external sources'
    )

    parser.add_argument(
        '--plugin-root',
        type=str,
        help='Plugin root directory (default: computed from script location)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be fetched without actually fetching'
    )

    args = parser.parse_args()

    # Determine plugin root
    if args.plugin_root:
        plugin_root = Path(args.plugin_root)
    else:
        plugin_root = Path(__file__).parent.parent

    if not plugin_root.exists():
        print(f"Error: Plugin root does not exist: {plugin_root}", file=sys.stderr)
        return 1

    print(f"Plugin root: {plugin_root}")
    print(f"Dry run: {args.dry_run}\n")

    # Fetch licenses
    counts = fetch_all_licenses(plugin_root, args.dry_run)

    # Create metadata
    create_metadata_file(plugin_root, args.dry_run)

    # Summary
    print("\n" + "="*50)
    print("Summary:")
    print(f"  GitHub licenses: {counts['github']}/{len(GITHUB_LICENSES)}")
    print(f"  Creative Commons licenses: {counts['cc']}/{len(CC_LICENSES)}")
    print(f"  FSL licenses: {counts['fsl']}/1")
    print(f"  Failed: {counts['failed']}")

    total_expected = len(GITHUB_LICENSES) + len(CC_LICENSES) + 1
    total_fetched = counts['github'] + counts['cc'] + counts['fsl']
    print(f"\nTotal: {total_fetched}/{total_expected} licenses fetched")

    if counts['failed'] > 0:
        print(f"\n⚠ Warning: {counts['failed']} licenses failed to fetch", file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
