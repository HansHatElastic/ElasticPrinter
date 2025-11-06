#!/bin/bash
#
# Quick start script for ElasticPrinter
# Helps users get started quickly with common configuration
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
 _____ _           _   _      ____       _       _            
|  ___| | __ _ ___| |_(_) ___|  _ \ _ __(_)_ __ | |_ ___ _ __ 
| |_  | |/ _` / __| __| |/ __| |_) | '__| | '_ \| __/ _ \ '__|
|  _| | | (_| \__ \ |_| | (__|  __/| |  | | | | | ||  __/ |   
|_|   |_|\__,_|___/\__|_|\___|_|   |_|  |_|_| |_|\__\___|_|   
                                                                
EOF
echo -e "${NC}"

echo -e "${GREEN}ElasticPrinter Setup Wizard${NC}\n"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Error: Python 3 is required but not found${NC}"
    exit 1
fi

# Create config directory
CONFIG_DIR="$HOME/.elasticprinter"
mkdir -p "$CONFIG_DIR"

# Interactive configuration
if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
    echo -e "${BLUE}Let's configure your Elasticsearch connection${NC}\n"
    
    read -p "Elasticsearch host (e.g., https://localhost:9200): " ES_HOST
    read -p "Index name (default: print-jobs): " ES_INDEX
    ES_INDEX=${ES_INDEX:-print-jobs}
    
    echo ""
    echo "Authentication method:"
    echo "1) API Key (recommended)"
    echo "2) Basic Auth (username/password)"
    read -p "Choose (1 or 2): " AUTH_METHOD
    
    if [ "$AUTH_METHOD" == "1" ]; then
        read -p "API Key ID: " API_KEY_ID
        read -sp "API Key Secret: " API_KEY
        echo ""
        
        cat > "$CONFIG_DIR/config.yaml" << EOF
elasticsearch:
  host: "$ES_HOST"
  api_key_id: "$API_KEY_ID"
  api_key: "$API_KEY"
  index: "$ES_INDEX"
  pipeline: "attachment"
  verify_certs: true

printer:
  name: "ElasticPrinter"
  description: "Virtual Printer to Elasticsearch"
  location: "Cloud Storage"

processing:
  temp_dir: "/tmp/elasticprinter"
  keep_pdfs: false
  max_retries: 3
  timeout: 30

logging:
  level: "INFO"
  file: "/var/log/elasticprinter/app.log"
EOF
    else
        read -p "Username: " ES_USERNAME
        read -sp "Password: " ES_PASSWORD
        echo ""
        
        cat > "$CONFIG_DIR/config.yaml" << EOF
elasticsearch:
  host: "$ES_HOST"
  username: "$ES_USERNAME"
  password: "$ES_PASSWORD"
  index: "$ES_INDEX"
  pipeline: "attachment"
  verify_certs: true

printer:
  name: "ElasticPrinter"
  description: "Virtual Printer to Elasticsearch"
  location: "Cloud Storage"

processing:
  temp_dir: "/tmp/elasticprinter"
  keep_pdfs: false
  max_retries: 3
  timeout: 30

logging:
  level: "INFO"
  file: "/var/log/elasticprinter/app.log"
EOF
    fi
    
    echo -e "\n${GREEN}✓ Configuration saved to $CONFIG_DIR/config.yaml${NC}\n"
else
    echo -e "${YELLOW}Configuration already exists at $CONFIG_DIR/config.yaml${NC}\n"
fi

# Install dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
pip3 install -r requirements.txt --quiet

echo -e "${GREEN}✓ Dependencies installed${NC}\n"

# Test Elasticsearch connection
echo -e "${BLUE}Testing Elasticsearch connection...${NC}"
if python3 -c "
import sys
sys.path.insert(0, 'src')
from utils.config_loader import ConfigLoader
from elastic.client import ElasticClient

try:
    config = ConfigLoader('$CONFIG_DIR/config.yaml')
    es_config = config.elasticsearch
    client = ElasticClient(
        host=es_config.get('host'),
        index=es_config.get('index', 'print-jobs'),
        api_key_id=es_config.get('api_key_id'),
        api_key=es_config.get('api_key'),
        username=es_config.get('username'),
        password=es_config.get('password'),
        verify_certs=es_config.get('verify_certs', True)
    )
    client.close()
    print('✓ Connected successfully')
except Exception as e:
    print(f'✗ Connection failed: {e}')
    sys.exit(1)
" 2>&1; then
    echo -e "${GREEN}✓ Elasticsearch connection successful${NC}\n"
else
    echo -e "${YELLOW}⚠ Could not connect to Elasticsearch${NC}"
    echo -e "${YELLOW}Please check your configuration and network${NC}\n"
fi

# Set up Elasticsearch
echo -e "${BLUE}Setting up Elasticsearch index and pipeline...${NC}"
if python3 src/elastic/pipeline_setup.py "$CONFIG_DIR/config.yaml"; then
    echo -e "${GREEN}✓ Elasticsearch setup complete${NC}\n"
else
    echo -e "${YELLOW}⚠ Elasticsearch setup had issues${NC}\n"
fi

# Installation instructions
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Setup Complete!${NC}\n"
echo "Next steps:"
echo ""
echo "1. Install the printer (requires sudo):"
echo -e "   ${YELLOW}sudo ./scripts/install_printer.sh${NC}"
echo ""
echo "2. Test printing:"
echo -e "   ${YELLOW}echo 'Test print' | lp -d ElasticPrinter -${NC}"
echo ""
echo "3. Search your documents in Elasticsearch:"
echo -e "   Index: ${YELLOW}$ES_INDEX${NC}"
echo ""
echo "For detailed information, see:"
echo "  - README.md for general usage"
echo "  - INSTALL.md for installation details"
echo "  - IMPLEMENTATION_SUMMARY.md for technical overview"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
