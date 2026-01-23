---
name: flutter-build
description: Build and package Flutter applications for multiple platforms with code signing, obfuscation, and release optimization
argument-hint: <android|ios|web|windows|macos|linux|all> [release|debug|profile] [--flavor=<name>] [--obfuscate]
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - AskUserQuestion
---

# Flutter Multi-Platform Build Manager

This command orchestrates building and packaging Flutter applications for all supported platforms with production-ready configurations, code signing, and optimization.

## Usage

```bash
/flutter-build <platform> [mode] [options]
```

## Platforms

- `android` - Build APK/AAB for Android
- `ios` - Build IPA for iOS (macOS only)
- `web` - Build web app
- `windows` - Build Windows executable
- `macos` - Build macOS app (macOS only)
- `linux` - Build Linux app (Linux/macOS only)
- `all` - Build for all available platforms

## Build Modes

- `release` - Production build (default)
- `debug` - Debug build with assertions
- `profile` - Performance profiling build

## Options

- `--flavor=<name>` - Build flavor (dev, staging, prod)
- `--obfuscate` - Obfuscate Dart code
- `--split-per-abi` - Create separate APKs per ABI (Android)
- `--bundle` - Create app bundle instead of APK (Android)
- `--export-method=<method>` - iOS export method (app-store, ad-hoc, enterprise, development)
- `--codesign` - Code sign the build (required for iOS/macOS distribution)
- `--analyze-size` - Generate size analysis report

## Examples

```bash
# Android release build
/flutter-build android release

# iOS App Store build with obfuscation
/flutter-build ios release --export-method=app-store --obfuscate --codesign

# Android bundle with flavor
/flutter-build android release --bundle --flavor=prod

# Multi-platform release
/flutter-build all release --obfuscate

# Web with size analysis
/flutter-build web release --analyze-size

# Development build for testing
/flutter-build android debug --flavor=dev
```

## Implementation

When this command runs:

### 1. **Pre-build Validation**

Check environment and prerequisites:

```bash
# Verify Flutter installation
flutter doctor -v

# Check we're in a Flutter project
if [ ! -f "pubspec.yaml" ]; then
  echo "Error: Not a Flutter project"
  exit 1
fi

# Verify platform support
flutter config
```

**Platform-Specific Checks:**

**Android:**
- Check Java/Gradle installation
- Verify Android SDK setup
- Check for keystore (release mode)

**iOS/macOS:**
- Verify running on macOS
- Check Xcode installation
- Verify provisioning profiles and certificates
- Check CocoaPods installation

**Web:**
- Check for web dependencies
- Verify build configuration

**Windows:**
- Check Visual Studio installation (Windows)
- Verify C++ build tools

**Linux:**
- Check GTK development libraries
- Verify build essentials

### 2. **Parse Build Configuration**

Extract configuration from arguments and project files:

```dart
// Read from pubspec.yaml
final config = {
  'name': packageName,
  'version': version,
  'build_number': buildNumber,
};

// Check for flavor configurations
final flavorConfig = flavor != null
  ? readFlavorConfig(flavor)
  : null;
```

Check for build configuration files:
- `android/app/build.gradle` - Android config
- `ios/Runner.xcodeproj` - iOS config
- `web/index.html` - Web config
- `build.yaml` - Build settings

### 3. **Pre-build Steps**

Clean and prepare:

```bash
# Clean previous builds
flutter clean

# Get dependencies
flutter pub get

# Run code generation if needed
if grep -q "build_runner" pubspec.yaml; then
  flutter pub run build_runner build --delete-conflicting-outputs
fi

# Run analysis
flutter analyze
```

If analysis has errors (release mode):
```
⚠️ Analysis found errors. Building with errors may cause runtime issues.

Continue anyway? (y/n)
```

### 4. **Build for Platform**

Execute platform-specific builds:

#### **Android Build**

**APK Build:**
```bash
flutter build apk \
  --release \
  ${flavor:+--flavor=$flavor} \
  ${obfuscate:+--obfuscate --split-debug-info=./debug-info} \
  ${split_abi:+--split-per-abi} \
  --target-platform android-arm,android-arm64,android-x64
```

**App Bundle Build:**
```bash
flutter build appbundle \
  --release \
  ${flavor:+--flavor=$flavor} \
  ${obfuscate:+--obfuscate --split-debug-info=./debug-info}
```

Output locations:
- APK: `build/app/outputs/flutter-apk/app-release.apk`
- AAB: `build/app/outputs/bundle/release/app-release.aab`

