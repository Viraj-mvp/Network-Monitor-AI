#!/bin/bash
#
# Build script for Network AI Monitor on macOS
# Creates a standalone .app bundle using PyInstaller
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
    echo "║         Network AI Monitor - macOS Build Script          ║"
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

# Clean if requested
if [ "$CLEAN" = true ]; then
    print_step "Cleaning build directories"
    rm -rf build dist
    print_success "Cleaned previous builds"
fi

# Install dependencies if requested
if [ "$INSTALL" = true ]; then
    print_step "Installing dependencies"
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-build.txt
    print_success "Dependencies installed"
fi

# Build
print_step "Building app bundle"
if pyinstaller build/pyinstaller/NetworkMonitor.spec; then
    print_success "Build completed"
else
    print_error "Build failed"
    exit 1
fi

# Prepare distribution
print_step "Preparing distribution"
if [ -d "dist/$APP_NAME" ]; then
    # Create proper .app structure
    mv "dist/$APP_NAME" "dist/$APP_NAME.app"
    
    # Create archive
    cd dist
    tar -czf "${APP_NAME}-macOS.tar.gz" "$APP_NAME.app"
    cd ..
    
    print_success "Created ${APP_NAME}-macOS.tar.gz"
fi

# Summary
echo -e "\n${BLUE}══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  BUILD COMPLETE${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
echo -e "\nOutput:"
if [ -f "dist/${APP_NAME}-macOS.tar.gz" ]; then
    SIZE=$(du -h "dist/${APP_NAME}-macOS.tar.gz" | cut -f1)
    echo "  • ${APP_NAME}-macOS.tar.gz ($SIZE)"
fi
echo -e "\nTo test:"
echo "  1. Extract: tar -xzf ${APP_NAME}-macOS.tar.gz"
echo "  2. Open: open ${APP_NAME}.app"
echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
