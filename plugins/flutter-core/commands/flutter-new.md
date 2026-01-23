---
name: flutter-new
description: Create a new Flutter project with templates, state management setup, and best practice configuration
argument-hint: <project-name> [template] [--state-management=<provider|bloc|riverpod>]
allowed-tools:
  - Bash
  - Write
  - Read
  - Edit
  - AskUserQuestion
---

# Create New Flutter Project

This command creates a new Flutter project with optional templates and pre-configured state management, architecture patterns, and development tools.

## Usage

```bash
/flutter-new <project-name> [template] [options]
```

## Templates

- `basic` - Minimal Flutter app (default)
- `material3` - Material Design 3 with theming
- `clean-arch` - Clean architecture structure
- `full-stack` - Flutter app + ServerPod backend

## Options

- `--state-management=<provider|bloc|riverpod>` - Pre-configure state management
- `--platforms=<android,ios,web,windows,macos,linux>` - Enable specific platforms
- `--org=<com.example>` - Organization identifier

## Examples

```bash
# Basic Material 3 app
/flutter-new my_app material3

# Clean architecture with BLoC
/flutter-new my_app clean-arch --state-management=bloc

# Full-stack app with ServerPod
/flutter-new my_backend full-stack

# Web-only app with Riverpod
/flutter-new my_web_app basic --platforms=web --state-management=riverpod
```

## Implementation

When this command runs:

1. **Parse Arguments**
   - Extract project name (required)
   - Extract template (default: basic)
   - Parse options (state management, platforms, org)
   - Validate project name (lowercase, underscores only)

2. **Ask for Clarifications** (if needed)
   - If no template specified, ask which template
   - If no state management specified for non-basic template, ask preference
   - If no platforms specified, use Flutter defaults

3. **Create Base Project**
   ```bash
   flutter create \
     --project-name=<project_name> \
     --org=<org_id> \
     --platforms=<platforms> \
     <project_name>
   ```

4. **Apply Template**
   Based on selected template:

   **material3** template:
   - Update `lib/main.dart` with Material 3 theming
   - Add `ThemeData` with `useMaterial3: true`
   - Configure `ColorScheme.fromSeed()`
   - Add dark theme support
   - Create `lib/theme/` directory with theme configuration

   **clean-arch** template:
   - Create directory structure:
     ```
     lib/
     ├── core/
     │   ├── error/
     │   ├── network/
     │   └── utils/
     ├── features/
     │   └── example/
     │       ├── data/
     │       │   ├── datasources/
     │       │   ├── models/
     │       │   └── repositories/
     │       ├── domain/
     │       │   ├── entities/
     │       │   ├── repositories/
     │       │   └── usecases/
     │       └── presentation/
     │           ├── pages/
     │           └── widgets/
     └── main.dart
     ```
   - Add dependency injection setup (get_it)
   - Create example feature with complete layers

   **full-stack** template:
   - Create Flutter client in `<project_name>_client/`
   - Create ServerPod backend in `<project_name>_server/`
   - Configure both projects
   - Set up shared models

5. **Configure State Management** (if specified)

   **provider**:
   - Add `provider: ^6.1.0` to pubspec.yaml
   - Create `lib/providers/` directory
   - Add example ChangeNotifier
   - Update main.dart with MultiProvider

   **bloc**:
   - Add `flutter_bloc: ^8.1.0` to pubspec.yaml
   - Create `lib/bloc/` directory
   - Add example Bloc with events/states
   - Update main.dart with BlocProvider

   **riverpod**:
   - Add `flutter_riverpod: ^2.4.0` to pubspec.yaml
   - Create `lib/providers/` directory
   - Add example providers
   - Update main.dart with ProviderScope

6. **Add Development Tools**
   - Add to pubspec.yaml:
     ```yaml
     dev_dependencies:
       flutter_test:
         sdk: flutter
       flutter_lints: ^3.0.0
       build_runner: ^2.4.0
     ```
   - Create `analysis_options.yaml` with strict linting
   - Create `.gitignore` with Flutter entries
   - Initialize git repository

7. **Run Initial Setup**
   ```bash
   cd <project_name>
   flutter pub get
   ```

8. **Create README**
   Generate README.md with:
   - Project description
   - Template and state management used
   - Getting started instructions
   - Available commands
   - Project structure overview

9. **Display Summary**
   Show user:
   - Project created successfully message
   - Directory location
   - Template applied
   - State management configured
   - Next steps:
     ```
     cd <project_name>
     flutter run
     ```

## Error Handling

- **Invalid project name**: Show error with naming rules
- **Flutter not installed**: Check with `flutter --version`, guide installation
- **Directory already exists**: Ask to overwrite or choose different name
- **Template not found**: List available templates
- **Unsupported platform**: Show supported platforms for current Flutter version

## Tips

- Project names must be lowercase with underscores (e.g., `my_app`, not `MyApp`)
- Use clean-arch template for medium to large applications
- Use basic or material3 for small apps or prototypes
- Consider full-stack template if you need a Dart backend
- State management can be added later if unsure

## Related Skills

Reference these skills for more information:
- **flutter-ui-widgets** - Material Design 3 theming
- **flutter-state-management** - Choosing state management approach
- **flutter-architecture** - Clean architecture patterns
- **flutter-serverpod** - ServerPod backend setup
