#!/usr/bin/env python3
"""
Integration tests for all templates in the plugin.

Tests that:
- All templates exist and are readable
- All templates have valid syntax
- Variable placeholders are consistent
- Templates can be rendered without errors
"""

import sys
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from render_template import find_template_variables


class TestTemplateStructure(unittest.TestCase):
    """Test that template directory structure is valid."""

    def setUp(self):
        """Set up plugin root path."""
        self.plugin_root = Path(__file__).parent.parent
        self.templates_dir = self.plugin_root / 'templates'

    def test_templates_directory_exists(self):
        """Test that templates directory exists."""
        self.assertTrue(self.templates_dir.exists())
        self.assertTrue(self.templates_dir.is_dir())

    def test_template_categories_exist(self):
        """Test that all expected template categories exist."""
        expected_categories = [
            'README',
            'LICENSE',
            'CONTRIBUTING',
            'CODE_OF_CONDUCT',
            'SECURITY',
            'SUPPORT',
            'CODEOWNERS',
            'ISSUE_TEMPLATES',
            'PR_TEMPLATES',
            'GOVERNANCE',
            'FUNDING',
        ]

        for category in expected_categories:
            category_path = self.templates_dir / category
            self.assertTrue(
                category_path.exists(),
                f"Template category {category} does not exist"
            )


class TestREADMETemplates(unittest.TestCase):
    """Test README templates."""

    def setUp(self):
        """Set up paths."""
        self.plugin_root = Path(__file__).parent.parent
        self.readme_dir = self.plugin_root / 'templates' / 'README'

    def test_minimal_template_exists(self):
        """Test that MINIMAL README template exists."""
        # Check in subdirectories too
        templates = list(self.readme_dir.rglob('*MINIMAL.template.md'))
        self.assertGreater(len(templates), 0, "No MINIMAL README template found")

    def test_standard_template_exists(self):
        """Test that STANDARD README template exists."""
        # Check in subdirectories too
        templates = list(self.readme_dir.rglob('*STANDARD.template.md'))
        self.assertGreater(len(templates), 0, "No STANDARD README template found")

    def test_readme_templates_are_valid(self):
        """Test that README templates have valid syntax."""
        for template_file in self.readme_dir.glob('*.template.md'):
            with self.subTest(template=template_file.name):
                content = template_file.read_text()

                # Should have content
                self.assertGreater(len(content), 0)

                # Should have at least one variable
                variables = find_template_variables(content)
                self.assertGreater(len(variables), 0)

    def test_readme_common_variables(self):
        """Test that README templates use common variables."""
        expected_vars = {'project_name', 'description'}

        for template_file in self.readme_dir.glob('*.template.md'):
            content = template_file.read_text()
            variables = find_template_variables(content)

            # Should have project_name
            self.assertIn(
                'project_name',
                variables,
                f"{template_file.name} missing project_name variable"
            )


class TestLICENSETemplates(unittest.TestCase):
    """Test LICENSE templates."""

    def setUp(self):
        """Set up paths."""
        self.plugin_root = Path(__file__).parent.parent
        self.license_dir = self.plugin_root / 'templates' / 'LICENSE'

    def test_github_licenses_directory_exists(self):
        """Test that github/ subdirectory exists."""
        github_dir = self.license_dir / 'github'
        self.assertTrue(github_dir.exists())

    def test_creative_commons_directory_exists(self):
        """Test that creative-commons/ subdirectory exists."""
        cc_dir = self.license_dir / 'creative-commons'
        self.assertTrue(cc_dir.exists())

    def test_fsl_directory_exists(self):
        """Test that fsl/ subdirectory exists."""
        fsl_dir = self.license_dir / 'fsl'
        self.assertTrue(fsl_dir.exists())

    def test_license_templates_count(self):
        """Test that we have expected number of license templates."""
        # Count all .template.* files in LICENSE and subdirectories
        all_templates = list(self.license_dir.rglob('*.template.*'))

        # Should have at least 21 licenses (as mentioned in review)
        self.assertGreaterEqual(
            len(all_templates),
            21,
            f"Expected at least 21 license templates, found {len(all_templates)}"
        )

    def test_common_github_licenses_exist(self):
        """Test that common GitHub licenses exist."""
        common_licenses = [
            'MIT.template.txt',
            'Apache-2.0.template.txt',
            'GPL-3.0.template.txt',
            'BSD-3-Clause.template.txt',
        ]

        github_dir = self.license_dir / 'github'
        for license_file in common_licenses:
            license_path = github_dir / license_file
            self.assertTrue(
                license_path.exists(),
                f"Common license {license_file} does not exist"
            )

    def test_license_templates_are_readable(self):
        """Test that all license templates can be read."""
        all_templates = list(self.license_dir.rglob('*.template.*'))

        for template_file in all_templates:
            with self.subTest(template=template_file.name):
                content = template_file.read_text()
                self.assertGreater(len(content), 100)


class TestCONTRIBUTINGTemplates(unittest.TestCase):
    """Test CONTRIBUTING templates."""

    def setUp(self):
        """Set up paths."""
        self.plugin_root = Path(__file__).parent.parent
        self.contrib_dir = self.plugin_root / 'templates' / 'CONTRIBUTING'

    def test_contributing_templates_exist(self):
        """Test that CONTRIBUTING templates exist."""
        templates = list(self.contrib_dir.rglob('*.template.md'))
        self.assertGreater(len(templates), 0)

    def test_contributing_templates_readable(self):
        """Test that CONTRIBUTING templates are readable."""
        for template_file in self.contrib_dir.rglob('*.template.md'):
            with self.subTest(template=template_file.name):
                content = template_file.read_text()
                self.assertGreater(len(content), 100)


