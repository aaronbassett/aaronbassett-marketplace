#!/usr/bin/env python3
"""
Integration tests for populate_license.py

Tests cover:
- License template discovery
- Variable substitution (multiple syntaxes)
- Smart defaults from git and package.json
- License name normalization
- All 21 license templates
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path to import the script
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from populate_license import (
    get_package_json_info,
    get_smart_defaults,
    normalize_license_name,
    find_license_template,
    substitute_license_variables,
    populate_license,
)


class TestGetPackageJsonInfo(unittest.TestCase):
    """Test package.json information extraction."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_extract_name(self):
        """Test extracting project name."""
        package_json = {"name": "my-project"}
        (self.temp_path / 'package.json').write_text(json.dumps(package_json))

        info = get_package_json_info(self.temp_path)
        self.assertEqual(info['project_name'], 'my-project')

    def test_extract_author_string(self):
        """Test extracting author as string."""
        package_json = {"author": "John Doe"}
        (self.temp_path / 'package.json').write_text(json.dumps(package_json))

        info = get_package_json_info(self.temp_path)
        self.assertEqual(info['author_name'], 'John Doe')

    def test_extract_author_object(self):
        """Test extracting author as object."""
        package_json = {
            "author": {
                "name": "Jane Doe",
                "email": "jane@example.com"
            }
        }
        (self.temp_path / 'package.json').write_text(json.dumps(package_json))

        info = get_package_json_info(self.temp_path)
        self.assertEqual(info['author_name'], 'Jane Doe')
        self.assertEqual(info['author_email'], 'jane@example.com')

    def test_no_package_json(self):
        """Test when package.json doesn't exist."""
        info = get_package_json_info(self.temp_path)
        self.assertEqual(info, {})

    def test_invalid_json(self):
        """Test handling of invalid JSON."""
        (self.temp_path / 'package.json').write_text('invalid json{')

        info = get_package_json_info(self.temp_path)
        self.assertEqual(info, {})


class TestGetSmartDefaults(unittest.TestCase):
    """Test smart defaults from git and package.json."""

    def test_includes_current_year(self):
        """Test that current year is included."""
        from datetime import datetime

        defaults = get_smart_defaults()
        self.assertEqual(defaults['year'], str(datetime.now().year))

    def test_returns_dict(self):
        """Test that function returns a dictionary."""
        defaults = get_smart_defaults()
        self.assertIsInstance(defaults, dict)

    # Note: Testing git config requires git to be configured
    # These are integration tests, so we test the behavior


class TestNormalizeLicenseName(unittest.TestCase):
    """Test license name normalization."""

    def test_normalize_mit(self):
        """Test MIT normalization."""
        self.assertEqual(normalize_license_name('MIT'), 'MIT')
        self.assertEqual(normalize_license_name('mit'), 'MIT')

    def test_normalize_apache(self):
        """Test Apache normalization."""
        self.assertEqual(normalize_license_name('APACHE'), 'Apache-2.0')
        self.assertEqual(normalize_license_name('apache'), 'Apache-2.0')
        self.assertEqual(normalize_license_name('Apache-2'), 'Apache-2.0')
        self.assertEqual(normalize_license_name('APACHE2'), 'Apache-2.0')

    def test_normalize_gpl(self):
        """Test GPL normalization."""
        self.assertEqual(normalize_license_name('GPL'), 'GPL-3.0')
        self.assertEqual(normalize_license_name('GPL-3'), 'GPL-3.0')
        self.assertEqual(normalize_license_name('gpl3'), 'GPL-3.0')

    def test_normalize_bsd(self):
        """Test BSD normalization."""
        self.assertEqual(normalize_license_name('BSD'), 'BSD-3-Clause')
        self.assertEqual(normalize_license_name('BSD-3'), 'BSD-3-Clause')

    def test_normalize_fsl(self):
        """Test FSL normalization."""
        self.assertEqual(normalize_license_name('FSL'), 'FSL-1.1-MIT')
        self.assertEqual(normalize_license_name('FSL-MIT'), 'FSL-1.1-MIT')

    def test_unknown_license_unchanged(self):
        """Test unknown license names are returned unchanged."""
        self.assertEqual(normalize_license_name('Custom-License'), 'Custom-License')


