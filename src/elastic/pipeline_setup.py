"""Setup Elasticsearch pipeline and index."""
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.elastic.client import ElasticClient
from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader

logger = get_logger(__name__)


def setup_elasticsearch(config: ConfigLoader) -> bool:
    """Set up Elasticsearch index and pipeline.
    
    Args:
        config: Configuration loader instance
        
    Returns:
        True if setup successful, False otherwise
    """
    try:
        # Create Elasticsearch client
        es_config = config.elasticsearch
        
        client = ElasticClient(
            host=es_config.get('host'),
            index=es_config.get('index', 'print-jobs'),
            pipeline=es_config.get('pipeline', 'attachment'),
            api_key_id=es_config.get('api_key_id'),
            api_key=es_config.get('api_key'),
            username=es_config.get('username'),
            password=es_config.get('password'),
            verify_certs=es_config.get('verify_certs', True)
        )
        
        # Ensure index exists
        if not client.ensure_index_exists():
            logger.error("Failed to create/verify index")
            return False
        
        # Ensure pipeline exists
        if not client.ensure_pipeline_exists():
            logger.error("Failed to create/verify pipeline")
            return False
        
        logger.info("Elasticsearch setup completed successfully")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Elasticsearch setup failed: {e}")
        return False


if __name__ == "__main__":
    # Allow running as standalone script for initial setup
    import sys
    
    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    config = ConfigLoader(config_path)
    
    if setup_elasticsearch(config):
        print("✓ Elasticsearch setup completed successfully")
        sys.exit(0)
    else:
        print("✗ Elasticsearch setup failed")
        sys.exit(1)
