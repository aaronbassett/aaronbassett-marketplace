#!/usr/bin/env python3
"""
Template Validation Script for readme-and-co Plugin

Validates that all expected templates exist and are correctly formatted.
Returns structured output of available templates for agent operations.

Usage:
    python validate_templates.py [--json] [--verbose]

Options:
    --json      Output results as JSON
    --verbose   Show detailed validation information
    --check     Exit with non-zero code if validation fails (CI mode)
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class TemplateValidator:
    """Validates readme-and-co plugin templates."""

    def __init__(self, plugin_root: Optional[Path] = None):
        """
        Initialize validator.

        Args:
            plugin_root: Path to plugin root directory.
                        If None, auto-detects from script location.
        """
        if plugin_root is None:
            # Auto-detect: script is in scripts/, plugin root is parent
            self.plugin_root = Path(__file__).parent.parent
        else:
            self.plugin_root = Path(plugin_root)

        self.templates_dir = self.plugin_root / "templates"
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.inventory: Dict[str, Dict] = {}

    def validate_all(self) -> Tuple[bool, Dict]:
        """
        Validate all templates in the plugin.

        Returns:
            Tuple of (success: bool, results: dict)
        """
        self.errors.clear()
        self.warnings.clear()
        self.inventory.clear()

        # Check templates directory exists
        if not self.templates_dir.exists():
            self.errors.append(f"Templates directory not found: {self.templates_dir}")
            return False, self._build_results()

        # Validate each template category
        self._validate_readme_templates()
        self._validate_license_templates()
        self._validate_contributing_templates()
        self._validate_security_templates()
        self._validate_issue_templates()
        self._validate_pr_templates()
        self._validate_support_templates()
        self._validate_codeowners_templates()
        self._validate_code_of_conduct_templates()
        self._validate_funding_templates()
        self._validate_governance_templates()

        success = len(self.errors) == 0
        return success, self._build_results()

    def _validate_readme_templates(self) -> None:
        """Validate README templates."""
        category = "README"
        templates = self._scan_templates(category)

        # Expected templates
        expected = [
            "full/README-MINIMAL.template.md",
            "full/README-STANDARD.template.md"
        ]

        self._check_expected_templates(category, templates, expected)
        self.inventory[category] = {
            "count": len(templates),
            "templates": templates,
            "expected": expected
        }

    def _validate_license_templates(self) -> None:
        """Validate LICENSE templates."""
        category = "LICENSE"
        templates = self._scan_templates(category)

        # Check subdirectories exist
        subdirs = ["github", "creative-commons", "fsl"]
        for subdir in subdirs:
            subdir_path = self.templates_dir / category / subdir
            if not subdir_path.exists():
                self.errors.append(f"Missing LICENSE subdirectory: {subdir}/")

        # Check metadata.json exists
        metadata_file = self.templates_dir / category / "metadata.json"
        if metadata_file.exists():
            self._validate_json_file(metadata_file)
        else:
            self.warnings.append(f"Missing {category}/metadata.json")

        # Expected minimum templates (some key licenses)
        expected_min = [
            "github/MIT.template.txt",
            "github/Apache-2.0.template.txt",
            "github/GPL-3.0.template.txt",
            "creative-commons/CC-BY-4.0.template.txt",
            "fsl/FSL-1.1-MIT.template.md"
        ]

        for template in expected_min:
            if template not in templates:
                self.errors.append(f"Missing expected LICENSE template: {template}")

        self.inventory[category] = {
            "count": len(templates),
            "templates": templates,
            "subdirectories": subdirs,
            "metadata": metadata_file.exists()
        }

    def _validate_contributing_templates(self) -> None:
        """Validate CONTRIBUTING templates."""
        category = "CONTRIBUTING"
        templates = self._scan_templates(category)

        expected = [
            "full/CONTRIBUTING-BASIC.template.md"
        ]

        self._check_expected_templates(category, templates, expected)
        self.inventory[category] = {
            "count": len(templates),
            "templates": templates,
            "expected": expected
        }

    def _validate_security_templates(self) -> None:
        """Validate SECURITY templates."""
        category = "SECURITY"
        templates = self._scan_templates(category)

        expected = [
            "full/SECURITY-BASIC.template.md"
        ]

        self._check_expected_templates(category, templates, expected)
        self.inventory[category] = {
            "count": len(templates),
            "templates": templates,
            "expected": expected
        }

    def _validate_issue_templates(self) -> None:
        """Validate ISSUE_TEMPLATES."""
        category = "ISSUE_TEMPLATES"
        templates = self._scan_templates(category)

        expected = [
            "full/bug_report.yml.template",
            "full/feature_request.yml.template"
        ]

        self._check_expected_templates(category, templates, expected)

        # Validate YAML syntax for .yml templates
        for template in templates:
            if template.endswith('.yml.template'):
                template_path = self.templates_dir / category / template
                self._validate_yaml_template(template_path)

        self.inventory[category] = {
            "count": len(templates),
            "templates": templates,
            "expected": expected
        }

    def _validate_pr_templates(self) -> None:
        """Validate PR_TEMPLATES."""
        category = "PR_TEMPLATES"
        templates = self._scan_templates(category)

        expected = [
            "full/PULL_REQUEST_TEMPLATE.md.template"
        ]

        self._check_expected_templates(category, templates, expected)
        self.inventory[category] = {
            "count": len(templates),
            "templates": templates,
            "expected": expected
        }

    def _validate_support_templates(self) -> None:
        """Validate SUPPORT templates."""
        category = "SUPPORT"
        templates = self._scan_templates(category)

        # SUPPORT templates are optional for now
        self.inventory[category] = {
            "count": len(templates),
            "templates": templates,
            "optional": True
        }

    def _validate_codeowners_templates(self) -> None:
        """Validate CODEOWNERS templates."""
        category = "CODEOWNERS"
        templates = self._scan_templates(category)

        # CODEOWNERS templates are optional
        self.inventory[category] = {
            "count": len(templates),
            "templates": templates,
            "optional": True
        }

    def _validate_code_of_conduct_templates(self) -> None:
        """Validate CODE_OF_CONDUCT templates."""
        category = "CODE_OF_CONDUCT"
        templates = self._scan_templates(category)

        # CODE_OF_CONDUCT templates are optional
        self.inventory[category] = {
            "count": len(templates),
            "templates": templates,
            "optional": True
        }

    def _validate_funding_templates(self) -> None:
        """Validate FUNDING templates."""
        category = "FUNDING"
        templates = self._scan_templates(category)

        # FUNDING templates are optional
        self.inventory[category] = {
            "count": len(templates),
            "templates": templates,
            "optional": True
        }

    def _validate_governance_templates(self) -> None:
        """Validate GOVERNANCE templates."""
        category = "GOVERNANCE"
        templates = self._scan_templates(category)

        # GOVERNANCE templates are optional
        self.inventory[category] = {
            "count": len(templates),
            "templates": templates,
            "optional": True
        }

    def _scan_templates(self, category: str) -> List[str]:
        """
        Scan a template category directory for template files.

        Args:
            category: Template category name (e.g., "README", "LICENSE")

        Returns:
            List of relative template paths within category
        """
        category_dir = self.templates_dir / category
        if not category_dir.exists():
            self.warnings.append(f"Template category directory not found: {category}/")
            return []

        templates = []
        # Match files with .template in the name (e.g., file.template.md or file.yml.template)
        for template_file in category_dir.rglob("*template*"):
            if template_file.is_file() and ".template" in template_file.name:
                # Get path relative to category directory
                rel_path = template_file.relative_to(category_dir)
                templates.append(str(rel_path).replace("\\", "/"))  # Normalize path separators

        return sorted(templates)

    def _check_expected_templates(
        self,
        category: str,
        found: List[str],
        expected: List[str]
    ) -> None:
        """
        Check if expected templates are present.

        Args:
            category: Template category name
            found: List of found templates
            expected: List of expected template paths
        """
        for template in expected:
            if template not in found:
                self.errors.append(
                    f"Missing expected {category} template: {template}"
                )

    def _validate_json_file(self, json_file: Path) -> None:
        """
        Validate JSON file syntax.

        Args:
            json_file: Path to JSON file
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(
                f"Invalid JSON in {json_file.name}: {e}"
            )
        except Exception as e:
            self.errors.append(
                f"Error reading {json_file.name}: {e}"
            )

    def _validate_yaml_template(self, yaml_file: Path) -> None:
        """
        Basic validation of YAML template file.

        Args:
            yaml_file: Path to YAML template file
        """
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                content = f.read()

                # Basic checks (not full YAML parsing to avoid dependencies)
                if not content.strip():
                    self.errors.append(f"Empty template file: {yaml_file.name}")
                    return

                # Check for common YAML template fields
                required_fields = ['name:', 'description:', 'body:']
                missing_fields = [
                    field for field in required_fields
                    if field not in content
                ]

                if missing_fields:
                    self.warnings.append(
                        f"{yaml_file.name} missing fields: {', '.join(missing_fields)}"
                    )
        except Exception as e:
            self.errors.append(f"Error reading {yaml_file.name}: {e}")

    def _build_results(self) -> Dict:
        """
        Build results dictionary.

        Returns:
            Results dictionary with validation status and inventory
        """
        total_templates = sum(
            cat.get("count", 0)
            for cat in self.inventory.values()
        )

        return {
            "success": len(self.errors) == 0,
            "templates_dir": str(self.templates_dir),
            "total_templates": total_templates,
            "errors": self.errors,
            "warnings": self.warnings,
            "inventory": self.inventory
        }

    def get_template_path(
        self,
        category: str,
        template: str
    ) -> Optional[Path]:
        """
        Get absolute path to a template file.

        Args:
            category: Template category (e.g., "README")
            template: Template relative path (e.g., "full/README-MINIMAL.template.md")

        Returns:
            Absolute path to template, or None if not found
        """
        template_path = self.templates_dir / category / template
        return template_path if template_path.exists() else None

    def list_templates(self, category: Optional[str] = None) -> Dict[str, List[str]]:
        """
        List available templates.

        Args:
            category: Optional category to filter (e.g., "README")
                     If None, returns all categories

        Returns:
            Dictionary mapping category to list of templates
        """
        if category:
            return {
                category: self.inventory.get(category, {}).get("templates", [])
            }

        return {
            cat: data.get("templates", [])
            for cat, data in self.inventory.items()
        }


