# Getting Started with ElasticPrinter

Welcome to ElasticPrinter! This guide will get you up and running in under 10 minutes.

## What is ElasticPrinter?

ElasticPrinter is a virtual printer for macOS that automatically sends your print jobs to Elasticsearch, making all your printed documents searchable in the cloud.

**Use Cases:**
- Archive all printed documents for compliance
- Search printed documents by content
- Track who prints what and when
- Build a searchable document repository
- Audit print activity

## Prerequisites Checklist

Before you start, make sure you have:

- [ ] macOS computer (10.15 or later)
- [ ] Python 3.9 or higher installed
- [ ] Elasticsearch cluster (cloud or self-hosted)
- [ ] Elasticsearch API key or credentials
- [ ] Administrator access (for installation)

## 5-Minute Quick Start

### 1. Get Elasticsearch Ready (2 minutes)

#### Option A: Elasticsearch Serverless (Recommended)
1. Go to https://cloud.elastic.co
2. Create a free account if you don't have one
3. Create a new Serverless project
4. Go to **Management** → **API Keys** → **Create API Key**
5. Copy the **encoded API key** (looks like: `abc123xyz...`)

#### Option B: Self-Managed Elasticsearch
- Have your Elasticsearch URL ready (e.g., `https://localhost:9200`)
- Have your credentials (username/password or API key)

### 2. Download ElasticPrinter (30 seconds)

```bash
cd ~/Projects  # or wherever you keep projects
git clone https://github.com/yourusername/elasticprinter.git
cd elasticprinter
```

### 3. Configure (1 minute)

```bash
# Create config directory
sudo mkdir -p /etc/elasticprinter

# Copy and edit config
sudo cp config/config.yaml.example /etc/elasticprinter/config.yaml
sudo nano /etc/elasticprinter/config.yaml
```

Edit these two lines:
```yaml
  host: "https://YOUR-CLUSTER-ID.elastic.cloud:443"  # Your Elasticsearch URL
  api_key: "YOUR_ENCODED_API_KEY"  # Paste your API key here
```

Save (Ctrl+O, Enter) and exit (Ctrl+X).

### 4. Install (1 minute)

```bash
sudo ./scripts/install_printer.sh
```

This installs everything automatically. Enter your password when prompted.

### 5. Test (30 seconds)

```bash
# Enable the printer
sudo cupsenable ElasticPrinter

# Test it
echo "Hello ElasticPrinter! - $(date)" | sudo -u _lp /usr/libexec/cups/backend/elasticprinter 1001 testuser "My First Document" 1 ""
```

You should see: `Successfully indexed document: print-job-1001`

### 6. Verify (30 seconds)

Check that your document is in Elasticsearch:

```bash
curl -H "Authorization: ApiKey YOUR_API_KEY" \
  "https://YOUR-CLUSTER.elastic.cloud:443/print-jobs/_doc/print-job-1001" \
  | python3 -m json.tool
```

You should see your document with the content "Hello ElasticPrinter!"

## Start Printing Web Pages!

That's it! Now you can print from any browser or macOS application:

### Quick Test - Print a Web Page

1. **Open Safari** (or Chrome, Firefox)
2. Navigate to **any web page** (e.g., news article, documentation)
3. Press **⌘P** (Command+P)
4. Select **ElasticPrinter** from the printer dropdown
5. Optionally customize the **title** (e.g., "AWS Lambda Python Guide")
6. Click **Print**

**Your web page is now indexed and searchable in Elasticsearch!** 🎉

### Print from Any App

ElasticPrinter also works with:
- **TextEdit** - Print text documents
- **Preview** - Print PDFs and images
- **Pages/Word** - Print documents
- **Safari/Chrome/Firefox** - Print web pages (primary use case)

## What's Next?

### Search Your Printed Web Pages

```bash
# Search for content (e.g., find all pages mentioning "kubernetes")
curl -H "Authorization: ApiKey YOUR_API_KEY" \
  "https://YOUR-CLUSTER.elastic.cloud:443/print-jobs/_search" \
  -H 'Content-Type: application/json' \
  -d'{"query":{"match":{"attachment.content":"kubernetes"}}}'

# Or use Kibana's Discover tab for visual searching
```

### Advanced Browser Printing

See the [Browser Printing Guide](BROWSER_PRINTING.md) for:
- Browser-specific tips (Safari, Chrome, Firefox)
- Optimal print settings for web pages
- Workflow examples (research, documentation, compliance)
- Searching and organizing archived pages
- AppleScript automation for batch printing

### View Logs

```bash
tail -f /var/log/elasticprinter/app.log
```

### Enable Debug Logging

Edit `/etc/elasticprinter/config.yaml`:
```yaml
logging:
  level: "DEBUG"  # Change from INFO
```

### Keep Processed Files

Edit `/etc/elasticprinter/config.yaml`:
```yaml
processing:
  keep_pdfs: true  # Change from false
```

Files will be saved in `/tmp/elasticprinter/` for inspection.

## Common Tasks

### Check Printer Status
```bash
lpstat -p ElasticPrinter
```

### Enable/Disable Printer
```bash
sudo cupsenable ElasticPrinter   # Enable
sudo cupsdisable ElasticPrinter  # Disable
```

### View Print Queue
```bash
lpstat -o
```

### Cancel Print Jobs
```bash
cancel -a ElasticPrinter  # Cancel all
cancel ElasticPrinter-5   # Cancel specific job
```

## Troubleshooting

### Printer not appearing?
```bash
sudo cupsenable ElasticPrinter
lpstat -p ElasticPrinter
```

### Elasticsearch connection failing?
```bash
# Test connection
curl -v -H "Authorization: ApiKey YOUR_KEY" \
  "https://YOUR-CLUSTER.elastic.cloud:443/"
```

Common issues:
- Missing port `:443` in URL
- Wrong API key (use the **encoded** key)
- Firewall blocking HTTPS traffic

### No logs appearing?
```bash
# Check log file
ls -l /var/log/elasticprinter/app.log

# Fix permissions if needed
sudo touch /var/log/elasticprinter/app.log
sudo chmod 666 /var/log/elasticprinter/app.log
```

### Print jobs failing?
```bash
# Check logs
tail -50 /var/log/elasticprinter/app.log

# Check CUPS logs
sudo tail -50 /var/log/cups/error_log
```

## Learn More

- **Full Documentation**: [README.md](README.md)
- **Detailed Installation**: [INSTALLATION.md](INSTALLATION.md)
- **Quick Reference**: [QUICKREF.md](QUICKREF.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

## Get Help

- Check the logs: `tail -f /var/log/elasticprinter/app.log`
- Review [INSTALLATION.md](INSTALLATION.md) for detailed troubleshooting
- Open an issue on GitHub
- Check existing issues for solutions

## Uninstall

If you need to remove ElasticPrinter:

```bash
sudo ./scripts/uninstall_printer.sh
```

---

**Congratulations!** You now have a cloud-connected virtual printer that makes all your documents searchable. Happy printing! 🎉
