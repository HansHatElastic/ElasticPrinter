# ElasticPrinter

A virtual printer for macOS that automatically indexes print jobs in Elasticsearch for searchability and cloud storage. **Perfect for archiving and searching web pages from your browser!**

## Primary Use Case: Web Page Archiving

Print any web page from Safari, Chrome, or Firefox directly to Elasticsearch:
- 📰 **Archive articles** and research materials with full-text search
- 📚 **Save documentation** for offline access and quick lookup
- 🔍 **Search across all saved pages** instantly
- ⚖️ **Compliance archiving** with automatic timestamping
- 🧠 **Build a personal knowledge base** from web content

See [Browser Printing Guide](BROWSER_PRINTING.md) for detailed instructions.

## Features

- **Browser Integration**: Print web pages directly from Safari, Chrome, Firefox, or any macOS app
- **Virtual Printer Integration**: Seamlessly integrates with macOS printing system using CUPS
- **Automatic Content Extraction**: Captures print job content and indexes in Elasticsearch
- **Elasticsearch Indexing**: Automatically posts documents to Elasticsearch with full-text search capability
- **Metadata Extraction**: Captures job metadata (user, timestamp, title, hostname)
- **Content Search**: Uses Elasticsearch ingest attachment pipeline to extract searchable text
- **Flexible Configuration**: YAML-based configuration for easy customization
- **Serverless Compatible**: Works with Elasticsearch Serverless clusters

## Requirements

- macOS 10.15 (Catalina) or later
- Python 3.9 or higher
- CUPS (pre-installed on macOS)
- Elasticsearch 8.0+ cluster (including Serverless)
- Network access to Elasticsearch
- API Key for authentication (recommended) or basic auth credentials

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/elasticprinter.git
cd elasticprinter
```

### 2. Configure Elasticsearch

Copy the example configuration and edit with your Elasticsearch settings:

```bash
sudo mkdir -p /etc/elasticprinter
sudo cp config/config.yaml.example /etc/elasticprinter/config.yaml
sudo nano /etc/elasticprinter/config.yaml
```

Update the following settings:
- `elasticsearch.host`: Your Elasticsearch URL (including port, e.g., `https://your-cluster.elastic.cloud:443`)
- `elasticsearch.api_key`: Your encoded API key (recommended for Serverless)
- Or use `elasticsearch.api_key_id` and `elasticsearch.api_key`: For tuple-based authentication
- Or use `username` and `password` for basic auth

**Note**: For Elasticsearch Serverless, use the encoded API key format.

### 3. Install the Printer

Run the installation script (requires sudo):

```bash
sudo ./scripts/install_printer.sh
```

This will:
- Install Python dependencies system-wide
- Install the CUPS backend at `/usr/libexec/cups/backend/elasticprinter`
- Install the PPD file at `/Library/Printers/PPDs/Contents/Resources/`
- Register the ElasticPrinter with CUPS
- Create necessary directories (`/tmp/elasticprinter`, `/var/log/elasticprinter`)
- Set appropriate permissions

### 4. Set Up Elasticsearch

The printer will automatically create the index and pipeline on first use, or you can pre-create them:

```bash
# The index and pipeline are created automatically when the first document is indexed
# Or manually create using the Elasticsearch API
```

### 5. Enable the Printer

After installation, enable the printer:

```bash
sudo cupsenable ElasticPrinter
```

### 6. Print from Your Browser

**That's it! Now print any web page:**

1. Open Safari, Chrome, or Firefox
2. Navigate to any web page
3. Press `⌘P` (Command+P) or select **File** → **Print**
4. Choose **ElasticPrinter** from the printer dropdown
5. Click **Print**

Your web page is now indexed and searchable in Elasticsearch! 🎉

**⚠️ Known Issue - Chrome/Firefox Jobs May Stuck:**  
If your print job doesn't appear in Elasticsearch within 30 seconds, run:
```bash
sudo python3 scripts/process_stuck_jobs.py
```
This processes any stuck jobs in the CUPS queue. See [Chrome Workaround Guide](CHROME_WORKAROUND.md) for details and alternative solutions.

