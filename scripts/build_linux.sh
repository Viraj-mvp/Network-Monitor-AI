#!/bin/bash
#
# Build script for Network AI Monitor on Linux
# Creates a standalone executable using PyInstaller
#

set -e

APP_NAME="NetworkAIMonitor"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║         Network AI Monitor - Linux Build Script          ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Parse arguments
CLEAN=false
INSTALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --clean)
            CLEAN=true
            shift
            ;;
        --install)
            INSTALL=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

print_banner

# Check for required system packages
print_step "Checking system dependencies"
MISSING_PKGS=""

if ! dpkg -l | grep -q "libgl1-mesa-glx\|libgl1"; then
    MISSING_PKGS="$MISSING_PKGS libgl1"
fi

if ! dpkg -l | grep -q "libxkbcommon-x11-0"; then
    MISSING_PKGS="$MISSING_PKGS libxkbcommon-x11-0"
fi

if ! dpkg -l | grep -q "libxcb-xinerama0"; then
    MISSING_PKGS="$MISSING_PKGS libxcb-xinerama0"
fi

if [ -n "$MISSING_PKGS" ]; then
    echo "Missing system packages:$MISSING_PKGS"
    echo "Install with: sudo apt-get install$MISSING_PKGS"
    exit 1
fi

print_success "System dependencies OK"

# Clean if requested
if [ "$CLEAN" = true ]; then
    print_step "Cleaning build directories"
    rm -rf build dist
    print_success "Cleaned previous builds"
fi

# Install dependencies if requested
if [ "$INSTALL" = true ]; then
    print_step "Installing Python dependencies"
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-build.txt
    print_success "Dependencies installed"
fi

# Build
print_step "Building executable"
if pyinstaller build/pyinstaller/NetworkMonitor.spec; then
    print_success "Build completed"
else
    print_error "Build failed"
    exit 1
fi

# Prepare distribution
print_step "Preparing distribution"
if [ -d "dist/$APP_NAME" ]; then
    mv "dist/$APP_NAME" "dist/$APP_NAME-Linux"
    
    # Make executable
    chmod +x "dist/$APP_NAME-Linux/$APP_NAME"
    
    # Create archive
    cd dist
    tar -czf "${APP_NAME}-Linux.tar.gz" "$APP_NAME-Linux"
    cd ..
    
    print_success "Created ${APP_NAME}-Linux.tar.gz"
fi

# Summary
echo -e "\n${BLUE}══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  BUILD COMPLETE${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
echo -e "\nOutput:"
if [ -f "dist/${APP_NAME}-Linux.tar.gz" ]; then
    SIZE=$(du -h "dist/${APP_NAME}-Linux.tar.gz" | cut -f1)
    echo "  • ${APP_NAME}-Linux.tar.gz ($SIZE)"
fi
echo -e "\nTo test:"
echo "  1. Extract: tar -xzf ${APP_NAME}-Linux.tar.gz"
echo "  2. Run: ./${APP_NAME}-Linux/${APP_NAME}"
echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
