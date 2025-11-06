"""Extract metadata from print jobs."""
import os
import pwd
from datetime import datetime
from typing import Dict, Any, Optional
from PyPDF2 import PdfReader

from utils.logger import get_logger

logger = get_logger(__name__)


class MetadataExtractor:
    """Extract metadata from print jobs and PDFs."""
    
    @staticmethod
    def extract_from_environment(
        job_id: str,
        user: str = None,
        title: str = None,
        copies: int = 1
    ) -> Dict[str, Any]:
        """Extract metadata from CUPS environment variables.
        
        CUPS provides job information through environment variables when
        running backend scripts.
        
        Args:
            job_id: Print job ID (from CUPS)
            user: Username (from CUPS, defaults to current user)
            title: Job title (from CUPS)
            copies: Number of copies (from CUPS)
            
        Returns:
            Dictionary containing job metadata
        """
        if user is None:
            try:
                user = pwd.getpwuid(os.getuid()).pw_name
            except Exception:
                user = "unknown"
        
        metadata = {
            "job_id": job_id,
            "user": user,
            "title": title or "Untitled",
            "copies": copies,
            "timestamp": datetime.now().isoformat(),
            "printer": os.environ.get("PRINTER", "ElasticPrinter"),
            "hostname": os.environ.get("HOSTNAME", "localhost"),
        }
        
        # Extract additional CUPS environment variables if available
        cups_vars = [
            "DEVICE_URI",
            "PRINTER_INFO",
            "PRINTER_LOCATION",
            "CONTENT_TYPE",
            "CHARSET",
            "LANG"
        ]
        
        for var in cups_vars:
            value = os.environ.get(var)
            if value:
                metadata[var.lower()] = value
        
        logger.info(f"Extracted job metadata: {metadata}")
        return metadata
    
    @staticmethod
    def extract_from_pdf(pdf_path: str) -> Dict[str, Any]:
        """Extract metadata from PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary containing PDF metadata
        """
        metadata = {
            "file_size": 0,
            "page_count": 0,
            "pdf_metadata": {}
        }
        
        try:
            # Get file size
            metadata["file_size"] = os.path.getsize(pdf_path)
            
            # Read PDF metadata
            with open(pdf_path, 'rb') as f:
                reader = PdfReader(f)
                metadata["page_count"] = len(reader.pages)
                
                # Extract PDF document information
                if reader.metadata:
                    pdf_meta = {}
                    for key, value in reader.metadata.items():
                        # Remove the leading '/' from PDF metadata keys
                        clean_key = key.lstrip('/')
                        pdf_meta[clean_key] = str(value) if value else ""
                    
                    metadata["pdf_metadata"] = pdf_meta
            
            logger.info(f"Extracted PDF metadata from {pdf_path}: {metadata}")
        except Exception as e:
            logger.error(f"Failed to extract PDF metadata from {pdf_path}: {e}")
        
        return metadata
    
    @staticmethod
    def combine_metadata(
        job_metadata: Dict[str, Any],
        pdf_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine job and PDF metadata into a single document.
        
        Args:
            job_metadata: Metadata from print job
            pdf_metadata: Metadata from PDF file
            
        Returns:
            Combined metadata dictionary
        """
        combined = {
            "print_job": job_metadata,
            "document": pdf_metadata,
            "indexed_at": datetime.now().isoformat()
        }
        
        return combined
