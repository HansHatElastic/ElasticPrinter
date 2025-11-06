"""Elasticsearch client wrapper."""
import base64
import json
from typing import Dict, Any, Optional
from pathlib import Path

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, AuthenticationException

from utils.logger import get_logger

logger = get_logger(__name__)


class ElasticClient:
    """Elasticsearch client for indexing print jobs."""
    
    def __init__(
        self,
        host: str,
        index: str = "print-jobs",
        pipeline: str = "attachment",
        api_key_id: Optional[str] = None,
        api_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verify_certs: bool = True
    ):
        """Initialize Elasticsearch client.
        
        Args:
            host: Elasticsearch host URL
            index: Index name for print jobs
            pipeline: Ingest pipeline name
            api_key_id: API key ID for authentication
            api_key: API key secret
            username: Username for basic auth (if not using API key)
            password: Password for basic auth (if not using API key)
            verify_certs: Whether to verify SSL certificates
        """
        self.host = host
        self.index = index
        self.pipeline = pipeline
        
        # Configure authentication
        auth_config = {}
        if api_key:
            # For Elasticsearch Python client, use the encoded API key directly
            # If api_key looks like an encoded key (no colon, longer than 20 chars), use it directly
            # Otherwise combine id:secret and encode
            if api_key_id:
                # Both ID and secret provided - use tuple format
                auth_config['api_key'] = (api_key_id, api_key)
                logger.info("Using API key authentication (id + secret)")
            elif ':' not in api_key and len(api_key) > 20:
                # Already encoded - use directly
                auth_config['api_key'] = api_key
                logger.info("Using API key authentication (encoded)")
            else:
                # Assume it's just the secret, no ID - use directly
                auth_config['api_key'] = api_key
                logger.info("Using API key authentication (secret only)")
        elif username and password:
            auth_config['basic_auth'] = (username, password)
            logger.info("Using basic authentication")
        else:
            logger.warning("No authentication configured")
        
        # Create Elasticsearch client
        try:
            self.es = Elasticsearch(
                [host],
                **auth_config,
                verify_certs=verify_certs
            )
            
            # Test connection - use info() instead of ping() for serverless compatibility
            try:
                info = self.es.info()
                logger.info(f"Successfully connected to Elasticsearch at {host}")
                logger.info(f"Cluster: {info.get('cluster_name', 'unknown')}, Version: {info.get('version', {}).get('number', 'unknown')}")
            except Exception as ping_error:
                logger.error(f"Connection test failed with error: {type(ping_error).__name__}: {ping_error}")
                raise ConnectionError(f"Cannot connect to Elasticsearch: {ping_error}")
        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch client: {type(e).__name__}: {e}")
            raise
    
    def ensure_index_exists(self) -> bool:
        """Ensure the index exists with proper mapping.
        
        Returns:
            True if index exists or was created successfully
        """
        try:
            if self.es.indices.exists(index=self.index):
                logger.info(f"Index {self.index} already exists")
                return True
            
            # Load mapping from JSON file
            mapping_file = Path(__file__).parent / "index_mapping.json"
            with open(mapping_file, 'r') as f:
                mapping = json.load(f)
            
            # Create index with mapping
            self.es.indices.create(index=self.index, body=mapping)
            logger.info(f"Created index {self.index} with mapping")
            return True
        except Exception as e:
            logger.error(f"Failed to ensure index exists: {e}")
            return False
    
    def ensure_pipeline_exists(self) -> bool:
        """Ensure the ingest attachment pipeline exists.
        
        Returns:
            True if pipeline exists or was created successfully
        """
        try:
            # Check if pipeline exists
            if self.es.ingest.get_pipeline(id=self.pipeline, ignore=[404]):
                logger.info(f"Pipeline {self.pipeline} already exists")
                return True
        except:
            pass
        
        try:
            # Create attachment pipeline
            pipeline_body = {
                "description": "Extract attachment information from PDFs",
                "processors": [
                    {
                        "attachment": {
                            "field": "data",
                            "target_field": "attachment",
                            "indexed_chars": -1,
                            "ignore_missing": True
                        }
                    },
                    {
                        "remove": {
                            "field": "data",
                            "ignore_missing": True
                        }
                    }
                ]
            }
            
            self.es.ingest.put_pipeline(id=self.pipeline, body=pipeline_body)
            logger.info(f"Created ingest pipeline {self.pipeline}")
            return True
        except Exception as e:
            logger.error(f"Failed to create pipeline: {e}")
            return False
    
    def index_pdf(
        self,
        pdf_path: str,
        metadata: Dict[str, Any],
        doc_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Index a PDF document with metadata.
        
        Args:
            pdf_path: Path to PDF file
            metadata: Document metadata
            doc_id: Optional document ID (if None, auto-generated)
            
        Returns:
            Elasticsearch response
            
        Raises:
            Exception: If indexing fails
        """
        try:
            # Read PDF and encode as base64
            with open(pdf_path, 'rb') as f:
                pdf_data = f.read()
            
            encoded_pdf = base64.b64encode(pdf_data).decode('utf-8')
            
            # Prepare document
            document = {
                "data": encoded_pdf,
                **metadata
            }
            
            # Index document with pipeline
            response = self.es.index(
                index=self.index,
                id=doc_id,
                document=document,
                pipeline=self.pipeline
            )
            
            logger.info(f"Indexed PDF {pdf_path} as document {response['_id']}")
            return response
        except Exception as e:
            logger.error(f"Failed to index PDF {pdf_path}: {e}")
            raise
    
    def search(self, query: Dict[str, Any], size: int = 10) -> Dict[str, Any]:
        """Search for documents.
        
        Args:
            query: Elasticsearch query DSL
            size: Number of results to return
            
        Returns:
            Search results
        """
        try:
            response = self.es.search(
                index=self.index,
                body=query,
                size=size
            )
            return response
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """Retrieve a document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document data
        """
        try:
            response = self.es.get(index=self.index, id=doc_id)
            return response
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            raise
    
    def close(self) -> None:
        """Close the Elasticsearch connection."""
        try:
            self.es.close()
            logger.info("Closed Elasticsearch connection")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")
