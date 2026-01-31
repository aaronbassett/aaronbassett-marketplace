#!/usr/bin/env python3
"""
Integration tests for detect_project_info.py

Tests cover:
- Language detection
- Package manager detection
- Framework detection
- Test framework detection
- CI/CD detection
- Documentation file detection
- Content type classification
- Monorepo detection
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path to import the script
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from detect_project_info import (
    detect_languages,
    detect_package_managers,
    detect_frameworks,
    detect_test_frameworks,
    detect_ci_cd,
    detect_existing_docs,
    detect_content_type,
    detect_monorepo,
    analyze_repository,
)


class TestDetectLanguages(unittest.TestCase):
    """Test programming language detection."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_detect_python_from_file(self):
        """Test Python detection from requirements.txt."""
        (self.temp_path / 'requirements.txt').touch()
        languages = detect_languages(self.temp_path)
        self.assertIn('python', languages)

    def test_detect_python_from_extension(self):
        """Test Python detection from .py files."""
        (self.temp_path / 'main.py').touch()
        languages = detect_languages(self.temp_path)
        self.assertIn('python', languages)

    def test_detect_javascript_from_package_json(self):
        """Test JavaScript detection from package.json."""
        (self.temp_path / 'package.json').touch()
        languages = detect_languages(self.temp_path)
        self.assertIn('javascript', languages)

    def test_detect_typescript(self):
        """Test TypeScript detection."""
        (self.temp_path / 'tsconfig.json').touch()
        languages = detect_languages(self.temp_path)
        self.assertIn('typescript', languages)

    def test_detect_rust(self):
        """Test Rust detection."""
        (self.temp_path / 'Cargo.toml').touch()
        languages = detect_languages(self.temp_path)
        self.assertIn('rust', languages)

    def test_detect_go(self):
        """Test Go detection."""
        (self.temp_path / 'go.mod').touch()
        languages = detect_languages(self.temp_path)
        self.assertIn('go', languages)

    def test_detect_multiple_languages(self):
        """Test detection of multiple languages."""
        (self.temp_path / 'main.py').touch()
        (self.temp_path / 'package.json').touch()
        (self.temp_path / 'Cargo.toml').touch()

        languages = detect_languages(self.temp_path)
        self.assertIn('python', languages)
        self.assertIn('javascript', languages)
        self.assertIn('rust', languages)

    def test_no_languages(self):
        """Test empty directory returns no languages."""
        languages = detect_languages(self.temp_path)
        self.assertEqual(languages, [])


class TestDetectPackageManagers(unittest.TestCase):
    """Test package manager detection."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_detect_npm(self):
        """Test npm detection."""
        (self.temp_path / 'package.json').touch()
        (self.temp_path / 'package-lock.json').touch()
        managers = detect_package_managers(self.temp_path)
        self.assertIn('npm', managers)

    def test_detect_yarn(self):
        """Test yarn detection."""
        (self.temp_path / 'package.json').touch()
        (self.temp_path / 'yarn.lock').touch()
        managers = detect_package_managers(self.temp_path)
        self.assertIn('yarn', managers)

    def test_detect_pnpm(self):
        """Test pnpm detection."""
        (self.temp_path / 'package.json').touch()
        (self.temp_path / 'pnpm-lock.yaml').touch()
        managers = detect_package_managers(self.temp_path)
        self.assertIn('pnpm', managers)

    def test_detect_pip(self):
        """Test pip detection."""
        (self.temp_path / 'requirements.txt').touch()
        managers = detect_package_managers(self.temp_path)
        self.assertIn('pip', managers)

    def test_detect_poetry(self):
        """Test poetry detection."""
        (self.temp_path / 'pyproject.toml').touch()
        managers = detect_package_managers(self.temp_path)
        self.assertIn('poetry', managers)

    def test_detect_cargo(self):
        """Test cargo detection."""
        (self.temp_path / 'Cargo.toml').touch()
        managers = detect_package_managers(self.temp_path)
        self.assertIn('cargo', managers)

    def test_detect_go_modules(self):
        """Test Go modules detection."""
        (self.temp_path / 'go.mod').touch()
        managers = detect_package_managers(self.temp_path)
        self.assertIn('go modules', managers)


class TestDetectFrameworks(unittest.TestCase):
    """Test framework detection."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_detect_react_from_package_json(self):
        """Test React detection from package.json."""
        package_json = {
            "name": "test-app",
            "dependencies": {
                "react": "^18.0.0"
            }
        }
        (self.temp_path / 'package.json').write_text(json.dumps(package_json))

        frameworks = detect_frameworks(self.temp_path)
        self.assertIn('react', frameworks)

    def test_detect_fastapi_from_requirements(self):
        """Test FastAPI detection from requirements.txt."""
        (self.temp_path / 'requirements.txt').write_text('fastapi==0.100.0\nuvicorn')

        frameworks = detect_frameworks(self.temp_path)
        self.assertIn('fastapi', frameworks)

    def test_detect_django(self):
        """Test Django detection."""
        (self.temp_path / 'requirements.txt').write_text('Django==4.2.0')

        frameworks = detect_frameworks(self.temp_path)
        self.assertIn('django', frameworks)

    def test_detect_express(self):
        """Test Express detection."""
        package_json = {
            "dependencies": {
                "express": "^4.18.0"
            }
        }
        (self.temp_path / 'package.json').write_text(json.dumps(package_json))

        frameworks = detect_frameworks(self.temp_path)
        self.assertIn('express', frameworks)

    def test_invalid_json_handled(self):
        """Test that invalid JSON doesn't crash detection."""
        (self.temp_path / 'package.json').write_text('invalid json{')

        # Should not raise exception
        frameworks = detect_frameworks(self.temp_path)
        self.assertEqual(frameworks, [])


