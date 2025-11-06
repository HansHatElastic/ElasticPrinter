#!/bin/bash
#
# ElasticPrinter Installation Script for macOS
# This script installs the ElasticPrinter CUPS backend and sets up the virtual printer
#

set -e

echo "======================================"
echo "ElasticPrinter Installation for macOS"
echo "======================================"
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
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installation steps:"
echo "1. Installing CUPS backend..."

# Copy the backend script
if [ -f "$SCRIPT_DIR/$BACKEND_NAME" ]; then
    cp "$SCRIPT_DIR/$BACKEND_NAME" "$BACKEND_DIR/$BACKEND_NAME"
    chmod 755 "$BACKEND_DIR/$BACKEND_NAME"
    chown root:wheel "$BACKEND_DIR/$BACKEND_NAME"
    echo "   ✓ Backend installed to $BACKEND_DIR/$BACKEND_NAME"
else
    echo "   ✗ Error: $BACKEND_NAME script not found in $SCRIPT_DIR"
    exit 1
fi

echo ""
echo "2. Installing Python dependencies..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "   ✗ Error: Python 3 is not installed"
    echo "   Please install Python 3 from https://www.python.org/"
    exit 1
fi

# Install requests library
if python3 -m pip show requests &> /dev/null; then
    echo "   ✓ requests library already installed"
else
    echo "   Installing requests library..."
    if python3 -m pip install --user --quiet requests; then
        echo "   ✓ requests library installed successfully"
    else
        echo "   ✗ Warning: Could not install requests library automatically"
        echo "   Please run: pip3 install --user requests"
    fi
fi

echo "   ✓ Python dependencies checked"

echo ""
echo "3. Creating configuration directory..."

# Create config directory for the user who invoked sudo
REAL_USER="${SUDO_USER:-$USER}"
REAL_HOME=$(eval echo ~$REAL_USER)
CONFIG_DIR="$REAL_HOME/.elasticprinter"

mkdir -p "$CONFIG_DIR/logs"
chown -R $REAL_USER:staff "$CONFIG_DIR"
echo "   ✓ Configuration directory created at $CONFIG_DIR"

# Create default config if it doesn't exist
CONFIG_FILE="$CONFIG_DIR/config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" << 'EOF'
{
  "elastic_url": "http://localhost:9200",
  "elastic_index": "printed-documents",
  "elastic_username": "",
  "elastic_password": ""
}
EOF
    chown $REAL_USER:staff "$CONFIG_FILE"
    echo "   ✓ Default configuration created at $CONFIG_FILE"
    echo "   Please edit this file to configure your Elasticsearch connection"
fi

echo ""
echo "4. Adding printer to CUPS..."

# Check if printer already exists
if lpstat -p "$PRINTER_NAME" &> /dev/null; then
    echo "   ! Printer '$PRINTER_NAME' already exists. Removing old version..."
    lpadmin -x "$PRINTER_NAME"
fi

# Add the printer
lpadmin -p "$PRINTER_NAME" \
    -v "elastic-printer://localhost/" \
    -E \
    -D "ElasticPrinter - Print to Elasticsearch" \
    -L "Virtual" \
    -m drv:///sample.drv/generic.ppd

# Enable the printer
cupsenable "$PRINTER_NAME"
cupsaccept "$PRINTER_NAME"

echo "   ✓ Printer '$PRINTER_NAME' added to CUPS"

echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "The ElasticPrinter virtual printer has been installed."
echo ""
echo "Configuration file: $CONFIG_FILE"
echo "Log file: $CONFIG_DIR/logs/elastic-printer.log"
echo ""
echo "To configure your Elasticsearch connection:"
echo "  1. Edit $CONFIG_FILE"
echo "  2. Set your Elasticsearch URL, index, and credentials"
echo ""
echo "To print a document:"
echo "  - Select 'ElasticPrinter' from any application's print dialog"
echo "  - Or use command line: lp -d ElasticPrinter <filename>"
echo ""
echo "To uninstall:"
echo "  - Run: sudo ./uninstall.sh"
echo ""
