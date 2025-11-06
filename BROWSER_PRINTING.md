# Printing Web Pages to ElasticPrinter

ElasticPrinter's primary use case is archiving and searching web pages from your browser. This guide shows you how to set it up and use it effectively.

## Why Print Web Pages to Elasticsearch?

- **Archive Research**: Save articles, documentation, and research materials
- **Full-Text Search**: Search across all saved web pages instantly
- **Compliance**: Keep records of web content for legal/compliance purposes
- **Knowledge Base**: Build a searchable personal knowledge repository
- **Offline Access**: Have web content indexed even if the original goes offline

## Browser Setup

### Safari (macOS Default Browser)

Safari has native macOS printing integration. ElasticPrinter works automatically once installed.

**Quick Print:**
1. Navigate to any web page
2. Press `⌘P` (Command+P) or **File** → **Print**
3. Select **ElasticPrinter** from the printer dropdown
4. Click **Print**

**Tips:**
- Use "Print Backgrounds" for better formatting
- Adjust "Scale" if the page is too wide
- Add a descriptive title in the "Title" field for easier searching

### Chrome/Brave/Edge

Chrome-based browsers work well with system printers.

**Setup:**
1. Open Chrome
2. Go to **Settings** → **Advanced** → **Printing**
3. ElasticPrinter should appear automatically in the print dialog

**Quick Print:**
1. Navigate to any web page
2. Press `⌘P` (Command+P)
3. Change destination to **ElasticPrinter**
4. Click **Print**

**Pro Tip:** 
- Use "Save as PDF" destination first if you want to preview
- Then print the PDF to ElasticPrinter for better formatting

### Firefox

Firefox integrates with macOS printing system.

**Quick Print:**
1. Navigate to any web page
2. Press `⌘P` (Command+P)
3. Select **ElasticPrinter** from printer list
4. Click **Print**

**Best Practices:**
- Use "Simplify Page" for cleaner text extraction
- Remove headers/footers for better content extraction

## Optimal Print Settings

### For Best Text Extraction

```
✅ DO:
- Use "Actual Size" or 100% scale
- Enable "Print Backgrounds" for article sites
- Use descriptive titles (e.g., "AWS Lambda Documentation - Python")
- Print in portrait orientation when possible

❌ AVOID:
- Shrinking to fit (reduces OCR quality)
- Printing multi-column layouts at small scale
- Generic titles like "Untitled" or "Document"
```

### Recommended Browser Print Settings

**Safari:**
- **Scale:** 100%
- **Headers and Footers:** Off
- **Print backgrounds:** On (for articles/blogs)
- **Paper Size:** Letter or A4

**Chrome:**
- **Destination:** ElasticPrinter
- **Pages:** All
- **Layout:** Portrait
- **Margins:** Default
- **Options:** Background graphics (On)

**Firefox:**
- **Print to:** ElasticPrinter
- **Simplify page:** On (for articles)
- **Headers and Footers:** Off

## Workflow Examples

### Example 1: Research Article Archiving

```
Scenario: Saving news articles for research
Browser: Safari

1. Navigate to article (e.g., news site, blog post)
2. ⌘P to open print dialog
3. Printer: ElasticPrinter
4. Title: "Article Title - Source - Date"
5. Print
6. Article is now searchable in Elasticsearch
```

### Example 2: Documentation Archiving

```
Scenario: Saving technical documentation
Browser: Chrome

1. Open documentation page (e.g., AWS, Azure, Python docs)
2. ⌘P to open print dialog
3. Destination: ElasticPrinter
4. Title: "AWS Lambda Python - Developer Guide"
5. Print
6. Search later: "lambda python handler"
```

### Example 3: Legal/Compliance Archiving

```
Scenario: Preserving web evidence
Browser: Safari

1. Navigate to page that needs preservation
2. Note the exact URL and timestamp
3. ⌘P → ElasticPrinter
4. Title: Include URL and purpose (e.g., "Terms of Service - Company.com - 2025-11-06")
5. Print
6. Document is timestamped and indexed in Elasticsearch
```

## Advanced: Browser Automation

### Print Multiple Pages with AppleScript

```applescript
#!/usr/bin/osascript
-- Print current Safari page to ElasticPrinter

tell application "Safari"
    set pageTitle to name of current tab of front window
    set pageURL to URL of current tab of front window
end tell

tell application "System Events"
    keystroke "p" using command down
    delay 1
    -- Select ElasticPrinter
    keystroke tab
    keystroke "ElasticPrinter"
    keystroke return
    delay 0.5
    -- Set title
    keystroke tab
    keystroke tab
    keystroke pageTitle
    delay 0.5
    -- Print
    keystroke return
end tell
```

Save as `print-to-elastic.scpt` and run:
```bash
osascript print-to-elastic.scpt
```

### Chrome Extension (Future Enhancement)

A Chrome extension could:
- Add "Send to ElasticPrinter" button to browser toolbar
- Automatically fill in title and URL
- Batch print multiple tabs
- Tag pages for organization

## Searching Printed Web Pages