**💡 Most Reliable Method:**  
For important pages, use **Print → Save as PDF** → then print the PDF to ElasticPrinter. This works 100% of the time!

See the [Browser Printing Guide](BROWSER_PRINTING.md) for:
- Browser-specific instructions
- Optimal print settings
- Workflow examples
- Searching your archived pages

### 7. Test the Backend (Optional)

You can test the backend directly:

```bash
echo "Test document - $(date)" | sudo -u _lp /usr/libexec/cups/backend/elasticprinter 1001 testuser "Test Document" 1 ""
```

Or print from any application and select "ElasticPrinter" as your printer!

## Usage

### Printing Web Pages (Primary Use Case)

**From Safari:**
1. Navigate to any web page
2. Press `⌘P` (Command+P)
3. Select **ElasticPrinter**
4. Optionally customize the title for easier searching
5. Click **Print**

**From Chrome/Firefox:**
1. Navigate to any web page
2. Press `⌘P` (Command+P)
3. Select **ElasticPrinter** as destination
4. Click **Print**

**Best Practices:**
- Use descriptive titles (e.g., "AWS Lambda Docs - Python")
- Enable "Print Backgrounds" for better formatting
- Use 100% scale for optimal text extraction

See [Browser Printing Guide](BROWSER_PRINTING.md) for detailed instructions and examples.

### Printing Documents

1. Open any document in macOS (PDF, Word, Pages, etc.)
2. Choose File → Print (Cmd+P)
3. Select "ElasticPrinter" from the printer list
4. Click Print

The document will be:
1. Converted to PDF
2. Indexed in Elasticsearch
3. Searchable via the Elasticsearch cluster

### Searching Your Printed Content

Use Elasticsearch queries to search your printed web pages and documents:

```bash
# Search for web pages containing "kubernetes" (replace with your Elasticsearch URL and API key)
curl -X GET "https://your-cluster.elastic.cloud:443/print-jobs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -H 'Authorization: ApiKey YOUR_ENCODED_API_KEY' \
  -d'
{
  "query": {
    "match": {
      "attachment.content": "kubernetes"
    }
  },
  "highlight": {
    "fields": {
      "attachment.content": {}
    }
  }
}
'

# Search by title (e.g., find all AWS documentation)
curl -X GET "https://your-cluster.elastic.cloud:443/print-jobs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -H 'Authorization: ApiKey YOUR_ENCODED_API_KEY' \
  -d'
{
  "query": {
    "match": {
      "print_job.title": "AWS"
    }
  }
}
'

# Get a specific document by ID
curl -H "Authorization: ApiKey YOUR_ENCODED_API_KEY" \
  "https://your-cluster.elastic.cloud:443/print-jobs/_doc/print-job-1001"

# List recent documents
curl -H "Authorization: ApiKey YOUR_ENCODED_API_KEY" \
  "https://your-cluster.elastic.cloud:443/print-jobs/_search?size=10&sort=indexed_at:desc"
```

### Viewing Logs

```bash
tail -f /var/log/elasticprinter/app.log
```

### Checking Printer Status

```bash
lpstat -p ElasticPrinter
```

## Configuration

The configuration file is located at `/etc/elasticprinter/config.yaml` and supports the following options:

```yaml
elasticsearch:
  host: "https://your-cluster.elastic.cloud:443"  # Include port
  # For Serverless or encoded API key:
  api_key: "your_encoded_api_key"
  # OR for tuple-based API key:
  # api_key_id: "your_api_key_id"
  # api_key: "your_api_key_secret"
  # OR for basic auth:
  # username: "elastic"
  # password: "your_password"
  index: "print-jobs"
  pipeline: "attachment"
  verify_certs: true

printer:
  name: "ElasticPrinter"
  description: "Virtual Printer to Elasticsearch"
  location: "Cloud Storage"

processing:
  temp_dir: "/tmp/elasticprinter"
  keep_pdfs: false  # Set to true for debugging
  max_retries: 3
  timeout: 30

logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "/var/log/elasticprinter/app.log"
```

## Architecture

