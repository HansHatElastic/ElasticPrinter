#!/bin/bash
#
# Installation script for ElasticPrinter
# This script must be run with sudo privileges
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print with color
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

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

print_info "Installing ElasticPrinter..."
print_info "Project directory: $PROJECT_DIR"

# Check dependencies
print_info "Checking dependencies..."

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not found"
    exit 1
fi
print_info "Python 3: $(python3 --version)"

# Check for CUPS
if ! command -v lpstat &> /dev/null; then
    print_error "CUPS is required but not found"
    exit 1
fi
print_info "CUPS: $(lpstat -r)"

# Install Python dependencies
print_info "Installing Python dependencies..."
pip3 install -r "$PROJECT_DIR/requirements.txt" || {
    print_error "Failed to install Python dependencies"
    exit 1
}

# Create config directory
print_info "Setting up configuration..."
CONFIG_DIR="$HOME/.elasticprinter"
mkdir -p "$CONFIG_DIR"

# Copy example config if config doesn't exist
if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
    cp "$PROJECT_DIR/config/config.yaml.example" "$CONFIG_DIR/config.yaml"
    print_warning "Created config file at $CONFIG_DIR/config.yaml"
    print_warning "Please edit this file with your Elasticsearch settings"
else
    print_info "Config file already exists at $CONFIG_DIR/config.yaml"
fi

# Create log directory
LOG_DIR="/var/log/elasticprinter"
mkdir -p "$LOG_DIR"
chmod 755 "$LOG_DIR"
print_info "Created log directory: $LOG_DIR"

# Create temp directory
TEMP_DIR="/tmp/elasticprinter"
mkdir -p "$TEMP_DIR"
chmod 755 "$TEMP_DIR"
print_info "Created temp directory: $TEMP_DIR"

# Install CUPS backend
print_info "Installing CUPS backend..."
BACKEND_DIR="/usr/libexec/cups/backend"
BACKEND_SRC="$PROJECT_DIR/printer/backend/elasticprinter"
BACKEND_DST="$BACKEND_DIR/elasticprinter"

# Make backend executable
chmod 755 "$BACKEND_SRC"

# Copy backend
cp "$BACKEND_SRC" "$BACKEND_DST"
chmod 755 "$BACKEND_DST"
chown root:wheel "$BACKEND_DST"
print_info "Installed CUPS backend to $BACKEND_DST"

# Install PPD file
print_info "Installing PPD file..."
PPD_SRC="$PROJECT_DIR/printer/elasticprinter.ppd"
PPD_DIR="/Library/Printers/PPDs/Contents/Resources"
mkdir -p "$PPD_DIR"
cp "$PPD_SRC" "$PPD_DIR/elasticprinter.ppd"
print_info "Installed PPD file"

# Add printer to CUPS
print_info "Adding printer to CUPS..."
PRINTER_NAME="ElasticPrinter"

# Check if printer already exists
if lpstat -p "$PRINTER_NAME" &> /dev/null; then
    print_warning "Printer $PRINTER_NAME already exists, removing..."
    lpadmin -x "$PRINTER_NAME"
fi

# Add printer
lpadmin -p "$PRINTER_NAME" \
    -E \
    -v "elasticprinter:/" \
    -P "$PPD_DIR/elasticprinter.ppd" \
    -D "Virtual PDF to Elasticsearch Printer" \
    -L "Cloud Storage"

print_info "Printer $PRINTER_NAME added successfully"

# Enable printer
cupsenable "$PRINTER_NAME"
cupsaccept "$PRINTER_NAME"

print_info "Printer enabled and accepting jobs"

# Optionally set as default
read -p "Set ElasticPrinter as default printer? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    lpadmin -d "$PRINTER_NAME"
    print_info "Set $PRINTER_NAME as default printer"
fi

# Test configuration
print_info "Testing configuration..."
if python3 -c "from src.utils.config_loader import ConfigLoader; ConfigLoader('$CONFIG_DIR/config.yaml')" 2>/dev/null; then
    print_info "Configuration loaded successfully"
else
    print_warning "Configuration test failed - please check your config.yaml"
fi

print_info ""
print_info "============================================"
print_info "ElasticPrinter installation complete!"
print_info "============================================"
print_info ""
print_info "Next steps:"
print_info "1. Edit configuration: $CONFIG_DIR/config.yaml"
print_info "2. Configure your Elasticsearch connection"
print_info "3. Run setup script: python3 $PROJECT_DIR/src/elastic/pipeline_setup.py $CONFIG_DIR/config.yaml"
print_info "4. Test printing to $PRINTER_NAME"
print_info ""
print_info "View printer status: lpstat -p $PRINTER_NAME"
print_info "View logs: tail -f $LOG_DIR/app.log"
print_info ""