def print_results(results: Dict, verbose: bool = False) -> None:
    """
    Print validation results in human-readable format.

    Args:
        results: Results dictionary from validator
        verbose: Show detailed information
    """
    success = results["success"]

    # Header
    print("=" * 70)
    print("README-AND-CO TEMPLATE VALIDATION")
    print("=" * 70)
    print()

    # Summary
    status_icon = "✅" if success else "❌"
    status_text = "PASS" if success else "FAIL"
    print(f"Status: {status_icon} {status_text}")
    print(f"Templates Directory: {results['templates_dir']}")
    print(f"Total Templates: {results['total_templates']}")
    print()

    # Errors
    if results["errors"]:
        print("ERRORS:")
        for error in results["errors"]:
            print(f"  ❌ {error}")
        print()

    # Warnings
    if results["warnings"]:
        print("WARNINGS:")
        for warning in results["warnings"]:
            print(f"  ⚠️  {warning}")
        print()

    # Inventory (verbose mode)
    if verbose:
        print("TEMPLATE INVENTORY:")
        for category, data in results["inventory"].items():
            count = data.get("count", 0)
            optional = " (optional)" if data.get("optional") else ""
            print(f"\n  {category}{optional}: {count} template(s)")

            if data.get("templates"):
                for template in data["templates"]:
                    print(f"    - {template}")
        print()

    # Footer
    print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate readme-and-co plugin templates"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed validation information"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit with non-zero code if validation fails (CI mode)"
    )
    parser.add_argument(
        "--plugin-root",
        type=str,
        help="Path to plugin root directory (auto-detected if not specified)"
    )

    args = parser.parse_args()

    # Create validator
    validator = TemplateValidator(
        plugin_root=Path(args.plugin_root) if args.plugin_root else None
    )

    # Run validation
    success, results = validator.validate_all()

    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_results(results, verbose=args.verbose)

    # Exit code
    if args.check and not success:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
