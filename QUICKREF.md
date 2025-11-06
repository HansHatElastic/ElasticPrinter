# ElasticPrinter Quick Reference

## Browser Printing (Primary Use Case)

### Safari
```
1. Navigate to web page
2. ⌘P (Command+P)
3. Select "ElasticPrinter"
4. Customize title (optional)
5. Click Print
```

### Chrome/Firefox
```
1. Navigate to web page
2. ⌘P (Command+P)
3. Destination: "ElasticPrinter"
4. Click Print
```

**Pro Tip:** Enable "Print Backgrounds" for better article formatting

See [BROWSER_PRINTING.md](BROWSER_PRINTING.md) for detailed browser guide.

## Common Commands

### Printer Management
```bash
# Check printer status
lpstat -p ElasticPrinter

# Check print queue
lpstat -o ElasticPrinter

# Process stuck jobs (COMMON ISSUE - use this if jobs don't index)
cd /path/to/elasticprinter
sudo ./scripts/process_queue.sh

# Enable printer
sudo cupsenable ElasticPrinter

# Disable printer
sudo cupsdisable ElasticPrinter

# Cancel all jobs
cancel -a ElasticPrinter

# Cancel specific job
cancel ElasticPrinter-XX

# Restart CUPS
sudo launchctl stop org.cups.cupsd
sudo launchctl start org.cups.cupsd
```

### Testing
```bash
# Test backend directly
echo "Test - $(date)" | sudo -u _lp /usr/libexec/cups/backend/elasticprinter 1001 testuser "Test" 1 ""

# Test with file
sudo -u _lp /usr/libexec/cups/backend/elasticprinter 1002 testuser "File Test" 1 "" < /path/to/file.txt

# Test Elasticsearch connection
curl -H "Authorization: ApiKey YOUR_API_KEY" \
  "https://your-cluster.elastic.cloud:443/_cluster/health"
```

### Logs
```bash
# View ElasticPrinter logs
tail -f /var/log/elasticprinter/app.log

# View CUPS error log
sudo tail -f /var/log/cups/error_log

# View last 50 lines
tail -50 /var/log/elasticprinter/app.log

# Search for errors
grep ERROR /var/log/elasticprinter/app.log

# Clear log file
sudo truncate -s 0 /var/log/elasticprinter/app.log
```

### Elasticsearch Queries
```bash
# Get specific document
curl -H "Authorization: ApiKey YOUR_API_KEY" \
  "https://your-cluster.elastic.cloud:443/print-jobs/_doc/print-job-1001"

# Search content
curl -H "Authorization: ApiKey YOUR_API_KEY" \
  "https://your-cluster.elastic.cloud:443/print-jobs/_search" \
  -H 'Content-Type: application/json' \
  -d'{"query":{"match":{"attachment.content":"search term"}}}'

# List recent documents
curl -H "Authorization: ApiKey YOUR_API_KEY" \
  "https://your-cluster.elastic.cloud:443/print-jobs/_search?size=10&sort=indexed_at:desc"

# Count documents
curl -H "Authorization: ApiKey YOUR_API_KEY" \
  "https://your-cluster.elastic.cloud:443/print-jobs/_count"

# Get index mapping
curl -H "Authorization: ApiKey YOUR_API_KEY" \
  "https://your-cluster.elastic.cloud:443/print-jobs/_mapping"
```

## Configuration Locations

| Item | Location |
|------|----------|
| Configuration | `/etc/elasticprinter/config.yaml` |
| Backend Script | `/usr/libexec/cups/backend/elasticprinter` |
| PPD File | `/Library/Printers/PPDs/Contents/Resources/ElasticPrinter.ppd` |
| Python Package | `/Library/Python/3.9/site-packages/` |
| Logs | `/var/log/elasticprinter/app.log` |
| Temp Files | `/tmp/elasticprinter/` |

## Configuration File

```yaml
elasticsearch:
  host: "https://cluster.elastic.cloud:443"
  api_key: "encoded_key_here"
  index: "print-jobs"
  pipeline: "attachment"
  verify_certs: true

logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "/var/log/elasticprinter/app.log"

processing:
  temp_dir: "/tmp/elasticprinter"
  keep_pdfs: false
  max_retries: 3
  timeout: 30
```

## Troubleshooting Quick Fixes

### Printer Disabled
```bash
sudo cupsenable ElasticPrinter
```

### No Logs Appearing
```bash
# Check log file exists and is writable
ls -l /var/log/elasticprinter/app.log
sudo chmod 666 /var/log/elasticprinter/app.log
```

### Permission Errors
```bash
# Fix temp directory
sudo chmod 777 /tmp/elasticprinter

# Fix log file
sudo chmod 666 /var/log/elasticprinter/app.log
```

### Elasticsearch Connection Failed
```bash
# Test connection
curl -v -H "Authorization: ApiKey YOUR_KEY" \
  "https://your-cluster.elastic.cloud:443/"

# Common issues:
# - Missing port (:443)
# - Wrong API key
# - Firewall blocking
```

### Backend Not Executing
```bash
# Check backend exists
ls -l /usr/libexec/cups/backend/elasticprinter

# Test execution
sudo -u _lp /usr/libexec/cups/backend/elasticprinter

# Reinstall if needed
sudo ./scripts/install_printer.sh
```

## Python API Usage

```python
from elastic.client import ElasticClient
from utils.config_loader import ConfigLoader

# Load config
config = ConfigLoader('/etc/elasticprinter/config.yaml')

# Create client
client = ElasticClient(
    host=config.elasticsearch['host'],
    api_key=config.elasticsearch['api_key'],
    index='print-jobs'
)

# Search documents
results = client.es.search(
    index='print-jobs',
    body={'query': {'match': {'attachment.content': 'invoice'}}}
)

# Get specific document
doc = client.es.get(index='print-jobs', id='print-job-1001')
```

## Environment Variables

```bash
# Disable Python bytecode (useful for CUPS)
export PYTHONDONTWRITEBYTECODE=1

# Python warnings
export PYTHONWARNINGS=ignore
```

## Useful Aliases

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
alias eplogs='tail -f /var/log/elasticprinter/app.log'
alias eptest='echo "Test - $(date)" | sudo -u _lp /usr/libexec/cups/backend/elasticprinter 999 testuser "Test" 1 ""'
alias epstatus='lpstat -p ElasticPrinter'
alias epenable='sudo cupsenable ElasticPrinter'
alias epclear='sudo truncate -s 0 /var/log/elasticprinter/app.log'
```

## Support

- Documentation: [README.md](README.md)
- Installation: [INSTALLATION.md](INSTALLATION.md)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
- Issues: GitHub Issues
