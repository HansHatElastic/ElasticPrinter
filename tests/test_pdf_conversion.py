"""Tests for PDF conversion functionality."""
import unittest
import os
import tempfile
from pathlib import Path

from src.converter.pdf_generator import PDFGenerator


class TestPDFGenerator(unittest.TestCase):
    """Test PDFGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = PDFGenerator(temp_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_generate_filename(self):
        """Test filename generation."""
        filename = self.generator.generate_filename(
            job_id="123",
            user="testuser"
        )
        
        self.assertIn("print_job", filename)
        self.assertIn("testuser", filename)
        self.assertIn("123", filename)
        self.assertTrue(filename.endswith(".pdf"))
    
    def test_temp_dir_creation(self):
        """Test that temp directory is created."""
        self.assertTrue(os.path.exists(self.temp_dir))
        self.assertTrue(os.path.isdir(self.temp_dir))


if __name__ == "__main__":
    unittest.main()
