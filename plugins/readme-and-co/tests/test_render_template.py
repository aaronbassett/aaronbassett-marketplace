#!/usr/bin/env python3
"""
Integration tests for render_template.py

Tests cover:
- Variable substitution
- Fragment concatenation
- Validation mode
- Error handling
- All variable syntaxes
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path to import the script
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from render_template import (
    find_template_variables,
    substitute_variables,
    validate_template,
    render_template,
    parse_variables,
)


class TestFindTemplateVariables(unittest.TestCase):
    """Test template variable detection."""

    def test_find_single_variable(self):
        """Test finding a single variable."""
        content = "Hello {{name}}!"
        variables = find_template_variables(content)
        self.assertEqual(variables, {'name'})

    def test_find_multiple_variables(self):
        """Test finding multiple variables."""
        content = "{{greeting}} {{name}}, welcome to {{project}}!"
        variables = find_template_variables(content)
        self.assertEqual(variables, {'greeting', 'name', 'project'})

    def test_find_duplicate_variables(self):
        """Test that duplicates are deduplicated."""
        content = "{{name}} and {{name}} again"
        variables = find_template_variables(content)
        self.assertEqual(variables, {'name'})

    def test_find_variables_with_whitespace(self):
        """Test variables with whitespace are trimmed."""
        content = "{{ name }} and {{  title  }}"
        variables = find_template_variables(content)
        self.assertEqual(variables, {'name', 'title'})

    def test_no_variables(self):
        """Test content with no variables."""
        content = "Just plain text"
        variables = find_template_variables(content)
        self.assertEqual(variables, set())


class TestSubstituteVariables(unittest.TestCase):
    """Test variable substitution."""

    def test_substitute_single_variable(self):
        """Test substituting a single variable."""
        content = "Hello {{name}}!"
        variables = {'name': 'World'}
        rendered, warnings = substitute_variables(content, variables)
        self.assertEqual(rendered, "Hello World!")
        self.assertEqual(warnings, [])

    def test_substitute_multiple_variables(self):
        """Test substituting multiple variables."""
        content = "{{greeting}} {{name}}!"
        variables = {'greeting': 'Hello', 'name': 'World'}
        rendered, warnings = substitute_variables(content, variables)
        self.assertEqual(rendered, "Hello World!")
        self.assertEqual(warnings, [])

    def test_missing_variable_warning(self):
        """Test that missing variables generate warnings."""
        content = "Hello {{name}}!"
        variables = {}
        rendered, warnings = substitute_variables(content, variables)
        self.assertEqual(rendered, "Hello [MISSING: name]!")
        self.assertEqual(len(warnings), 1)
        self.assertIn('name', warnings[0])

    def test_partial_substitution(self):
        """Test partial substitution with some missing variables."""
        content = "{{greeting}} {{name}}, age {{age}}"
        variables = {'greeting': 'Hello', 'age': '30'}
        rendered, warnings = substitute_variables(content, variables)
        self.assertEqual(rendered, "Hello [MISSING: name], age 30")
        self.assertEqual(len(warnings), 1)

    def test_number_to_string_conversion(self):
        """Test that numbers are converted to strings."""
        content = "Version {{version}}"
        variables = {'version': 123}
        rendered, warnings = substitute_variables(content, variables)
        self.assertEqual(rendered, "Version 123")
        self.assertEqual(warnings, [])


class TestValidateTemplate(unittest.TestCase):
    """Test template validation."""

    def test_validate_perfect_match(self):
        """Test validation with perfect variable match."""
        content = "{{name}} {{age}}"
        variables = {'name': 'John', 'age': '30'}
        result = validate_template(content, variables)

        self.assertEqual(result['errors'], [])
        self.assertEqual(result['warnings'], [])
        self.assertEqual(len(result['info']), 2)

    def test_validate_missing_variables(self):
        """Test validation detects missing variables."""
        content = "{{name}} {{age}} {{city}}"
        variables = {'name': 'John'}
        result = validate_template(content, variables)

        self.assertEqual(len(result['errors']), 2)
        self.assertTrue(any('age' in err for err in result['errors']))
        self.assertTrue(any('city' in err for err in result['errors']))

    def test_validate_unused_variables(self):
        """Test validation detects unused variables."""
        content = "{{name}}"
        variables = {'name': 'John', 'age': '30', 'city': 'NYC'}
        result = validate_template(content, variables)

        self.assertEqual(len(result['warnings']), 2)
        self.assertTrue(any('age' in warn for warn in result['warnings']))
        self.assertTrue(any('city' in warn for warn in result['warnings']))

    def test_validate_empty_template(self):
        """Test validation with template that has no variables."""
        content = "Just plain text"
        variables = {'name': 'John'}
        result = validate_template(content, variables)

        self.assertEqual(result['errors'], [])
        self.assertEqual(len(result['warnings']), 1)  # Unused variable


class TestParseVariables(unittest.TestCase):
    """Test JSON variable parsing."""

    def test_parse_simple_json(self):
        """Test parsing simple JSON."""
        json_str = '{"name": "John", "age": "30"}'
        variables = parse_variables(json_str)
        self.assertEqual(variables, {'name': 'John', 'age': '30'})

    def test_parse_empty_string(self):
        """Test parsing empty string returns empty dict."""
        variables = parse_variables('')
        self.assertEqual(variables, {})

    def test_parse_empty_json(self):
        """Test parsing empty JSON object."""
        variables = parse_variables('{}')
        self.assertEqual(variables, {})

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON raises ValueError."""
        with self.assertRaises(ValueError):
            parse_variables('not valid json')

    def test_parse_non_dict_json(self):
        """Test parsing non-dict JSON raises ValueError."""
        with self.assertRaises(ValueError):
            parse_variables('["array", "not", "dict"]')


