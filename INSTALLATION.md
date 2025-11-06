# ElasticPrinter Installation Guide

Complete step-by-step installation guide for ElasticPrinter on macOS.

## Prerequisites

Before installing ElasticPrinter, ensure you have:

1. **macOS 10.15 (Catalina) or later**
2. **Python 3.9 or higher** (check with `python3 --version`)
3. **Elasticsearch cluster** (8.0+ or Serverless)
4. **Elasticsearch API Key** with permissions:
   - `create_index` on `print-jobs` index
   - `write` on `print-jobs` index
   - `manage` on `.ingest-*` indices (for pipeline creation)

## Step-by-Step Installation

### 1. Download ElasticPrinter

```bash
cd ~/Projects
git clone https://github.com/yourusername/elasticprinter.git
cd elasticprinter
```

### 2. Get Your Elasticsearch Credentials

#### For Elasticsearch Serverless:

1. Go to your Elasticsearch Serverless console
2. Navigate to **Management** → **API Keys**
3. Click **Create API Key**
4. Give it a name like "elasticprinter"
5. Set permissions (or use the default)
6. **Copy the encoded API key** (it will look like: `RzVsX1dab0...`)
7. Save this key securely - you won't be able to see it again!

#### For Self-Managed Elasticsearch:

You can use either:
- API Key (recommended): Create via Kibana or API
- Username/Password: Use your Elasticsearch credentials

### 3. Configure ElasticPrinter

Create and edit the configuration file:

```bash
sudo mkdir -p /etc/elasticprinter
sudo cp config/config.yaml.example /etc/elasticprinter/config.yaml
sudo nano /etc/elasticprinter/config.yaml
```

Update these values:

```yaml
elasticsearch:
  # Your Elasticsearch URL with port
  host: "https://your-cluster-id.es.region.cloud.provider.elastic.cloud:443"
  
  # Paste your encoded API key here
  api_key: "your_encoded_api_key_here"
  
  # Index name (you can keep the default)
  index: "print-jobs"
  
  # Keep other defaults
  pipeline: "attachment"
  verify_certs: true
```

Save and exit (Ctrl+O, Enter, Ctrl+X in nano).

### 4. Test Elasticsearch Connection

Before installing, verify your Elasticsearch credentials work:

```bash
# Replace YOUR_API_KEY and YOUR_URL with your actual values
curl -H "Authorization: ApiKey YOUR_ENCODED_API_KEY" \
  "https://your-cluster.elastic.cloud:443/_cluster/health"
```

You should see a JSON response with cluster health information.

### 5. Install ElasticPrinter

Run the installation script:

```bash
sudo ./scripts/install_printer.sh
```

This script will:
- ✓ Install Python package and dependencies system-wide
- ✓ Create necessary directories
- ✓ Install CUPS backend
- ✓ Install printer PPD file
- ✓ Register ElasticPrinter with CUPS
- ✓ Set proper permissions

**Note**: You'll be prompted for your password (sudo access required).

### 6. Enable the Printer

After installation, enable the printer:

```bash
sudo cupsenable ElasticPrinter
```

### 7. Verify Installation

Check that the printer is registered:

```bash
lpstat -p ElasticPrinter
```

You should see:
```
printer ElasticPrinter is idle.  enabled since ...
```

### 8. Test the Backend Manually

Test that the backend can communicate with Elasticsearch:

```bash
echo "Installation test - $(date)" | sudo -u _lp /usr/libexec/cups/backend/elasticprinter 1001 testuser "Installation Test" 1 ""
```

Expected output should include:
```
Successfully indexed document: print-job-1001
Print job processed successfully
```

### 9. Verify Document in Elasticsearch

Check that the test document was indexed:

```bash
curl -H "Authorization: ApiKey YOUR_ENCODED_API_KEY" \
  "https://your-cluster.elastic.cloud:443/print-jobs/_doc/print-job-1001" | python3 -m json.tool
```

You should see your test document with content extracted!

### 10. Print a Test Page

Try printing from any application:

1. Open TextEdit or any app
2. Type "Hello ElasticPrinter!"
3. Press Cmd+P to print
4. Select **ElasticPrinter** from the printer dropdown
5. Click **Print**

Check the logs:

```bash
tail -20 /var/log/elasticprinter/app.log
```

## Post-Installation Configuration

### Adjust Log Level

For debugging, enable DEBUG logging:

```bash
sudo nano /etc/elasticprinter/config.yaml
```

Change:
```yaml
logging:
  level: "DEBUG"  # Changed from INFO
```

### Keep PDFs for Inspection

To keep processed files temporarily:

```yaml
processing:
  keep_pdfs: true  # Changed from false
  temp_dir: "/tmp/elasticprinter"
```

Files will be saved in `/tmp/elasticprinter/` for inspection.

### Create Log Rotation

To prevent log files from growing too large:

```bash
sudo nano /etc/newsyslog.d/elasticprinter.conf
```

Add:
```
/var/log/elasticprinter/app.log 644 7 10000 * GZ
```

## Troubleshooting Installation

### Python Dependencies Fail to Install

```bash
# Check Python version (must be 3.9+)
python3 --version

# Manually install dependencies
sudo pip3 install elasticsearch PyPDF2 pyyaml requests
```

### Permission Errors

```bash
# Fix log file permissions
sudo touch /var/log/elasticprinter/app.log
sudo chmod 666 /var/log/elasticprinter/app.log

# Fix temp directory permissions
sudo mkdir -p /tmp/elasticprinter
sudo chmod 777 /tmp/elasticprinter
```

### Printer Won't Appear

```bash
# Restart CUPS
sudo launchctl stop org.cups.cupsd
sudo launchctl start org.cups.cupsd

# Re-enable printer
sudo cupsenable ElasticPrinter

# Check printer exists
lpstat -p
```

### Elasticsearch Connection Fails

```bash
# Test connection directly
curl -v -H "Authorization: ApiKey YOUR_API_KEY" \
  "https://your-cluster.elastic.cloud:443/"

# Common issues:
# - Wrong URL (missing port :443)
# - Wrong API key (copy the ENCODED key, not the ID)
# - Firewall blocking outbound HTTPS
# - API key doesn't have required permissions
```

### Backend Not Executing

```bash
# Check backend exists and is executable
ls -l /usr/libexec/cups/backend/elasticprinter

# Should show: -rwxr-xr-x ... elasticprinter

# Test backend directly
sudo -u _lp /usr/libexec/cups/backend/elasticprinter

# Should output: file elasticprinter:/ "ElasticPrinter" ...
```

## Uninstallation

To completely remove ElasticPrinter:

```bash
sudo ./scripts/uninstall_printer.sh
```

This removes:
- CUPS printer registration
- Backend script
- PPD file
- Python package
- Configuration file (optional - you'll be prompted)

## Next Steps

- Read [README.md](README.md) for usage instructions
- Check [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for technical details
- See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues

## Getting Help

- Check logs: `tail -f /var/log/elasticprinter/app.log`
- Check CUPS logs: `sudo tail -f /var/log/cups/error_log`
- Open an issue on GitHub
- Review the troubleshooting guide
