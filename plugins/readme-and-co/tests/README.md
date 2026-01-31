# readme-and-co Tests

Comprehensive integration tests for the readme-and-co plugin.

## Test Coverage

### Test Files

1. **test_render_template.py** (32 tests)
   - Variable substitution
   - Template validation
   - Error handling
   - Edge cases (Unicode, special characters, etc.)

2. **test_detect_project_info.py** (43 tests)
   - Language detection
   - Package manager detection
   - Framework detection
   - Test framework detection
   - CI/CD system detection
   - Documentation file detection
   - Content type classification
   - Monorepo detection

3. **test_populate_license.py** (34 tests)
   - License template discovery
   - Variable substitution (all three syntaxes: `[var]`, `${var}`, `{{var}}`)
   - Smart defaults from git and package.json
   - License name normalization
   - All 21+ license templates

4. **test_templates.py** (25 tests)
   - Template directory structure
   - README templates
   - LICENSE templates
   - CONTRIBUTING templates
   - GitHub templates (issues, PRs, CODEOWNERS, etc.)
   - Template naming conventions
   - Template content validation

**Total: 134 tests**

## Running Tests

### Run All Tests

```bash
# From plugin root directory
python3 -m unittest discover tests

# Verbose output
python3 -m unittest discover tests -v
```

### Run Specific Test File

```bash
# Render template tests
python3 -m unittest tests.test_render_template

# Project detection tests
python3 -m unittest tests.test_detect_project_info

# License population tests
python3 -m unittest tests.test_populate_license

# Template validation tests
python3 -m unittest tests.test_templates
```

### Run Specific Test Class

```bash
python3 -m unittest tests.test_render_template.TestValidateTemplate
```

### Run Specific Test Method

```bash
python3 -m unittest tests.test_render_template.TestValidateTemplate.test_validate_perfect_match
```

## Test Requirements

- **Python**: 3.9+
- **Dependencies**: None (uses only Python standard library)
- **Git**: Required for git config tests (optional, tests will skip if not available)

## Test Structure

```
tests/
├── README.md                      # This file
├── test_render_template.py        # Template rendering tests
├── test_detect_project_info.py    # Project analysis tests
├── test_populate_license.py       # License population tests
├── test_templates.py              # Template validation tests
└── fixtures/                      # Test data (auto-created during tests)
```

## What Tests Cover

### Script Integration Tests

- **End-to-end workflows**: Complete workflows from CLI invocation to file output
- **Auto-detection**: Git config and package.json parsing
- **Error handling**: Invalid input, missing files, malformed JSON
- **Edge cases**: Unicode, special characters, empty values, large files

### Template Tests

- **Template availability**: All expected templates exist
- **Template structure**: Proper directory organization
- **Template syntax**: Valid variable placeholders
- **Template rendering**: All templates can be rendered without errors
- **Naming conventions**: Consistent `.template.*` naming

### Validation Tests

- **Variable detection**: Finding all `{{variable}}` placeholders
- **Missing variable detection**: Identifying required variables not provided
- **Unused variable detection**: Identifying provided variables not used
- **Validation reporting**: Structured errors, warnings, and info messages

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```bash
# Exit code 0 if all tests pass
python3 -m unittest discover tests

# Exit code 1 if any test fails
echo $?
```

## Adding New Tests

When adding new features or templates:

1. **Add tests first** (TDD approach)
2. **Test both success and failure cases**
3. **Include edge cases** (empty values, special characters, etc.)
4. **Use descriptive test names** (`test_<what>_<condition>_<expected>`)
5. **Add docstrings** explaining what each test validates

### Example Test

```python
def test_render_with_unicode_variables(self):
    """Test that Unicode characters in variables are handled correctly."""
    content = "Hello {{name}}!"
    variables = {'name': 'José 🎉'}
    rendered, warnings = substitute_variables(content, variables)

    self.assertEqual(rendered, "Hello José 🎉!")
    self.assertEqual(warnings, [])
```

## Test Isolation

All tests use temporary directories and clean up after themselves:

```python
def setUp(self):
    """Create temporary directory for test files."""
    self.temp_dir = tempfile.mkdtemp()
    self.temp_path = Path(self.temp_dir)

def tearDown(self):
    """Clean up temporary files."""
    import shutil
    shutil.rmtree(self.temp_dir)
```

This ensures:
- No test pollution between runs
- No modification of actual plugin files
- Tests can run in parallel (if needed)

## Debugging Failed Tests

### Verbose Output

```bash
# See detailed test output
python3 -m unittest tests.test_render_template -v
```

### Run Single Test

```bash
# Focus on one failing test
python3 -m unittest tests.test_render_template.TestValidateTemplate.test_validate_missing_variables -v
```

### Use Python Debugger

```python
import pdb; pdb.set_trace()  # Add to test code
```

## Coverage Goals

- **Line coverage**: 95%+
- **Branch coverage**: 90%+
- **Function coverage**: 95%+

To measure coverage (requires `coverage` package):

```bash
pip install coverage
coverage run -m unittest discover tests
coverage report
coverage html  # Generate HTML report
```

## Future Test Additions

Planned test coverage (from review report):

- [ ] **Hook tests**: Test PreToolUse/PostToolUse hooks (Task #7)
- [ ] **Agent tests**: Test doc-generator agent workflows (Task #5)
- [ ] **Preview mode tests**: Test --preview flag functionality (Task #11)
- [ ] **Config tests**: Test local configuration support (Task #8)
- [ ] **Monorepo tests**: Test monorepo template generation (Task #12)

## Notes

- Tests use only Python standard library (no external dependencies)
- All file I/O uses temporary directories
- Tests are OS-agnostic (work on macOS, Linux, Windows)
- Git operations have fallbacks if git is not available
- Template existence tests skip gracefully if templates not yet created
