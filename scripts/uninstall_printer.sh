#!/bin/bash
#
# Uninstallation script for ElasticPrinter
# This script must be run with sudo privileges
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root (use sudo)"
    exit 1
fi

PRINTER_NAME="ElasticPrinter"

print_info "Uninstalling ElasticPrinter..."

# Remove printer from CUPS
if lpstat -p "$PRINTER_NAME" &> /dev/null; then
    print_info "Removing printer $PRINTER_NAME..."
    lpadmin -x "$PRINTER_NAME"
    print_info "Printer removed"
else
    print_warning "Printer $PRINTER_NAME not found"
fi

# Remove CUPS backend
BACKEND_FILE="/usr/libexec/cups/backend/elasticprinter"
if [ -f "$BACKEND_FILE" ]; then
    print_info "Removing CUPS backend..."
    rm "$BACKEND_FILE"
    print_info "CUPS backend removed"
fi

# Remove PPD file
PPD_FILE="/Library/Printers/PPDs/Contents/Resources/elasticprinter.ppd"
if [ -f "$PPD_FILE" ]; then
    print_info "Removing PPD file..."
    rm "$PPD_FILE"
    print_info "PPD file removed"
fi

# Ask about config and logs
read -p "Remove configuration and logs? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Remove config
    CONFIG_DIR="$HOME/.elasticprinter"
    if [ -d "$CONFIG_DIR" ]; then
        print_info "Removing configuration..."
        rm -rf "$CONFIG_DIR"
        print_info "Configuration removed"
    fi
    
    # Remove logs
    LOG_DIR="/var/log/elasticprinter"
    if [ -d "$LOG_DIR" ]; then
        print_info "Removing logs..."
        rm -rf "$LOG_DIR"
        print_info "Logs removed"
    fi
else
    print_info "Configuration and logs preserved"
fi

# Remove temp directory
TEMP_DIR="/tmp/elasticprinter"
if [ -d "$TEMP_DIR" ]; then
    print_info "Removing temp directory..."
    rm -rf "$TEMP_DIR"
    print_info "Temp directory removed"
fi

print_info ""
print_info "============================================"
print_info "ElasticPrinter uninstalled successfully!"
print_info "============================================"
print_info ""