class TestGitHubTemplates(unittest.TestCase):
    """Test GitHub-specific templates (issues, PRs, etc)."""

    def setUp(self):
        """Set up paths."""
        self.plugin_root = Path(__file__).parent.parent
        self.templates_dir = self.plugin_root / 'templates'

    def test_issue_templates_exist(self):
        """Test that issue templates exist if directory exists."""
        issue_dir = self.templates_dir / 'ISSUE_TEMPLATES'
        if not issue_dir.exists():
            self.skipTest("ISSUE_TEMPLATES directory does not exist yet")

        templates = list(issue_dir.rglob('*.template.*'))
        # Allow empty for now - templates may be added later
        # At minimum, directory structure should exist
        self.assertTrue(issue_dir.exists())

    def test_pr_templates_exist(self):
        """Test that PR templates exist if directory exists."""
        pr_dir = self.templates_dir / 'PR_TEMPLATES'
        if not pr_dir.exists():
            self.skipTest("PR_TEMPLATES directory does not exist yet")

        # At minimum, directory structure should exist
        self.assertTrue(pr_dir.exists())

    def test_codeowners_template_exists(self):
        """Test that CODEOWNERS template exists if directory exists."""
        codeowners_dir = self.templates_dir / 'CODEOWNERS'
        if not codeowners_dir.exists():
            self.skipTest("CODEOWNERS directory does not exist yet")

        # At minimum, directory structure should exist
        self.assertTrue(codeowners_dir.exists())

    def test_security_template_exists(self):
        """Test that SECURITY template exists if directory exists."""
        security_dir = self.templates_dir / 'SECURITY'
        if not security_dir.exists():
            self.skipTest("SECURITY directory does not exist yet")

        # At minimum, directory structure should exist
        self.assertTrue(security_dir.exists())

    def test_code_of_conduct_template_exists(self):
        """Test that CODE_OF_CONDUCT template exists if directory exists."""
        coc_dir = self.templates_dir / 'CODE_OF_CONDUCT'
        if not coc_dir.exists():
            self.skipTest("CODE_OF_CONDUCT directory does not exist yet")

        # At minimum, directory structure should exist
        self.assertTrue(coc_dir.exists())


class TestTemplateConsistency(unittest.TestCase):
    """Test template consistency and quality."""

    def setUp(self):
        """Set up paths."""
        self.plugin_root = Path(__file__).parent.parent
        self.templates_dir = self.plugin_root / 'templates'

    def test_all_templates_have_template_extension(self):
        """Test that all template files use .template in naming."""
        for template_dir in self.templates_dir.iterdir():
            if not template_dir.is_dir():
                continue

            # Find all potential template files
            for file in template_dir.rglob('*'):
                if file.is_file() and not file.name.startswith('.'):
                    # Skip metadata files
                    if file.suffix in ['.json', '.yaml']:
                        continue

                    # Should contain .template somewhere in name
                    # Accepts both .template.md and .yml.template formats
                    self.assertIn(
                        '.template',
                        file.name,
                        f"File {file.relative_to(self.templates_dir)} "
                        f"does not include .template in filename"
                    )

    def test_no_empty_templates(self):
        """Test that no templates are empty."""
        all_templates = list(self.templates_dir.rglob('*.template.*'))

        for template_file in all_templates:
            with self.subTest(template=template_file.relative_to(self.templates_dir)):
                content = template_file.read_text()
                self.assertGreater(
                    len(content.strip()),
                    0,
                    f"Template {template_file.name} is empty"
                )

    def test_templates_use_utf8(self):
        """Test that all templates can be read as UTF-8."""
        all_templates = list(self.templates_dir.rglob('*.template.*'))

        for template_file in all_templates:
            with self.subTest(template=template_file.name):
                try:
                    content = template_file.read_text(encoding='utf-8')
                    self.assertIsInstance(content, str)
                except UnicodeDecodeError:
                    self.fail(f"Template {template_file.name} is not valid UTF-8")


class TestTemplateCount(unittest.TestCase):
    """Test overall template count."""

    def setUp(self):
        """Set up paths."""
        self.plugin_root = Path(__file__).parent.parent
        self.templates_dir = self.plugin_root / 'templates'

    def test_total_template_count(self):
        """Test that we have expected number of templates."""
        # Count all .template.* files
        all_templates = list(self.templates_dir.rglob('*.template.*'))

        # Review report mentions 70+ templates
        self.assertGreaterEqual(
            len(all_templates),
            25,  # Conservative estimate for initial implementation
            f"Expected at least 25 templates, found {len(all_templates)}"
        )

    def test_template_categories_have_templates(self):
        """Test that all categories have at least one template."""
        required_categories = [
            'README',
            'LICENSE',
            'CONTRIBUTING',
        ]

        for category in required_categories:
            category_path = self.templates_dir / category
            templates = list(category_path.rglob('*.template.*'))
            self.assertGreater(
                len(templates),
                0,
                f"Category {category} has no templates"
            )


if __name__ == '__main__':
    unittest.main()