class TestFindLicenseTemplate(unittest.TestCase):
    """Test license template discovery."""

    def setUp(self):
        """Set plugin root to actual plugin directory."""
        # Find plugin root (go up from tests/ to plugin root)
        self.plugin_root = Path(__file__).parent.parent

    def test_find_mit_template(self):
        """Test finding MIT template."""
        template_path = find_license_template('MIT', self.plugin_root)
        self.assertIsNotNone(template_path)
        self.assertTrue(template_path.exists())

    def test_find_apache_template(self):
        """Test finding Apache template."""
        template_path = find_license_template('Apache-2.0', self.plugin_root)
        self.assertIsNotNone(template_path)
        self.assertTrue(template_path.exists())

    def test_find_gpl_template(self):
        """Test finding GPL template."""
        template_path = find_license_template('GPL-3.0', self.plugin_root)
        self.assertIsNotNone(template_path)
        self.assertTrue(template_path.exists())

    def test_find_fsl_template(self):
        """Test finding FSL template."""
        template_path = find_license_template('FSL-1.1-MIT', self.plugin_root)
        self.assertIsNotNone(template_path)
        self.assertTrue(template_path.exists())

    def test_nonexistent_template(self):
        """Test that nonexistent template returns None."""
        template_path = find_license_template('NONEXISTENT-LICENSE', self.plugin_root)
        self.assertIsNone(template_path)


class TestSubstituteLicenseVariables(unittest.TestCase):
    """Test license variable substitution."""

    def test_substitute_bracket_syntax(self):
        """Test [variable] syntax substitution."""
        content = "Copyright (c) [year] [fullname]"
        variables = {'year': '2024', 'fullname': 'John Doe'}
        result = substitute_license_variables(content, variables)
        self.assertEqual(result, "Copyright (c) 2024 John Doe")

    def test_substitute_dollar_brace_syntax(self):
        """Test ${variable} syntax substitution."""
        content = "Copyright (c) ${year} ${fullname}"
        variables = {'year': '2024', 'fullname': 'John Doe'}
        result = substitute_license_variables(content, variables)
        self.assertEqual(result, "Copyright (c) 2024 John Doe")

    def test_substitute_double_brace_syntax(self):
        """Test {{variable}} syntax substitution."""
        content = "Copyright (c) {{year}} {{fullname}}"
        variables = {'year': '2024', 'fullname': 'John Doe'}
        result = substitute_license_variables(content, variables)
        self.assertEqual(result, "Copyright (c) 2024 John Doe")

    def test_variable_mapping(self):
        """Test that copyright_holder maps to fullname."""
        content = "[fullname]"
        variables = {'copyright_holder': 'Jane Doe'}
        result = substitute_license_variables(content, variables)
        self.assertEqual(result, "Jane Doe")

    def test_all_syntaxes_together(self):
        """Test mixed variable syntaxes in same content."""
        content = "[year] ${fullname} {{project}}"
        variables = {
            'year': '2024',
            'fullname': 'John Doe',
            'project': 'MyProject'
        }
        result = substitute_license_variables(content, variables)
        self.assertEqual(result, "2024 John Doe MyProject")

    def test_unsubstituted_variables_unchanged(self):
        """Test that missing variables remain unchanged."""
        content = "[year] [missing]"
        variables = {'year': '2024'}
        result = substitute_license_variables(content, variables)
        self.assertIn('2024', result)
        self.assertIn('[missing]', result)


