# ElasticPrinter

A virtual printer for macOS that sends printed documents to an Elasticsearch cluster. Print from any application and have your documents automatically indexed and stored in Elasticsearch.

## Features

- 🖨️ **Virtual Printer**: Acts as a standard macOS printer - print from any application
- 🔍 **Elasticsearch Integration**: Automatically sends print jobs to your Elasticsearch cluster
- ⚙️ **Configurable**: Easy configuration via JSON file
- 📝 **Metadata Capture**: Stores job metadata (title, user, timestamp, etc.) along with document data
- 🔐 **Authentication Support**: Supports Elasticsearch authentication with username/password
- 📊 **Base64 Encoding**: Documents are base64-encoded for safe JSON storage

## Requirements

- macOS (tested on macOS 10.14+)
- Python 3.6 or higher
- CUPS (included with macOS)
- Elasticsearch cluster (local or remote)
- Python `requests` library (automatically installed during setup)

## Installation

1. **Clone or download this repository**:
   ```bash
   git clone https://github.com/HansHatElastic/ElasticPrinter.git
   cd ElasticPrinter
   ```

2. **Run the installation script**:
   ```bash
   sudo ./install.sh
   ```

   The installer will:
   - Install the CUPS backend to `/usr/libexec/cups/backend/`
   - Install required Python dependencies
   - Create configuration directory at `~/.elasticprinter/`
   - Add the ElasticPrinter to your system printers

3. **Configure your Elasticsearch connection**:
   Edit `~/.elasticprinter/config.json`:
   ```json
   {
     "elastic_url": "http://localhost:9200",
     "elastic_index": "printed-documents",
     "elastic_username": "",
     "elastic_password": ""
   }
   ```

   Update the values according to your Elasticsearch setup:
   - `elastic_url`: Your Elasticsearch cluster URL
   - `elastic_index`: Index name for storing documents (will be created if it doesn't exist)
   - `elastic_username`: Username for authentication (optional)
   - `elastic_password`: Password for authentication (optional)

## Usage

### Printing from Applications

1. Open any document in any macOS application (Preview, TextEdit, Safari, etc.)
2. Go to File → Print (or press ⌘+P)
3. Select **ElasticPrinter** from the printer dropdown
4. Click Print

Your document will be sent to Elasticsearch!

### Printing from Command Line

```bash
# Print a PDF file
lp -d ElasticPrinter document.pdf

# Print a text file
lp -d ElasticPrinter report.txt

# Print with title
lp -d ElasticPrinter -t "My Important Document" file.pdf
```

### Checking Print Status

View the log file to see print job status:
```bash
tail -f ~/.elasticprinter/logs/elastic-printer.log
```

### Viewing Documents in Elasticsearch

Query your printed documents:
```bash
# View all documents
curl -X GET "http://localhost:9200/printed-documents/_search?pretty"

# Search by title
curl -X GET "http://localhost:9200/printed-documents/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "title": "my document"
    }
  }
}
'
```

## Document Structure

Each printed document is stored in Elasticsearch with the following structure:

```json
{
  "timestamp": "2025-11-06T18:42:00.000Z",
  "job_id": "123",
  "title": "Document Title",
  "user": "username",
  "copies": "1",
  "options": "print-options",
  "document_data": "base64-encoded-document-content",
  "size_bytes": 12345
}
```

Fields:
- `timestamp`: When the document was printed (ISO 8601 format)
- `job_id`: CUPS job identifier
- `title`: Document title from print job
- `user`: Username of the person who printed
- `copies`: Number of copies requested
- `options`: CUPS print options
- `document_data`: The actual document data, base64-encoded
- `size_bytes`: Size of the document in bytes

## Configuration

### Configuration File Location

`~/.elasticprinter/config.json`

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `elastic_url` | Elasticsearch cluster URL | `http://localhost:9200` |
| `elastic_index` | Index name for documents | `printed-documents` |
| `elastic_username` | Username for authentication | `""` (empty) |
| `elastic_password` | Password for authentication | `""` (empty) |

### Environment Variables

You can also configure ElasticPrinter using environment variables (useful for testing):

- `ELASTIC_URL`: Elasticsearch URL
- `ELASTIC_INDEX`: Index name
- `ELASTIC_USERNAME`: Username
- `ELASTIC_PASSWORD`: Password

Environment variables take precedence over the config file if both are set.

## Troubleshooting

### Printer doesn't appear in print dialog

1. Check if the printer is installed:
   ```bash
   lpstat -p ElasticPrinter
   ```

2. If not found, reinstall:
   ```bash
   sudo ./install.sh
   ```

### Print jobs fail

1. Check the log file:
   ```bash
   tail -f ~/.elasticprinter/logs/elastic-printer.log
   ```

2. Verify Elasticsearch is running:
   ```bash
   curl -X GET "http://localhost:9200/"
   ```

3. Check configuration:
   ```bash
   cat ~/.elasticprinter/config.json
   ```

### Permission errors

The backend script must be owned by root and executable:
```bash
sudo chown root:wheel /usr/libexec/cups/backend/elastic-printer
sudo chmod 755 /usr/libexec/cups/backend/elastic-printer
```

## Uninstallation

To remove ElasticPrinter from your system:

```bash
sudo ./uninstall.sh
```

This will:
- Remove the ElasticPrinter from CUPS
- Remove the CUPS backend script

Note: Configuration files in `~/.elasticprinter/` are preserved. To remove them:
```bash
rm -rf ~/.elasticprinter
```

## Architecture

ElasticPrinter uses the CUPS (Common UNIX Printing System) backend interface:

1. **CUPS Backend**: The `elastic-printer` script acts as a CUPS backend
2. **Print Job Reception**: CUPS sends print jobs to the backend via stdin or file
3. **Document Processing**: The backend reads and base64-encodes the document
4. **Metadata Extraction**: Job metadata (title, user, etc.) is extracted from CUPS arguments
5. **Elasticsearch Storage**: Document and metadata are sent to Elasticsearch via REST API

```
┌─────────────┐     ┌──────────┐     ┌────────────────┐     ┌──────────────┐
│ Application │────▶│   CUPS   │────▶│ elastic-printer│────▶│ Elasticsearch│
└─────────────┘     └──────────┘     └────────────────┘     └──────────────┘
    (Print)         (Manage Jobs)    (Backend Script)       (Store Documents)
```

## Development

### Testing the Backend Script

Test the backend in discovery mode:
```bash
./elastic-printer
```

Test with a sample document:
```bash
./elastic-printer 1 testuser "Test Document" 1 "" test.pdf
```

### Debugging

Enable verbose logging by editing the backend script and changing the log level:
```python
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.DEBUG,  # Changed from INFO
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

## Security Considerations

- Documents are transmitted to Elasticsearch over HTTP by default. Use HTTPS URLs for production.
- Credentials in `config.json` are stored in plain text. Ensure proper file permissions:
  ```bash
  chmod 600 ~/.elasticprinter/config.json
  ```
- Consider using Elasticsearch API keys instead of username/password for better security.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built using CUPS (Common UNIX Printing System)
- Elasticsearch integration via the official REST API
- Inspired by the need for document archival and searchability