```
Print Job → CUPS → ElasticPrinter Backend → Content Processing → Elasticsearch
                           ↓                         ↓
                    Read from stdin          Metadata Extraction
                                                     ↓
                                            Ingest Pipeline (attachment)
```

1. **CUPS Backend** (`/usr/libexec/cups/backend/elasticprinter`): Receives print jobs from macOS printing system
2. **Content Processing**: Saves print job content (PostScript/text) for indexing
3. **Metadata Extractor**: Extracts job metadata (user, title, timestamp, hostname) and PDF metadata
4. **Elasticsearch Client**: Indexes content with metadata using ingest attachment pipeline
5. **Attachment Pipeline**: Elasticsearch extracts searchable text from the document

### Component Details

- **Python Package**: Installed at `/Library/Python/3.9/site-packages/`
  - `converter/`: Content handling and processing
  - `elastic/`: Elasticsearch client and indexing
  - `utils/`: Configuration, logging utilities
  - `elasticprinter_backend/`: Main orchestrator
  
- **CUPS Integration**:
  - Backend: `/usr/libexec/cups/backend/elasticprinter`
  - PPD: `/Library/Printers/PPDs/Contents/Resources/ElasticPrinter.ppd`
  
- **Configuration**: `/etc/elasticprinter/config.yaml`
- **Logs**: `/var/log/elasticprinter/app.log`
- **Temporary Files**: `/tmp/elasticprinter/`

## Troubleshooting

### Printer doesn't appear in print dialog

```bash
# Check if printer is registered
lpstat -p ElasticPrinter

# Re-install if needed
sudo ./scripts/uninstall_printer.sh
sudo ./scripts/install_printer.sh
```

### Print jobs fail

Check the logs:
```bash
tail -f /var/log/elasticprinter/app.log

# Or check CUPS logs
sudo tail -f /var/log/cups/error_log
```

Common issues:
- **Elasticsearch connection failed**: Check network, credentials, and firewall rules
- **Permission denied**: Ensure `/tmp/elasticprinter` and `/var/log/elasticprinter/app.log` are writable
- **Printer disabled**: Run `sudo cupsenable ElasticPrinter`
- **No logs appearing**: Backend might not be executing - check CUPS error log

### Test Backend Directly

The best way to test is to run the backend directly:

```bash
# Test as the CUPS user (_lp)
echo "Test content - $(date)" | sudo -u _lp /usr/libexec/cups/backend/elasticprinter 999 testuser "Test" 1 ""

# Check if document was indexed
curl -H "Authorization: ApiKey YOUR_API_KEY" \
  "https://your-cluster.elastic.cloud:443/print-jobs/_doc/print-job-999"
```

### Test Elasticsearch Connection

```bash
# Quick connection test
curl -H "Authorization: ApiKey YOUR_ENCODED_API_KEY" \
  "https://your-cluster.elastic.cloud:443/_cluster/health"

# Test with Python
sudo python3 -c "
from utils.config_loader import ConfigLoader
from elastic.client import ElasticClient

config = ConfigLoader('/etc/elasticprinter/config.yaml')
es_config = config.elasticsearch
client = ElasticClient(
    host=es_config.get('host'),
    api_key=es_config.get('api_key'),
    index=es_config.get('index')
)
print('Connected successfully!')
"
```

## Uninstallation

To remove ElasticPrinter:

```bash
sudo ./scripts/uninstall_printer.sh
```

## Development

### Running Tests

```bash
python3 -m pytest tests/
```

### Project Structure

```
elasticprinter/
├── src/
│   ├── converter/        # PDF generation and conversion
│   ├── elastic/          # Elasticsearch integration
│   ├── utils/            # Configuration and logging
│   └── main.py           # Main orchestrator
├── printer/
│   ├── backend/          # CUPS backend script
│   └── elasticprinter.ppd # Printer definition
├── scripts/              # Installation scripts
├── config/               # Configuration templates
└── tests/                # Unit tests
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.

## Roadmap

- [ ] OCR support for scanned documents
- [ ] Web UI for searching and retrieving documents
- [ ] Multi-tenancy support
- [ ] Cloud storage integration (S3, Azure Blob)
- [ ] macOS Settings extension
- [ ] Notification on successful indexing