**Code Signing** (release):
```bash
# Verify keystore exists
if [ ! -f "$KEYSTORE_PATH" ]; then
  echo "Error: Keystore not found"
  echo "Create keystore: keytool -genkey -v -keystore release.jks ..."
  exit 1
fi

# Sign APK
jarsigner -verbose \
  -sigalg SHA256withRSA \
  -digestalg SHA-256 \
  -keystore $KEYSTORE_PATH \
  app-release.apk \
  $KEY_ALIAS

# Zipalign
zipalign -v 4 app-release.apk app-release-aligned.apk
```

#### **iOS Build**

```bash
# Build iOS app
flutter build ios \
  --release \
  ${flavor:+--flavor=$flavor} \
  ${obfuscate:+--obfuscate --split-debug-info=./debug-info} \
  ${no_codesign:+--no-codesign}

# Create archive (if codesigning)
if [ "$codesign" = true ]; then
  xcodebuild -workspace ios/Runner.xcworkspace \
    -scheme Runner \
    -configuration Release \
    -archivePath build/ios/archive/Runner.xcarchive \
    archive

  # Export IPA
  xcodebuild -exportArchive \
    -archivePath build/ios/archive/Runner.xcarchive \
    -exportPath build/ios/ipa \
    -exportOptionsPlist ios/ExportOptions.plist
fi
```

Output: `build/ios/ipa/Runner.ipa`

**Provisioning Profile Check:**
```bash
# List available profiles
security find-identity -v -p codesigning

# Verify profile matches bundle ID
```

#### **Web Build**

```bash
flutter build web \
  --release \
  --web-renderer canvaskit \
  ${obfuscate:+--source-maps}

# Optimize assets
if command -v gzip &> /dev/null; then
  find build/web -type f \( -name '*.js' -o -name '*.css' -o -name '*.html' \) \
    -exec gzip -k {} \;
fi
```

Output: `build/web/`

**Web Optimization:**
```bash
# Create service worker
# Configure caching strategy
# Optimize images
# Generate manifest.json
```

#### **Windows Build**

```bash
flutter build windows \
  --release \
  ${obfuscate:+--obfuscate --split-debug-info=./debug-info}

# Create installer (optional)
if command -v iscc &> /dev/null; then
  iscc windows/installer.iss
fi
```

Output: `build/windows/runner/Release/`

#### **macOS Build**

```bash
flutter build macos \
  --release \
  ${obfuscate:+--obfuscate --split-debug-info=./debug-info}

# Code sign (if required)
if [ "$codesign" = true ]; then
  codesign --deep --force \
    --sign "$DEVELOPER_ID" \
    build/macos/Build/Products/Release/your_app.app

  # Notarize (for distribution)
  xcrun notarytool submit \
    build/macos/Build/Products/Release/your_app.app \
    --apple-id "$APPLE_ID" \
    --password "$APP_PASSWORD" \
    --team-id "$TEAM_ID"
fi
```

Output: `build/macos/Build/Products/Release/your_app.app`

#### **Linux Build**

```bash
flutter build linux \
  --release \
  ${obfuscate:+--obfuscate --split-debug-info=./debug-info}

# Create package (optional)
# - .deb package
# - AppImage
# - Snap
```

Output: `build/linux/x64/release/bundle/`

### 5. **Build Artifacts Analysis**

Analyze build output:

```bash
# Calculate sizes
du -sh build/*/

# For Android
apkanalyzer apk summary app-release.apk

# For iOS
xcrun dyld_info -size Runner.app/Runner

# Generate size breakdown
flutter build apk --analyze-size --target-platform android-arm64
```

Create size report:
```
Build Size Analysis
===================

Platform: Android (ARM64)
Total size: 15.2 MB

Breakdown:
  Code (Dart):     8.3 MB (55%)
  Assets:          4.2 MB (28%)
  Native libs:     2.1 MB (14%)
  Resources:       0.6 MB (3%)

Largest assets:
  1. assets/images/splash.png - 1.2 MB
  2. assets/fonts/Roboto.ttf - 0.8 MB
  3. assets/data/cities.json - 0.5 MB

Recommendations:
  - Compress splash image (PNG → WebP)
  - Use variable fonts to reduce font size
  - Consider code splitting for large apps
```

### 6. **Flavor Configuration** (if --flavor specified)

Handle build flavors:

**Android (build.gradle):**
```gradle
android {
    flavorDimensions "environment"
    productFlavors {
        dev {
            dimension "environment"
            applicationIdSuffix ".dev"
            versionNameSuffix "-dev"
        }
        prod {
            dimension "environment"
        }
    }
}
```

**iOS (Scheme configuration):**
- Create separate schemes for each flavor
- Configure bundle IDs
- Set app icons per flavor