class TestDetectTestFrameworks(unittest.TestCase):
    """Test testing framework detection."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_detect_pytest_from_file(self):
        """Test pytest detection from pytest.ini."""
        (self.temp_path / 'pytest.ini').touch()
        tests = detect_test_frameworks(self.temp_path)
        self.assertIn('pytest', tests)

    def test_detect_jest_from_package_json(self):
        """Test Jest detection from package.json."""
        package_json = {
            "devDependencies": {
                "jest": "^29.0.0"
            }
        }
        (self.temp_path / 'package.json').write_text(json.dumps(package_json))

        tests = detect_test_frameworks(self.temp_path)
        self.assertIn('jest', tests)


class TestDetectCICD(unittest.TestCase):
    """Test CI/CD system detection."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_detect_github_actions(self):
        """Test GitHub Actions detection."""
        workflows_dir = self.temp_path / '.github' / 'workflows'
        workflows_dir.mkdir(parents=True)
        (workflows_dir / 'ci.yml').touch()

        ci_systems = detect_ci_cd(self.temp_path)
        self.assertIn('github-actions', ci_systems)

    def test_detect_gitlab_ci(self):
        """Test GitLab CI detection."""
        (self.temp_path / '.gitlab-ci.yml').touch()

        ci_systems = detect_ci_cd(self.temp_path)
        self.assertIn('gitlab-ci', ci_systems)

    def test_detect_travis(self):
        """Test Travis CI detection."""
        (self.temp_path / '.travis.yml').touch()

        ci_systems = detect_ci_cd(self.temp_path)
        self.assertIn('travis', ci_systems)


class TestDetectExistingDocs(unittest.TestCase):
    """Test documentation file detection."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_detect_readme(self):
        """Test README detection."""
        (self.temp_path / 'README.md').touch()
        docs = detect_existing_docs(self.temp_path)
        self.assertTrue(docs['readme.md'])

    def test_detect_license(self):
        """Test LICENSE detection."""
        (self.temp_path / 'LICENSE').touch()
        docs = detect_existing_docs(self.temp_path)
        self.assertTrue(docs['license'])

    def test_detect_contributing(self):
        """Test CONTRIBUTING detection."""
        (self.temp_path / 'CONTRIBUTING.md').touch()
        docs = detect_existing_docs(self.temp_path)
        self.assertTrue(docs['contributing.md'])

    def test_detect_github_templates(self):
        """Test GitHub template detection."""
        github_dir = self.temp_path / '.github'
        github_dir.mkdir()

        # PR template
        (github_dir / 'pull_request_template.md').touch()

        # Issue templates
        issue_dir = github_dir / 'ISSUE_TEMPLATE'
        issue_dir.mkdir()

        # CODEOWNERS
        (github_dir / 'CODEOWNERS').touch()

        # FUNDING
        (github_dir / 'FUNDING.yml').touch()

        docs = detect_existing_docs(self.temp_path)
        self.assertTrue(docs['pr_template'])
        self.assertTrue(docs['issue_templates'])
        self.assertTrue(docs['codeowners'])
        self.assertTrue(docs['funding'])

    def test_missing_docs_are_false(self):
        """Test that missing docs return False."""
        docs = detect_existing_docs(self.temp_path)
        self.assertFalse(docs['readme.md'])
        self.assertFalse(docs['license'])
        self.assertFalse(docs['contributing.md'])


class TestDetectContentType(unittest.TestCase):
    """Test content type classification."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_code_only_project(self):
        """Test project with only code files."""
        (self.temp_path / 'main.py').touch()
        (self.temp_path / 'utils.py').touch()
        (self.temp_path / 'helpers.py').touch()

        content_type = detect_content_type(self.temp_path, ['python'])
        self.assertEqual(content_type, 'code')

    def test_documentation_only_project(self):
        """Test project with only documentation."""
        (self.temp_path / 'README.md').touch()
        (self.temp_path / 'guide.md').touch()
        (self.temp_path / 'tutorial.md').touch()

        content_type = detect_content_type(self.temp_path, [])
        self.assertEqual(content_type, 'documentation')

    def test_mixed_project(self):
        """Test project with both code and docs."""
        (self.temp_path / 'main.py').touch()
        (self.temp_path / 'README.md').touch()

        content_type = detect_content_type(self.temp_path, ['python'])
        self.assertEqual(content_type, 'mixed')


