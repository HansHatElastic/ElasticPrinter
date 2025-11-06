"""Tests for Elasticsearch client."""
import unittest
from unittest.mock import Mock, patch, MagicMock

from src.elastic.client import ElasticClient


class TestElasticClient(unittest.TestCase):
    """Test ElasticClient class."""
    
    @patch('src.elastic.client.Elasticsearch')
    def test_client_initialization_with_api_key(self, mock_es):
        """Test client initialization with API key."""
        mock_instance = Mock()
        mock_instance.ping.return_value = True
        mock_es.return_value = mock_instance
        
        client = ElasticClient(
            host="https://localhost:9200",
            index="test-index",
            api_key_id="test_id",
            api_key="test_key"
        )
        
        self.assertEqual(client.index, "test-index")
        mock_instance.ping.assert_called_once()
    
    @patch('src.elastic.client.Elasticsearch')
    def test_client_initialization_with_basic_auth(self, mock_es):
        """Test client initialization with basic auth."""
        mock_instance = Mock()
        mock_instance.ping.return_value = True
        mock_es.return_value = mock_instance
        
        client = ElasticClient(
            host="https://localhost:9200",
            index="test-index",
            username="elastic",
            password="password"
        )
        
        self.assertEqual(client.index, "test-index")
        mock_instance.ping.assert_called_once()


if __name__ == "__main__":
    unittest.main()
