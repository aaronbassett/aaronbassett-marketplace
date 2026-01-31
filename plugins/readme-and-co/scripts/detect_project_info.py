#!/usr/bin/env python3
"""
Detect project information for documentation generation.

Analyzes repository to detect:
- Programming languages
- Package managers
- Frameworks
- Testing tools
- CI/CD setup
- Existing documentation
- Content type (code vs docs vs mixed)

Outputs JSON with detection results.

Usage:
    python detect_project_info.py [--path /path/to/repo]
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Language indicators (filename -> language)
LANGUAGE_INDICATORS = {
    # Python
    'requirements.txt': 'python',
    'setup.py': 'python',
    'pyproject.toml': 'python',
    'Pipfile': 'python',
    '*.py': 'python',

    # JavaScript/TypeScript
    'package.json': 'javascript',
    'package-lock.json': 'javascript',
    'yarn.lock': 'javascript',
    'pnpm-lock.yaml': 'javascript',
    'tsconfig.json': 'typescript',
    '*.ts': 'typescript',
    '*.tsx': 'typescript',
    '*.js': 'javascript',
    '*.jsx': 'javascript',

    # Go
    'go.mod': 'go',
    'go.sum': 'go',
    '*.go': 'go',

    # Rust
    'Cargo.toml': 'rust',
    'Cargo.lock': 'rust',
    '*.rs': 'rust',

    # Ruby
    'Gemfile': 'ruby',
    'Gemfile.lock': 'ruby',
    '*.rb': 'ruby',

    # Java
    'pom.xml': 'java',
    'build.gradle': 'java',
    '*.java': 'java',

    # C/C++
    'CMakeLists.txt': 'c++',
    'Makefile': 'c',
    '*.c': 'c',
    '*.cpp': 'c++',
    '*.h': 'c',
    '*.hpp': 'c++',
}

# Framework indicators
FRAMEWORK_INDICATORS = {
    # Python
    'fastapi': ['fastapi', 'uvicorn'],
    'django': ['django', 'Django'],
    'flask': ['flask', 'Flask'],

    # JavaScript
    'react': ['react', 'React', '"react"'],
    'vue': ['vue', 'Vue', '"vue"'],
    'angular': ['angular', '@angular'],
    'express': ['express', '"express"'],
    'next': ['next', 'Next.js', '"next"'],
    'nuxt': ['nuxt', '"nuxt"'],
}

# Test framework indicators
TEST_INDICATORS = {
    'pytest': ['pytest', 'pytest.ini'],
    'jest': ['jest', 'jest.config'],
    'mocha': ['mocha'],
    'cargo-test': ['#[test]', '#[cfg(test)]'],
    'go-test': ['testing', '*_test.go'],
}

# CI/CD indicators
CI_INDICATORS = {
    'github-actions': ['.github/workflows'],
    'gitlab-ci': ['.gitlab-ci.yml'],
    'travis': ['.travis.yml'],
    'circle-ci': ['.circleci/config.yml'],
}

# Documentation files
DOC_FILES = [
    'README.md', 'README', 'readme.md',
    'LICENSE', 'LICENSE.md', 'LICENSE.txt',
    'CONTRIBUTING.md', 'CONTRIBUTING',
    'CODE_OF_CONDUCT.md', 'CODE_OF_CONDUCT',
    'SECURITY.md', 'SECURITY',
    'SUPPORT.md', 'SUPPORT',
    'GOVERNANCE.md', 'GOVERNANCE',
    'CHANGELOG.md', 'CHANGELOG',
]


def find_files(root: Path, pattern: str, max_depth: int = 3) -> List[Path]:
    """Find files matching pattern up to max_depth."""
    found = []

    if pattern.startswith('*.'):
        # Extension pattern
        ext = pattern[1:]
        for path in root.rglob(f'*{ext}'):
            if len(path.relative_to(root).parts) <= max_depth:
                found.append(path)
    else:
        # Exact filename
        for path in root.rglob(pattern):
            if len(path.relative_to(root).parts) <= max_depth:
                found.append(path)

    return found


def detect_languages(root: Path) -> List[str]:
    """Detect programming languages used in repository."""
    languages = set()

    for indicator, lang in LANGUAGE_INDICATORS.items():
        if indicator.startswith('*.'):
            # Extension-based detection
            if find_files(root, indicator, max_depth=2):
                languages.add(lang)
        else:
            # File-based detection
            if (root / indicator).exists():
                languages.add(lang)

    return sorted(languages)


def detect_package_managers(root: Path) -> List[str]:
    """Detect package managers in use."""
    managers = []

    # Python
    if (root / 'requirements.txt').exists():
        managers.append('pip')
    if (root / 'pyproject.toml').exists():
        managers.append('poetry')
    if (root / 'Pipfile').exists():
        managers.append('pipenv')

    # JavaScript
    if (root / 'package.json').exists():
        if (root / 'package-lock.json').exists():
            managers.append('npm')
        elif (root / 'yarn.lock').exists():
            managers.append('yarn')
        elif (root / 'pnpm-lock.yaml').exists():
            managers.append('pnpm')
        else:
            managers.append('npm')

    # Go
    if (root / 'go.mod').exists():
        managers.append('go modules')

    # Rust
    if (root / 'Cargo.toml').exists():
        managers.append('cargo')

    # Ruby
    if (root / 'Gemfile').exists():
        managers.append('bundler')

    return managers


def detect_frameworks(root: Path) -> List[str]:
    """Detect frameworks in use."""
    frameworks = []

    # Check package.json
    package_json = root / 'package.json'
    if package_json.exists():
        try:
            with open(package_json) as f:
                content = f.read()
                for framework, indicators in FRAMEWORK_INDICATORS.items():
                    if any(ind in content for ind in indicators):
                        frameworks.append(framework)
        except (OSError, UnicodeDecodeError):
            pass

    # Check requirements.txt / pyproject.toml
    for req_file in ['requirements.txt', 'pyproject.toml']:
        req_path = root / req_file
        if req_path.exists():
            try:
                with open(req_path) as f:
                    content = f.read()
                    for framework, indicators in FRAMEWORK_INDICATORS.items():
                        if any(ind in content for ind in indicators):
                            if framework not in frameworks:
                                frameworks.append(framework)
            except (OSError, UnicodeDecodeError):
                pass

    return frameworks


def detect_test_frameworks(root: Path) -> List[str]:
    """Detect testing frameworks in use."""
    tests = []

    for framework, indicators in TEST_INDICATORS.items():
        for indicator in indicators:
            # Check if it's a file pattern
            if '.' in indicator and not indicator.startswith('#'):
                if find_files(root, indicator, max_depth=2):
                    tests.append(framework)
                    break
            # Check in common config files
            else:
                for config_file in ['package.json', 'pyproject.toml', 'Cargo.toml']:
                    config_path = root / config_file
                    if config_path.exists():
                        try:
                            with open(config_path) as f:
                                if indicator in f.read():
                                    tests.append(framework)
                                    break
                        except (OSError, UnicodeDecodeError):
                            pass

    return tests


def detect_ci_cd(root: Path) -> List[str]:
    """Detect CI/CD systems in use."""
    ci_systems = []

    for system, indicators in CI_INDICATORS.items():
        for indicator in indicators:
            path = root / indicator
            if path.exists():
                ci_systems.append(system)
                break

    return ci_systems


def detect_existing_docs(root: Path) -> Dict[str, bool]:
    """Check which documentation files exist."""
    docs = {}

    for doc_file in DOC_FILES:
        docs[doc_file.lower()] = (root / doc_file).exists()

    # Check for GitHub templates
    github_dir = root / '.github'
    docs['issue_templates'] = (github_dir / 'ISSUE_TEMPLATE').exists()
    docs['pr_template'] = (
        (github_dir / 'pull_request_template.md').exists() or
        (github_dir / 'PULL_REQUEST_TEMPLATE').exists()
    )
    docs['codeowners'] = (
        (github_dir / 'CODEOWNERS').exists() or
        (root / 'CODEOWNERS').exists()
    )
    docs['funding'] = (github_dir / 'FUNDING.yml').exists()

    return docs


def detect_content_type(root: Path, languages: List[str]) -> str:
    """Determine if project is code, documentation, or mixed."""
    # Count code files vs documentation files
    code_files = len(find_files(root, '*.py', max_depth=2)) + \
                 len(find_files(root, '*.js', max_depth=2)) + \
                 len(find_files(root, '*.ts', max_depth=2)) + \
                 len(find_files(root, '*.go', max_depth=2)) + \
                 len(find_files(root, '*.rs', max_depth=2))

    doc_files = len(find_files(root, '*.md', max_depth=2)) + \
                len(find_files(root, '*.rst', max_depth=2))

    if code_files == 0 and doc_files > 0:
        return 'documentation'
    elif code_files > 0 and doc_files == 0:
        return 'code'
    elif code_files > doc_files * 3:
        return 'code'
    elif doc_files > code_files * 3:
        return 'documentation'
    else:
        return 'mixed'


def detect_monorepo(root: Path) -> bool:
    """Detect if this is a monorepo structure."""
    # Check for common monorepo indicators
    indicators = [
        'packages',
        'apps',
        'libs',
        'services',
        'lerna.json',
        'nx.json',
        'pnpm-workspace.yaml',
    ]

    for indicator in indicators:
        if (root / indicator).exists():
            return True

    return False


def detect_monorepo_detailed(root: Path) -> Dict:
    """
    Detect monorepo structure with detailed package discovery.

    Returns:
        Dictionary with is_monorepo, type, packages list, and package_count
    """
    result = {
        'is_monorepo': False,
        'type': None,
        'packages': [],
        'package_count': 0
    }

    # Check for monorepo tool config files
    if (root / 'lerna.json').exists():
        result['is_monorepo'] = True
        result['type'] = 'lerna'
    elif (root / 'nx.json').exists():
        result['is_monorepo'] = True
        result['type'] = 'nx'
    elif (root / 'pnpm-workspace.yaml').exists():
        result['is_monorepo'] = True
        result['type'] = 'pnpm-workspaces'
    elif (root / 'package.json').exists():
        # Check for npm/yarn workspaces
        try:
            with open(root / 'package.json') as f:
                data = json.load(f)
                if 'workspaces' in data:
                    result['is_monorepo'] = True
                    result['type'] = 'npm-workspaces'
        except (OSError, json.JSONDecodeError):
            pass

    # If not detected yet, check for common package directories
    if not result['is_monorepo']:
        package_dirs = ['packages', 'apps', 'libs', 'services']
        for dir_name in package_dirs:
            if (root / dir_name).exists() and (root / dir_name).is_dir():
                # Check if it has subdirectories (likely packages)
                subdirs = [p for p in (root / dir_name).iterdir() if p.is_dir() and not p.name.startswith('.')]
                if len(subdirs) >= 2:  # At least 2 packages to be a monorepo
                    result['is_monorepo'] = True
                    result['type'] = 'directory-based'
                    break

    # Discover packages
    if result['is_monorepo']:
        packages = []

        # Try common package directories
        for dir_name in ['packages', 'apps', 'libs', 'services']:
            pkg_dir = root / dir_name
            if pkg_dir.exists() and pkg_dir.is_dir():
                for item in pkg_dir.iterdir():
                    if item.is_dir() and not item.name.startswith('.'):
                        # Check if it looks like a package (has package.json or similar)
                        if (item / 'package.json').exists() or \
                           (item / 'pyproject.toml').exists() or \
                           (item / 'Cargo.toml').exists():
                            packages.append({
                                'name': item.name,
                                'path': str(item.relative_to(root)),
                                'type': dir_name
                            })
                        else:
                            # Include it anyway if it's in a packages directory
                            packages.append({
                                'name': item.name,
                                'path': str(item.relative_to(root)),
                                'type': dir_name
                            })

        result['packages'] = packages
        result['package_count'] = len(packages)

    return result


def get_github_repo_info(root: Path = None) -> Optional[Dict[str, str]]:
    """
    Get GitHub repository information using gh CLI.

    Returns:
        Dictionary with 'owner', 'name', and 'nameWithOwner' keys, or None if not a GitHub repo
    """
    if root is None:
        root = Path.cwd()

    try:
        # Use gh CLI to get repo info
        result = subprocess.run(
            ['gh', 'repo', 'view', '--json', 'nameWithOwner,owner,name'],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=root
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            # Extract owner name from owner object
            owner_name = data.get('owner', {}).get('login', '')
            return {
                'owner': owner_name,
                'name': data.get('name', ''),
                'nameWithOwner': data.get('nameWithOwner', ''),
                'url': f"https://github.com/{data.get('nameWithOwner', '')}"
            }
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass

    return None


def generate_badges(project_info: Dict, config: Optional[Dict] = None) -> str:
    """
    Generate shields.io badge markdown based on project info and config.

    Args:
        project_info: Project information from analyze_repository()
        config: Configuration from .claude/readme-and-co.local.md

    Returns:
        Markdown string with badges
    """
    if config is None:
        config = {}

    # Check if badges are enabled
    badge_config = config.get('badges', {})
    if not badge_config.get('enabled', True):
        return ''

    # Get badge style
    style = badge_config.get('style', 'flat-square')

    # Determine which badges to include
    include = badge_config.get('include', ['license', 'ci-status', 'language-version'])

    badges = []
    github_repo = project_info.get('github_repo')
    nameWithOwner = github_repo.get('nameWithOwner') if github_repo else None

    # License badge
    if 'license' in include and 'license' in config.get('defaults', {}):
        license_name = config['defaults']['license']
        license_encoded = license_name.replace('-', '--')
        badges.append(
            f"[![License](https://img.shields.io/badge/license-{license_encoded}-blue.svg?style={style})](LICENSE)"
        )

    # CI/CD status badge
    if 'ci-status' in include and nameWithOwner and 'github-actions' in project_info.get('ci_cd', []):
        badges.append(
            f"[![CI](https://img.shields.io/github/actions/workflow/status/{nameWithOwner}/ci.yml?style={style})](https://github.com/{nameWithOwner}/actions)"
        )

    # Language version badges
    if 'language-version' in include:
        primary_lang = project_info.get('primary_language')

        if primary_lang == 'python':
            badges.append(
                f"[![Python](https://img.shields.io/badge/python-3.8+-blue.svg?style={style})](https://www.python.org/)"
            )
        elif primary_lang == 'javascript' or primary_lang == 'typescript':
            badges.append(
                f"[![Node](https://img.shields.io/badge/node-%3E%3D18-green.svg?style={style})](https://nodejs.org/)"
            )
        elif primary_lang == 'rust':
            badges.append(
                f"[![Rust](https://img.shields.io/badge/rust-1.70+-orange.svg?style={style})](https://www.rust-lang.org/)"
            )
        elif primary_lang == 'go':
            badges.append(
                f"[![Go](https://img.shields.io/badge/go-1.20+-00ADD8.svg?style={style})](https://golang.org/)"
            )

    # NPM version badge
    if 'npm-version' in include and nameWithOwner and 'javascript' in project_info.get('languages', []):
        # Extract package name from nameWithOwner
        pkg_name = nameWithOwner.split('/')[-1]
        badges.append(
            f"[![npm](https://img.shields.io/npm/v/{pkg_name}?style={style})](https://www.npmjs.com/package/{pkg_name})"
        )

    # Build badges into single line
    if badges:
        return '\n'.join(badges) + '\n'

    return ''


def analyze_repository(path: Optional[str] = None, include_badges: bool = True) -> Dict:
    """Analyze repository and return structured information."""
    root = Path(path) if path else Path.cwd()

    if not root.exists():
        return {'error': f'Path does not exist: {root}'}

    languages = detect_languages(root)

    # Get GitHub repo info if available
    github_info = get_github_repo_info(root)

    # Get detailed monorepo info
    monorepo_info = detect_monorepo_detailed(root)

    result = {
        'languages': languages,
        'package_managers': detect_package_managers(root),
        'frameworks': detect_frameworks(root),
        'test_frameworks': detect_test_frameworks(root),
        'ci_cd': detect_ci_cd(root),
        'existing_docs': detect_existing_docs(root),
        'content_type': detect_content_type(root, languages),
        'is_monorepo': monorepo_info['is_monorepo'],
        'monorepo': monorepo_info if monorepo_info['is_monorepo'] else None,
        'primary_language': languages[0] if languages else None,
        'github_repo': github_info,
    }

    # Generate badges if requested
    if include_badges:
        # Try to load local config for badge settings
        try:
            from yaml_parser import load_config_file
            config_path = root / ".claude" / "readme-and-co.local.md"
            if config_path.exists():
                config = load_config_file(str(config_path))
            else:
                config = {}
        except (ImportError, Exception):
            config = {}

        badges = generate_badges(result, config)
        if badges:
            result['badges'] = badges

    return result


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Detect project information for documentation generation'
    )
    parser.add_argument(
        '--path',
        default=None,
        help='Path to repository (default: current directory)'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty-print JSON output'
    )

    args = parser.parse_args()

    result = analyze_repository(args.path)

    if args.pretty:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))

    return 0 if 'error' not in result else 1


if __name__ == '__main__':
    sys.exit(main())