class TestRenderTemplate(unittest.TestCase):
    """Test complete template rendering workflow."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_render_simple_template(self):
        """Test rendering a simple template."""
        # Create template file
        template_path = self.temp_path / 'template.md'
        template_path.write_text('# {{title}}\n\nBy {{author}}')

        # Render
        variables = {'title': 'My Project', 'author': 'Jane Doe'}
        rendered, warnings, validation = render_template(
            template_path=template_path,
            variables=variables
        )

        self.assertIn('My Project', rendered)
        self.assertIn('Jane Doe', rendered)
        self.assertEqual(warnings, [])
        self.assertIsNone(validation)

    def test_render_to_file(self):
        """Test rendering and writing to output file."""
        # Create template
        template_path = self.temp_path / 'template.md'
        template_path.write_text('Hello {{name}}!')

        # Render to file
        output_path = self.temp_path / 'output.md'
        variables = {'name': 'World'}
        rendered, warnings, validation = render_template(
            template_path=template_path,
            variables=variables,
            output_path=output_path
        )

        # Check file was created
        self.assertTrue(output_path.exists())
        self.assertEqual(output_path.read_text(), 'Hello World!')

    def test_render_fragments(self):
        """Test fragment concatenation."""
        # Create fragments
        frag1 = self.temp_path / 'frag1.md'
        frag1.write_text('# {{title}}')

        frag2 = self.temp_path / 'frag2.md'
        frag2.write_text('By {{author}}')

        # Render fragments
        variables = {'title': 'Project', 'author': 'John'}
        rendered, warnings, validation = render_template(
            fragment_paths=[frag1, frag2],
            variables=variables
        )

        # Fragments should be joined with double newline
        self.assertIn('# Project', rendered)
        self.assertIn('By John', rendered)
        self.assertIn('\n\n', rendered)

    def test_validate_mode(self):
        """Test validation mode doesn't render."""
        template_path = self.temp_path / 'template.md'
        template_path.write_text('{{name}} {{age}}')

        # Validate with missing variable
        variables = {'name': 'John'}
        rendered, warnings, validation = render_template(
            template_path=template_path,
            variables=variables,
            validate_only=True
        )

        # Should return empty rendered content
        self.assertEqual(rendered, '')
        self.assertEqual(warnings, [])

        # Should have validation results
        self.assertIsNotNone(validation)
        self.assertEqual(len(validation['errors']), 1)
        self.assertTrue(any('age' in err for err in validation['errors']))

    def test_missing_template_error(self):
        """Test that missing template raises error."""
        nonexistent = self.temp_path / 'doesnotexist.md'

        with self.assertRaises(FileNotFoundError):
            render_template(template_path=nonexistent)

    def test_no_input_error(self):
        """Test that no template or fragments raises error."""
        with self.assertRaises(ValueError):
            render_template()


class TestVariableSyntaxes(unittest.TestCase):
    """Test that only {{variable}} syntax is supported."""

    def test_double_brace_syntax(self):
        """Test {{variable}} syntax works."""
        content = "Name: {{name}}"
        variables = {'name': 'John'}
        rendered, warnings = substitute_variables(content, variables)
        self.assertEqual(rendered, "Name: John")

    def test_bracket_syntax_not_supported(self):
        """Test [variable] syntax is not substituted."""
        content = "Name: [name]"
        variables = {'name': 'John'}
        rendered, warnings = substitute_variables(content, variables)
        self.assertEqual(rendered, "Name: [name]")  # Not substituted

    def test_dollar_brace_syntax_not_supported(self):
        """Test ${variable} syntax is not substituted."""
        content = "Name: ${name}"
        variables = {'name': 'John'}
        rendered, warnings = substitute_variables(content, variables)
        self.assertEqual(rendered, "Name: ${name}")  # Not substituted


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and special scenarios."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_multiline_template(self):
        """Test template with multiple lines."""
        template = """# {{title}}

## Description
{{description}}

## Author
{{author}}"""

        template_path = self.temp_path / 'template.md'
        template_path.write_text(template)

        variables = {
            'title': 'My Project',
            'description': 'A cool project',
            'author': 'Jane'
        }
        rendered, warnings, _ = render_template(
            template_path=template_path,
            variables=variables
        )

        self.assertIn('# My Project', rendered)
        self.assertIn('A cool project', rendered)
        self.assertIn('Jane', rendered)

    def test_empty_variable_value(self):
        """Test substituting with empty string."""
        content = "Name: {{name}}"
        variables = {'name': ''}
        rendered, warnings = substitute_variables(content, variables)
        self.assertEqual(rendered, "Name: ")
        self.assertEqual(warnings, [])

    def test_special_characters_in_value(self):
        """Test values with special characters."""
        content = "Name: {{name}}"
        variables = {'name': 'John & Jane <Test>'}
        rendered, warnings = substitute_variables(content, variables)
        self.assertEqual(rendered, "Name: John & Jane <Test>")

    def test_unicode_in_template_and_values(self):
        """Test Unicode support."""
        content = "{{greeting}} {{name}}! {{emoji}}"
        variables = {
            'greeting': 'こんにちは',
            'name': 'José',
            'emoji': '🎉'
        }
        rendered, warnings = substitute_variables(content, variables)
        self.assertEqual(rendered, "こんにちは José! 🎉")


if __name__ == '__main__':
    unittest.main()
