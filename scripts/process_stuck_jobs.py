#!/usr/bin/env python3
"""
Process stuck ElasticPrinter jobs from CUPS queue.

This script manually processes print jobs that are stuck in the CUPS queue
and sends them to Elasticsearch.

Usage:
    sudo python3 scripts/process_stuck_jobs.py
"""

import subprocess
import sys
import os
import re
from pathlib import Path

def run_command(cmd, check=True):
    """Run a shell command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        return None
    return result.stdout.strip()

def get_queued_jobs():
    """Get list of ElasticPrinter jobs in queue."""
    output = run_command("lpstat -o ElasticPrinter", check=False)
    if not output:
        return []
    
    jobs = []
    for line in output.split('\n'):
        if 'ElasticPrinter-' in line:
            job_name = line.split()[0]
            jobs.append(job_name)
    return jobs

def process_job(job_name, user):
    """Process a single print job."""
    # Extract job number
    match = re.search(r'ElasticPrinter-(\d+)', job_name)
    if not match:
        return False
    
    job_num = match.group(1)
    spool_file = f"/var/spool/cups/d{int(job_num):05d}-001"
    
    if not os.path.exists(spool_file):
        print(f"  ⚠️  Spool file not found: {spool_file}")
        return False
    
    # Get file size
    size_bytes = os.path.getsize(spool_file)
    size_mb = size_bytes / (1024 * 1024)
    print(f"  ✓ Found spool file ({size_mb:.1f} MB)")
    
    # Create job details
    job_id = f"browser-page-{job_num}"
    title = f"Browser Page {job_num}"
    
    print(f"  Job ID: {job_id}")
    print(f"  Title: {title}")
    print(f"  User: {user}")
    print(f"  Processing...")
    
    # Process with backend
    cmd = f"sudo -u _lp /usr/libexec/cups/backend/elasticprinter '{job_id}' '{user}' '{title}' 1 '' < {spool_file}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    # Check if successful
    if "Successfully indexed" in result.stdout or "Successfully indexed" in result.stderr:
        print(f"  ✅ Successfully indexed!")
        return True
    else:
        print(f"  ❌ Failed to index")
        if result.stderr:
            print(f"  Error: {result.stderr[:200]}")
        return False

def main():
    """Main function."""
    print("=== ElasticPrinter Queue Processor ===\n")
    
    # Check if running as root
    if os.geteuid() != 0:
        print("ERROR: This script must be run as root (use sudo)")
        sys.exit(1)
    
    # Get current user (before sudo)
    user = os.environ.get('SUDO_USER', os.environ.get('USER', 'unknown'))
    
    # Get queued jobs
    jobs = get_queued_jobs()
    
    if not jobs:
        print("✓ No jobs in ElasticPrinter queue\n")
        return 0
    
    print(f"Found {len(jobs)} job(s) in queue:\n")
    
    # Process each job
    processed = 0
    failed = 0
    
    for i, job in enumerate(jobs, 1):
        print(f"[{i}/{len(jobs)}] Processing {job}...")
        
        if process_job(job, user):
            processed += 1
        else:
            failed += 1
        
        # Cancel job from queue
        print(f"  Removing from queue...")
        run_command(f"cancel {job}", check=False)
        print()
    
    # Summary
    print("=== Summary ===")
    print(f"  ✅ Successfully processed: {processed}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📊 Total: {len(jobs)}\n")
    
    if processed > 0:
        print("✓ Check Elasticsearch for your documents:")
        print('  curl -s -H "Authorization: ApiKey YOUR_KEY" \\')
        print('    "https://your-cluster:443/print-jobs/_search?size=10&sort=indexed_at:desc"')
    
    print("\nDone!")
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nAborted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
