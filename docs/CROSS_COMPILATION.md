# Cross-Platform Build Guide for Storymaster

This guide explains how to build Storymaster for multiple platforms, including building macOS versions from Linux.

## 🎯 Build Matrix

| Target Platform | Build Platform | Method | Difficulty |
|------------------|----------------|---------|------------|
| Windows | Windows | PyInstaller | Easy ✅ |
| Windows | Linux | PyInstaller + Wine | Medium 🟡 |
| macOS | macOS | Native build | Easy ✅ |
| macOS | Linux | Cross-compilation | Hard 🔴 |
| Linux | Linux | Native build | Easy ✅ |
| Linux | Any | Docker | Easy ✅ |

## 🖥️ Platform-Specific Instructions

### Windows from Linux

**Option 1: GitHub Actions (Recommended)**
```yaml
# Use the provided .github/workflows/build-releases.yml
# Automatically builds on Windows runners
```

**Option 2: Wine + PyInstaller**
```bash
# Install Wine
sudo apt install wine winetricks

# Install Python in Wine
winetricks python3

# Install dependencies in Wine environment  
wine pip install -r requirements.txt pyinstaller

# Build executable
wine python build_executable.py
```

### macOS from Linux

**Option 1: GitHub Actions (Recommended)**
```yaml
# Use the provided .github/workflows/build-releases.yml
# Automatically builds on macOS runners - no setup required!
```

**Option 2: OSXCross Toolchain**
```bash
# 1. Install OSXCross (requires macOS SDK)
git clone https://github.com/tpoechtrager/osxcross
cd osxcross

# 2. Download macOS SDK (legally - from Xcode)
# Place MacOSX10.15.sdk.tar.xz in tarballs/

# 3. Build toolchain
./build.sh

# 4. Set environment
export OSXCROSS_ROOT=/opt/osxcross
export OSXCROSS_HOST=x86_64-apple-darwin19
export OSXCROSS_TARGET_DIR=$OSXCROSS_ROOT/target
export PATH=$OSXCROSS_TARGET_DIR/bin:$PATH

# 5. Build Storymaster
python build_macos.py
```

**Option 3: Docker with OSXCross**
```dockerfile
FROM ubuntu:20.04

# Install OSXCross in container
RUN apt-get update && apt-get install -y \
    clang git patch python3 python3-pip \
    libxml2-dev libssl-dev cmake

# Build toolchain in container
# ... (OSXCross setup)

# Build application
COPY . /app
WORKDIR /app
RUN python3 build_macos.py
```

**Option 4: Virtual Machine**
```bash
# Use macOS VM (legally - own hardware only)
# 1. Set up macOS VM on Mac hardware
# 2. Install Python and dependencies
# 3. Build natively with build_macos.py
```

## 🤖 Automated CI/CD (Recommended)

### GitHub Actions Setup

The provided workflow (`.github/workflows/build-releases.yml`) automatically builds for all platforms:

**Triggers:**
- Push tags starting with `v` (e.g., `v1.0.0`)
- Manual workflow dispatch

**Platforms:**
- ✅ Windows (windows-latest runner)
- ✅ macOS (macos-latest runner) 
- ✅ Linux (ubuntu-latest runner)

**Outputs:**
- Windows: `.exe` executable + `.zip` archive
- macOS: `.app` bundle + `.dmg` installer
- Linux: Executable + `.AppImage` + `.rpm` package

### Alternative CI Platforms

**GitLab CI:**
```yaml
stages:
  - build

build-windows:
  stage: build
  tags: [windows]
  script:
    - python build_executable.py

build-macos:
  stage: build  
  tags: [macos]
  script:
    - python build_macos.py

build-linux:
  stage: build
  tags: [linux]
  script:
    - python build_executable.py
    - python build_appimage.py
```

## 🐳 Docker Cross-Compilation

### Multi-Platform Docker Build

```dockerfile
# Dockerfile.multiplatform
FROM --platform=$BUILDPLATFORM python:3.11-slim AS base

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Build based on target platform
ARG TARGETPLATFORM
RUN if [ "$TARGETPLATFORM" = "linux/amd64" ]; then \
        python build_executable.py && \
        python build_appimage.py; \
    elif [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
        python build_executable.py; \
    fi
```

**Build commands:**
```bash
# Build for multiple architectures
docker buildx build --platform linux/amd64,linux/arm64 -t storymaster .

# Extract built artifacts
docker create --name temp storymaster
docker cp temp:/app/dist ./
docker rm temp
```

## 🎯 Build Strategies by Use Case

### For Development
```bash
# Quick local build
python build_executable.py
```

### For Testing
```bash
# Build all local formats
python build_all.py
```

### For Release
```bash
# Use GitHub Actions
git tag v1.0.0
git push origin v1.0.0
# Wait for automatic builds
```

### For Custom Deployment
```bash
# Specific platform builds
python build_executable.py    # Any platform
python build_appimage.py       # Linux universal
python build_rpm.py           # Linux RPM
python build_macos.py         # macOS (if supported)
```

## 🔧 Troubleshooting Cross-Compilation

### Common Issues

**PyInstaller Cross-Compilation:**
- ❌ PyInstaller doesn't fully support cross-compilation
- ✅ Use native runners or VMs for best results

**macOS Code Signing:**
- ❌ Can't sign from Linux without certificates
- ✅ Sign on macOS or use GitHub Actions

**Windows Antivirus:**
- ❌ May flag PyInstaller executables as suspicious
- ✅ Code signing or allow-listing required

**Library Dependencies:**
- ❌ Platform-specific libraries cause issues
- ✅ Use virtual environments and platform matching

### Solutions

1. **Use CI/CD**: Let GitHub Actions handle cross-platform builds
2. **Docker**: Containerized builds for consistency
3. **Native VMs**: Virtual machines for testing
4. **Code Signing**: Proper certificates for distribution

## 📊 Comparison of Methods

| Method | Setup Effort | Reliability | Cost | Maintenance |
|--------|-------------|-------------|------|-------------|
| GitHub Actions | Low | High | Free | Low |
| OSXCross | High | Medium | Free | High |
| Docker | Medium | High | Free | Medium |
| Native VMs | High | High | License cost | High |
| Wine | Medium | Low | Free | Medium |

## 🚀 Recommended Workflow

1. **Development**: Use native builds (`python build_executable.py`)
2. **Testing**: Use `python build_all.py` for local testing
3. **Release**: Use GitHub Actions for multi-platform builds
4. **Distribution**: Upload artifacts to GitHub Releases

This approach minimizes complexity while maximizing compatibility and reliability.