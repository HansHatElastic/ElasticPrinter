#!/bin/bash
#
# ElasticPrinter Uninstallation Script for macOS
#

set -e

echo "========================================="
echo "ElasticPrinter Uninstallation for macOS"
echo "========================================="
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This script is for macOS only"
    exit 1
fi

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root (use sudo)"
    exit 1
fi

# Variables
BACKEND_DIR="/usr/libexec/cups/backend"
BACKEND_NAME="elastic-printer"
PRINTER_NAME="ElasticPrinter"

echo "Uninstallation steps:"
echo ""

echo "1. Removing printer from CUPS..."
if lpstat -p "$PRINTER_NAME" &> /dev/null; then
    lpadmin -x "$PRINTER_NAME"
    echo "   ✓ Printer '$PRINTER_NAME' removed"
else
    echo "   - Printer '$PRINTER_NAME' not found"
fi

echo ""
echo "2. Removing CUPS backend..."
if [ -f "$BACKEND_DIR/$BACKEND_NAME" ]; then
    rm -f "$BACKEND_DIR/$BACKEND_NAME"
    echo "   ✓ Backend removed from $BACKEND_DIR"
else
    echo "   - Backend not found"
fi

echo ""
echo "======================================"
echo "Uninstallation Complete!"
echo "======================================"
echo ""
echo "The ElasticPrinter has been removed from your system."
echo ""
echo "Note: Configuration files in ~/.elasticprinter were not removed."
echo "To remove them manually, run:"
echo "  rm -rf ~/.elasticprinter"
echo ""