class TestDetectMonorepo(unittest.TestCase):
    """Test monorepo detection."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_detect_packages_directory(self):
        """Test monorepo detection from packages/ directory."""
        (self.temp_path / 'packages').mkdir()
        is_monorepo = detect_monorepo(self.temp_path)
        self.assertTrue(is_monorepo)

    def test_detect_apps_directory(self):
        """Test monorepo detection from apps/ directory."""
        (self.temp_path / 'apps').mkdir()
        is_monorepo = detect_monorepo(self.temp_path)
        self.assertTrue(is_monorepo)

    def test_detect_lerna_json(self):
        """Test monorepo detection from lerna.json."""
        (self.temp_path / 'lerna.json').touch()
        is_monorepo = detect_monorepo(self.temp_path)
        self.assertTrue(is_monorepo)

    def test_detect_nx_json(self):
        """Test monorepo detection from nx.json."""
        (self.temp_path / 'nx.json').touch()
        is_monorepo = detect_monorepo(self.temp_path)
        self.assertTrue(is_monorepo)

    def test_not_monorepo(self):
        """Test non-monorepo project."""
        (self.temp_path / 'main.py').touch()
        is_monorepo = detect_monorepo(self.temp_path)
        self.assertFalse(is_monorepo)


class TestAnalyzeRepository(unittest.TestCase):
    """Test complete repository analysis."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_analyze_python_project(self):
        """Test analyzing a Python project."""
        # Create Python project structure
        (self.temp_path / 'main.py').touch()
        (self.temp_path / 'requirements.txt').write_text('pytest\nfastapi')
        (self.temp_path / 'README.md').touch()
        (self.temp_path / 'LICENSE').touch()

        workflows_dir = self.temp_path / '.github' / 'workflows'
        workflows_dir.mkdir(parents=True)
        (workflows_dir / 'ci.yml').touch()

        result = analyze_repository(str(self.temp_path))

        # Check results
        self.assertIn('python', result['languages'])
        self.assertIn('pip', result['package_managers'])
        self.assertIn('fastapi', result['frameworks'])
        self.assertIn('github-actions', result['ci_cd'])
        self.assertTrue(result['existing_docs']['readme.md'])
        self.assertTrue(result['existing_docs']['license'])
        self.assertFalse(result['is_monorepo'])
        self.assertEqual(result['primary_language'], 'python')

    def test_analyze_javascript_project(self):
        """Test analyzing a JavaScript project."""
        # Create JavaScript project
        package_json = {
            "name": "test-app",
            "dependencies": {
                "react": "^18.0.0",
                "express": "^4.18.0"
            },
            "devDependencies": {
                "jest": "^29.0.0"
            }
        }
        (self.temp_path / 'package.json').write_text(json.dumps(package_json))
        (self.temp_path / 'package-lock.json').touch()
        (self.temp_path / 'index.js').touch()

        result = analyze_repository(str(self.temp_path))

        self.assertIn('javascript', result['languages'])
        self.assertIn('npm', result['package_managers'])
        self.assertIn('react', result['frameworks'])
        self.assertIn('express', result['frameworks'])
        self.assertIn('jest', result['test_frameworks'])

    def test_analyze_monorepo(self):
        """Test analyzing a monorepo."""
        (self.temp_path / 'packages').mkdir()
        (self.temp_path / 'lerna.json').touch()
        (self.temp_path / 'package.json').touch()

        result = analyze_repository(str(self.temp_path))

        self.assertTrue(result['is_monorepo'])

    def test_analyze_nonexistent_path(self):
        """Test analyzing nonexistent path returns error."""
        result = analyze_repository('/path/that/does/not/exist')

        self.assertIn('error', result)

    def test_analyze_current_directory(self):
        """Test analyzing without path uses current directory."""
        result = analyze_repository()

        # Should return valid structure
        self.assertIn('languages', result)
        self.assertIn('package_managers', result)
        self.assertIn('frameworks', result)


if __name__ == '__main__':
    unittest.main()