After printing web pages, search them in Elasticsearch:

### Search by Content

```bash
curl -H "Authorization: ApiKey YOUR_KEY" \
  -H "Content-Type: application/json" \
  -X POST "https://your-cluster:443/print-jobs/_search" \
  -d '{
    "query": {
      "match": {
        "attachment.content": "kubernetes deployment"
      }
    },
    "highlight": {
      "fields": {
        "attachment.content": {}
      }
    }
  }'
```

### Search by Title

```bash
curl -H "Authorization: ApiKey YOUR_KEY" \
  -H "Content-Type: application/json" \
  -X POST "https://your-cluster:443/print-jobs/_search" \
  -d '{
    "query": {
      "match": {
        "print_job.title": "AWS Lambda"
      }
    }
  }'
```

### Search by Date Range

```bash
curl -H "Authorization: ApiKey YOUR_KEY" \
  -H "Content-Type: application/json" \
  -X POST "https://your-cluster:443/print-jobs/_search" \
  -d '{
    "query": {
      "range": {
        "indexed_at": {
          "gte": "2025-11-01",
          "lte": "2025-11-30"
        }
      }
    }
  }'
```

## Kibana Dashboard

Create a Kibana dashboard to visualize your printed web pages:

1. **Discover View:**
   - Search all printed pages
   - Filter by date, user, title
   - View extracted content

2. **Visualizations:**
   - Timeline of printed pages
   - Top users (who prints most)
   - Most common topics (word cloud)
   - Content length distribution

3. **Saved Searches:**
   - "Technical Documentation"
   - "News Articles"
   - "Research Papers"
   - "Legal Documents"

## Troubleshooting Browser Printing

### ⚠️ Jobs Stuck in Queue (Common Issue)

**Symptom:** Print job appears in queue but doesn't get indexed in Elasticsearch

**Cause:** CUPS occasionally fails to execute the backend for queued jobs

**Solution 1 - Process Queue Manually:**
```bash
# Run the queue processor script
cd /path/to/elasticprinter
sudo ./scripts/process_queue.sh
```

**Solution 2 - Manual Processing:**
```bash
# Check queue
lpstat -o ElasticPrinter

# For each stuck job, cancel it and resubmit
cancel ElasticPrinter-XX

# Then print again or use direct backend testing
```

**Solution 3 - Direct Backend (Always Works):**
```bash
# Save web page as PDF first
# Then process directly with backend
cat /path/to/saved-page.pdf | sudo -u _lp \
  /usr/libexec/cups/backend/elasticprinter \
  "web-page-1" "$USER" "Page Title" 1 ""
```

### ElasticPrinter Not Appearing in Print Dialog

**Solution:**
```bash
# Restart CUPS
sudo launchctl stop org.cups.cupsd
sudo launchctl start org.cups.cupsd

# Verify printer is installed
lpstat -p ElasticPrinter
```

### Pages Printing Blank

**Cause:** Browser might be sending PostScript that can't be processed

**Solution:**
1. Try "Save as PDF" first in browser
2. Then print the PDF to ElasticPrinter
3. Or use "Print to File" then `lp -d ElasticPrinter file.pdf`

### Content Not Searchable

**Cause:** Text might be in images or complex formatting

**Solution:**
- Use "Reader View" in Safari before printing
- Use "Simplify Page" in Firefox
- Convert to PDF first, then print

### Large Pages Timing Out

**Solution:**
Update timeout in `/etc/elasticprinter/config.yaml`:
```yaml
processing:
  timeout: 60  # Increase from 30 to 60 seconds
```

## Best Practices Summary

1. **Use Descriptive Titles:** Always customize the print job title
2. **Enable Backgrounds:** For better visual preservation
3. **100% Scale:** Best for text extraction
4. **Save Important URLs:** Include URL in title for reference
5. **Regular Backups:** Back up your Elasticsearch index
6. **Use Tags in Title:** Add [Research], [Legal], [Docs] prefixes
7. **Check Logs:** Monitor `/var/log/elasticprinter/app.log` for issues

## Example Use Cases

### Academic Research
```
Print: Journal articles, papers, blog posts
Title Format: "[Research] Topic - Author - Date"
Search: Full-text across all research materials
```

### Software Development
```
Print: Documentation, Stack Overflow answers, tutorials
Title Format: "[Dev] Technology - Topic - Source"
Search: Code examples, error messages, API docs
```

### Legal/Compliance
```
Print: Terms of service, policies, legal notices
Title Format: "[Legal] Company - Document Type - Date"
Search: Specific terms, clauses, dates
```

### Personal Knowledge Management
```
Print: Articles, how-tos, recipes, guides
Title Format: "[Personal] Category - Title"
Search: Build a personal searchable wiki
```

## Next Steps

- Set up a Kibana dashboard for your printed pages
- Create browser bookmarklets for quick printing
- Set up alerts for specific keywords
- Export search results to other tools
- Share your Elasticsearch index with your team

---

**Happy Printing!** 🖨️ → ☁️ → 🔍
