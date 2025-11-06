#!/bin/bash
#
# Process stuck ElasticPrinter jobs manually
# This script processes jobs that are stuck in the CUPS queue
#
# Usage: sudo ./scripts/process_queue.sh
#

set -e

echo "=== ElasticPrinter Queue Processor ==="
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: This script must be run as root (use sudo)"
    exit 1
fi

# Load config to get Elasticsearch details
CONFIG_FILE="/etc/elasticprinter/config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Config file not found: $CONFIG_FILE"
    exit 1
fi

# Get list of ElasticPrinter jobs
JOBS=$(lpstat -o ElasticPrinter 2>/dev/null | awk '{print $1}' || echo "")

if [ -z "$JOBS" ]; then
    echo "✓ No jobs in ElasticPrinter queue"
    echo
    echo "Recent documents in Elasticsearch:"
    echo "  (Check with: curl -H \"Authorization: ApiKey YOUR_KEY\" https://your-cluster:443/print-jobs/_search?size=5&sort=indexed_at:desc)"
    exit 0
fi

echo "Found jobs in queue:"
lpstat -o ElasticPrinter
echo

# Count jobs
JOB_COUNT=$(echo "$JOBS" | wc -l | tr -d ' ')
echo "Processing $JOB_COUNT job(s)..."
echo

# Process each job
PROCESSED=0
FAILED=0

for JOB in $JOBS; do
    echo "[$((PROCESSED + FAILED + 1))/$JOB_COUNT] Processing $JOB..."
    
    # Extract job number (e.g., ElasticPrinter-37 -> 37)
    JOB_NUM=$(echo $JOB | cut -d'-' -f2)
    
    # Try to find the spool file (format: dNNNNN-001)
    SPOOL_FILE="/var/spool/cups/d$(printf "%05d" $JOB_NUM)-001"
    
    if [ ! -f "$SPOOL_FILE" ]; then
        echo "  ⚠️  Spool file not found: $SPOOL_FILE"
        echo "  Skipping and canceling job..."
        cancel $JOB 2>/dev/null || true
        FAILED=$((FAILED + 1))
        echo
        continue
    fi
    
    echo "  ✓ Found spool file ($(du -h $SPOOL_FILE | cut -f1))"
    
    # Get job info
    USER=$(lpstat -o $JOB -l 2>/dev/null | grep -i "submitted" | awk '{print $5}' || echo "$USER")
    [ -z "$USER" ] && USER="unknown"
    
    # Create a job ID
    JOB_ID="web-page-$(date +%s)-$JOB_NUM"
    TITLE="Web Page $JOB_NUM - $(date '+%Y-%m-%d %H:%M')"
    
    echo "  User: $USER"
    echo "  Job ID: $JOB_ID"
    echo "  Title: $TITLE"
    
    # Process with backend
    echo "  Processing with backend..."
    if sudo -u _lp /usr/libexec/cups/backend/elasticprinter \
        "$JOB_ID" "$USER" "$TITLE" 1 "" < "$SPOOL_FILE" 2>&1 | \
        grep -q "Successfully indexed"; then
        echo "  ✅ Successfully indexed!"
        PROCESSED=$((PROCESSED + 1))
    else
        echo "  ❌ Failed to index"
        FAILED=$((FAILED + 1))
    fi
    
    # Cancel the job from queue
    echo "  Removing job from queue..."
    cancel $JOB 2>/dev/null || true
    
    echo
done

echo "=== Summary ==="
echo "  ✅ Successfully processed: $PROCESSED"
echo "  ❌ Failed: $FAILED"
echo "  📊 Total: $JOB_COUNT"
echo

if [ $PROCESSED -gt 0 ]; then
    echo "✓ Check Elasticsearch for your documents:"
    echo "  curl -s -H \"Authorization: ApiKey YOUR_KEY\" \\"
    echo "    \"https://your-cluster:443/print-jobs/_search?size=10&sort=indexed_at:desc\" | jq '.hits.hits[]._source.print_job.title'"
fi

echo
echo "Done!"