class TestPopulateLicense(unittest.TestCase):
    """Test complete license population workflow."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.plugin_root = Path(__file__).parent.parent

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_populate_mit_license(self):
        """Test populating MIT license."""
        output_path = self.temp_path / 'LICENSE'

        result = populate_license(
            license_name='MIT',
            holder='John Doe',
            year='2024',
            plugin_root=self.plugin_root,
            output_path=output_path
        )

        # Check output file was created
        self.assertTrue(output_path.exists())

        # Check content
        content = output_path.read_text()
        self.assertIn('MIT License', content)
        self.assertIn('2024', content)
        self.assertIn('John Doe', content)

    def test_populate_apache_license(self):
        """Test populating Apache license."""
        output_path = self.temp_path / 'LICENSE'

        result = populate_license(
            license_name='Apache-2.0',
            holder='Jane Doe',
            year='2024',
            plugin_root=self.plugin_root,
            output_path=output_path
        )

        # Check content
        content = output_path.read_text()
        self.assertIn('Apache License', content)
        # Apache license has placeholders in appendix, not variables

    def test_populate_with_auto_detect(self):
        """Test populating with auto-detected values."""
        output_path = self.temp_path / 'LICENSE'

        result = populate_license(
            license_name='MIT',
            auto_detect=True,
            plugin_root=self.plugin_root,
            output_path=output_path
        )

        # Should succeed and create file
        self.assertTrue(output_path.exists())

        # Should include current year
        from datetime import datetime
        content = output_path.read_text()
        self.assertIn(str(datetime.now().year), content)

    def test_populate_to_stdout(self):
        """Test populating without output path (stdout)."""
        result = populate_license(
            license_name='MIT',
            holder='Test User',
            year='2024',
            plugin_root=self.plugin_root,
            output_path=None
        )

        # Should return rendered content
        self.assertIn('MIT License', result)
        self.assertIn('Test User', result)

    def test_nonexistent_license_raises_error(self):
        """Test that nonexistent license raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            populate_license(
                license_name='NONEXISTENT-LICENSE',
                plugin_root=self.plugin_root
            )

    def test_normalized_license_name(self):
        """Test that license names are normalized."""
        output_path = self.temp_path / 'LICENSE'

        # Use 'apache' (lowercase) which should be normalized to Apache-2.0
        result = populate_license(
            license_name='apache',
            holder='Test',
            year='2024',
            plugin_root=self.plugin_root,
            output_path=output_path
        )

        content = output_path.read_text()
        self.assertIn('Apache License', content)


class TestLicenseTemplates(unittest.TestCase):
    """Test that all expected license templates exist and render."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.plugin_root = Path(__file__).parent.parent

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_all_github_licenses_exist(self):
        """Test that all common GitHub licenses exist."""
        github_licenses = [
            'MIT',
            'Apache-2.0',
            'GPL-3.0',
            'AGPL-3.0',
            'MPL-2.0',
            'BSD-2-Clause',
            'BSD-3-Clause',
            'BSL-1.0',
            'Unlicense',
        ]

        for license_name in github_licenses:
            template_path = find_license_template(license_name, self.plugin_root)
            self.assertIsNotNone(
                template_path,
                f"Template not found for {license_name}"
            )

    def test_fsl_license_exists(self):
        """Test that FSL license template exists."""
        template_path = find_license_template('FSL-1.1-MIT', self.plugin_root)
        self.assertIsNotNone(template_path)

    def test_creative_commons_licenses_exist(self):
        """Test that Creative Commons licenses exist."""
        cc_licenses = [
            'CC-BY-4.0',
            'CC-BY-SA-4.0',
            'CC-BY-NC-4.0',
            'CC-BY-NC-SA-4.0',
            'CC-BY-ND-4.0',
            'CC-BY-NC-ND-4.0',
            'CC0-1.0',
        ]

        for license_name in cc_licenses:
            template_path = find_license_template(license_name, self.plugin_root)
            self.assertIsNotNone(
                template_path,
                f"Template not found for {license_name}"
            )

    def test_all_licenses_render_without_error(self):
        """Test that all license templates can be rendered."""
        all_licenses = [
            'MIT', 'Apache-2.0', 'GPL-3.0', 'AGPL-3.0',
            'MPL-2.0', 'BSD-2-Clause', 'BSD-3-Clause', 'BSL-1.0',
            'Unlicense', 'FSL-1.1-MIT',
            'CC-BY-4.0', 'CC-BY-SA-4.0', 'CC-BY-NC-4.0',
            'CC-BY-NC-SA-4.0', 'CC-BY-ND-4.0', 'CC-BY-NC-ND-4.0',
            'CC0-1.0',
        ]

        for license_name in all_licenses:
            with self.subTest(license_name=license_name):
                # Skip if template doesn't exist (some licenses may be optional)
                template_path = find_license_template(license_name, self.plugin_root)
                if not template_path:
                    continue

                try:
                    output_path = self.temp_path / f'{license_name}.txt'
                    result = populate_license(
                        license_name=license_name,
                        holder='Test User',
                        year='2024',
                        plugin_root=self.plugin_root,
                        output_path=output_path
                    )

                    # Should create file
                    self.assertTrue(output_path.exists())

                    # Should have content
                    content = output_path.read_text()
                    self.assertGreater(len(content), 100)

                except Exception as e:
                    self.fail(f"Failed to render {license_name}: {e}")


if __name__ == '__main__':
    unittest.main()
