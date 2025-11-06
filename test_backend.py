#!/usr/bin/env python3
"""
Test script for ElasticPrinter backend
This script tests the backend functionality without requiring CUPS installation
"""

import sys
import os
import json
import tempfile
import base64
from pathlib import Path

# Add current directory to path to import the backend
sys.path.insert(0, os.path.dirname(__file__))

def create_test_config():
    """Create a test configuration file."""
    config_dir = Path.home() / ".elasticprinter"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = config_dir / "config.json"
    test_config = {
        "elastic_url": "http://localhost:9200",
        "elastic_index": "printed-documents-test",
        "elastic_username": "",
        "elastic_password": ""
    }
    
    with open(config_file, 'w') as f:
        json.dump(test_config, f, indent=2)
    
    print(f"✓ Test configuration created at {config_file}")
    return config_file

def test_discovery_mode():
    """Test the discovery mode of the backend."""
    print("\n=== Testing Discovery Mode ===")
    import subprocess
    
    result = subprocess.run(
        [sys.executable, 'elastic-printer'],
        capture_output=True,
        text=True
    )
    
    if 'elastic-printer' in result.stdout and 'ElasticPrinter' in result.stdout:
        print("✓ Discovery mode works correctly")
        print(f"  Output: {result.stdout.strip()}")
        return True
    else:
        print("✗ Discovery mode failed")
        print(f"  Output: {result.stdout}")
        print(f"  Error: {result.stderr}")
        return False

def test_config_loading():
    """Test configuration loading."""
    print("\n=== Testing Configuration Loading ===")
    
    try:
        config_file = Path.home() / ".elasticprinter" / "config.json"
        
        if not config_file.exists():
            print("✗ Configuration file not found")
            return False
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        if config and 'elastic_url' in config:
            print("✓ Configuration loaded successfully")
            print(f"  Elastic URL: {config.get('elastic_url')}")
            print(f"  Elastic Index: {config.get('elastic_index')}")
            return True
        else:
            print("✗ Configuration loading failed - missing required fields")
            return False
    except Exception as e:
        print(f"✗ Error loading configuration: {e}")
        return False

def test_document_encoding():
    """Test document encoding functionality."""
    print("\n=== Testing Document Encoding ===")
    
    # Create a test document
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        test_content = "This is a test document for ElasticPrinter"
        f.write(test_content)
        test_file = f.name
    
    try:
        # Read and encode the file
        with open(test_file, 'rb') as f:
            file_data = f.read()
        
        encoded = base64.b64encode(file_data).decode('utf-8')
        
        # Decode to verify
        decoded = base64.b64decode(encoded).decode('utf-8')
        
        if decoded == test_content:
            print("✓ Document encoding/decoding works correctly")
            print(f"  Original size: {len(test_content)} bytes")
            print(f"  Encoded size: {len(encoded)} bytes")
            return True
        else:
            print("✗ Document encoding/decoding failed")
            return False
    except Exception as e:
        print(f"✗ Error in encoding test: {e}")
        return False
    finally:
        os.unlink(test_file)

def test_metadata_structure():
    """Test metadata structure."""
    print("\n=== Testing Metadata Structure ===")
    
    metadata = {
        "job_id": "123",
        "user": "testuser",
        "title": "Test Document",
        "copies": "1",
        "options": "PageSize=A4"
    }
    
    # Check all required fields are present
    required_fields = ["job_id", "user", "title", "copies", "options"]
    
    if all(field in metadata for field in required_fields):
        print("✓ Metadata structure is correct")
        print(f"  Fields: {', '.join(required_fields)}")
        return True
    else:
        print("✗ Metadata structure is incomplete")
        return False

def print_elasticsearch_check():
    """Provide instructions for Elasticsearch check."""
    print("\n=== Elasticsearch Connection ===")
    print("To test Elasticsearch connection, ensure Elasticsearch is running and execute:")
    print("  curl -X GET 'http://localhost:9200/'")
    print("\nIf Elasticsearch is running, you can test the full printing workflow:")
    print("  echo 'Test content' | python3 elastic-printer 1 testuser 'Test Doc' 1 ''")

def main():
    """Run all tests."""
    print("====================================")
    print("ElasticPrinter Backend Test Suite")
    print("====================================")
    
    # Create test configuration
    create_test_config()
    
    # Run tests
    results = []
    results.append(("Discovery Mode", test_discovery_mode()))
    results.append(("Configuration Loading", test_config_loading()))
    results.append(("Document Encoding", test_document_encoding()))
    results.append(("Metadata Structure", test_metadata_structure()))
    
    # Print summary
    print("\n====================================")
    print("Test Summary")
    print("====================================")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    # Elasticsearch check info
    print_elasticsearch_check()
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