**Flutter (dart-defines):**
```bash
flutter build apk --dart-define=FLAVOR=prod --dart-define=API_URL=https://api.prod.com
```

### 7. **Post-build Steps**

After successful build:

```bash
# Run built app (debug/profile mode)
if [ "$mode" != "release" ]; then
  flutter install
fi

# Copy artifacts to distribution folder
mkdir -p dist/
cp build/app/outputs/flutter-apk/*.apk dist/

# Generate checksums
sha256sum dist/*.apk > dist/checksums.txt

# Create build manifest
cat > dist/build-manifest.json <<EOF
{
  "version": "$version",
  "build_number": "$build_number",
  "platform": "$platform",
  "mode": "$mode",
  "flavor": "$flavor",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "git_commit": "$(git rev-parse HEAD)",
  "obfuscated": $obfuscate
}
EOF
```

### 8. **Generate Build Report**

Create comprehensive build report:

```markdown
# Flutter Build Report

## Build Information
- Platform: Android
- Mode: Release
- Flavor: prod
- Date: 2026-01-23 16:30:00
- Git Commit: a1b2c3d4

## Configuration
- Obfuscation: ✓ Enabled
- Code Signing: ✓ Signed
- Bundle: ✓ AAB created
- Split ABIs: ✓ Enabled

## Build Artifacts
- `app-arm64-v8a-release.apk` (12.1 MB)
- `app-armeabi-v7a-release.apk` (13.5 MB)
- `app-x86_64-release.apk` (14.2 MB)
- `app-release.aab` (28.5 MB)

## Size Analysis
- Total APK size: 12.1 MB (ARM64)
- 23% smaller than previous build
- Dart code: 6.8 MB
- Native code: 3.2 MB
- Assets: 2.1 MB

## Quality Checks
- ✓ Analysis: No issues
- ✓ Tests: 177/177 passed
- ✓ Code signing: Valid
- ✓ Permissions: Reviewed

## Distribution
- Location: `dist/`
- Checksum: SHA256 available
- Upload to: Play Console

## Next Steps
1. Test on physical devices
2. Submit to Play Store
3. Monitor crash reports
```

### 9. **Platform-Specific Distribution Guidance**

**Android:**
```
Google Play Console Upload:
1. Go to: https://play.google.com/console
2. Select your app
3. Navigate to: Release > Production
4. Upload: app-release.aab
5. Fill release notes
6. Submit for review
```

**iOS:**
```
App Store Connect Upload:
1. Open Xcode
2. Window > Organizer
3. Select archive
4. Distribute App > App Store Connect
5. Upload
6. Go to: https://appstoreconnect.apple.com
7. Submit for review
```

**Web:**
```
Deploy to hosting:

Firebase:
  firebase deploy --only hosting

GitHub Pages:
  cp -r build/web/* docs/
  git add docs/ && git commit -m "Deploy web build"
  git push

Custom server:
  rsync -avz build/web/ user@server:/var/www/html/
```

### 10. **Error Handling**

Common build errors and solutions:

**Android:**
- **Keystore not found**: Guide creating release keystore
- **Build tools missing**: Run `flutter doctor --android-licenses`
- **Gradle errors**: Clean and rebuild

**iOS:**
- **Signing issues**: Check certificates and profiles
- **CocoaPods errors**: Run `cd ios && pod install`
- **Architecture errors**: Update Xcode

**All Platforms:**
- **Dependency errors**: Run `flutter pub get`
- **Analysis errors**: Fix before building release
- **Out of memory**: Increase heap size

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: subosito/flutter-action@v2
      - name: Build Android
        run: /flutter-build android release --bundle --obfuscate
      - name: Upload to Play Store
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.PLAY_STORE_JSON }}
          packageName: com.example.app
          releaseFiles: build/app/outputs/bundle/release/*.aab

  build-ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: subosito/flutter-action@v2
      - name: Build iOS
        run: /flutter-build ios release --export-method=app-store --codesign
      - name: Upload to App Store
        uses: apple-actions/upload-testflight-build@v1
        with:
          app-path: build/ios/ipa/Runner.ipa
          issuer-id: ${{ secrets.APPSTORE_ISSUER_ID }}
          api-key-id: ${{ secrets.APPSTORE_KEY_ID }}
```

## Related Skills

- **flutter-deployment** - Detailed deployment guides per platform
- **flutter-performance** - Optimization before building
- **flutter-testing-quality** - Testing before release

## Tips

- Always test release builds on physical devices
- Use flavors to separate dev/staging/prod
- Enable obfuscation for production builds
- Monitor app size - target <15MB for Android
- Keep debug symbols for crash reporting
- Automate builds with CI/CD
- Version bumps: flutter pub run cider bump patch/minor/major
