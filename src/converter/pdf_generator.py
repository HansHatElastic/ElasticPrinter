"""PDF generator from print jobs."""
import os
import subprocess
import tempfile
from datetime import datetime
from typing import Optional
from pathlib import Path

from utils.logger import get_logger

logger = get_logger(__name__)


class PDFGenerator:
    """Generate PDFs from print job data."""
    
    def __init__(self, temp_dir: str = "/tmp/elasticprinter"):
        """Initialize PDF generator.
        
        Args:
            temp_dir: Directory for temporary PDF files
        """
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"PDFGenerator initialized with temp_dir: {self.temp_dir}")
    
    def generate_filename(self, job_id: str, user: str) -> str:
        """Generate unique filename for PDF.
        
        Args:
            job_id: Print job ID
            user: Username who submitted the job
            
        Returns:
            Filename for the PDF
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"print_job_{user}_{job_id}_{timestamp}.pdf"
    
    def convert_to_pdf(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        job_id: str = "unknown",
        user: str = "unknown"
    ) -> str:
        """Convert print job to PDF.
        
        Args:
            input_file: Path to input file (PostScript or other print format)
            output_file: Path to output PDF file. If None, generates one.
            job_id: Print job ID for naming
            user: Username for naming
            
        Returns:
            Path to generated PDF file
            
        Raises:
            RuntimeError: If conversion fails
        """
        if output_file is None:
            filename = self.generate_filename(job_id, user)
            output_file = str(self.temp_dir / filename)
        
        logger.info(f"Converting {input_file} to PDF: {output_file}")
        
        # For now, just copy the input file as the "PDF" - Elasticsearch attachment processor can handle it
        # TODO: Implement proper PDF conversion when needed
        import shutil
        try:
            shutil.copy2(input_file, output_file)
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                logger.info(f"Saved print job as: {output_file}")
                return output_file
            else:
                raise RuntimeError("Failed to copy print job file")
        except Exception as e:
            logger.error(f"Failed to save print job: {e}")
            raise RuntimeError(f"Failed to save print job: {e}")
    
    def _convert_with_cupsfilter(self, input_file: str, output_file: str) -> bool:
        """Convert using cupsfilter command.
        
        Args:
            input_file: Input file path
            output_file: Output PDF path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.debug(f"Attempting cupsfilter conversion: {input_file} -> {output_file}")
            with open(output_file, 'wb') as out_f:
                result = subprocess.run(
                    ['/usr/sbin/cupsfilter', '-m', 'application/pdf', input_file],
                    stdout=out_f,
                    stderr=subprocess.PIPE,
                    check=True,
                    timeout=60
                )
            exists = os.path.exists(output_file)
            size = os.path.getsize(output_file) if exists else 0
            logger.debug(f"cupsfilter completed: exists={exists}, size={size}")
            return exists and size > 0
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.debug(f"cupsfilter conversion failed: {type(e).__name__}: {e}")
            if hasattr(e, 'stderr') and e.stderr:
                logger.debug(f"cupsfilter stderr: {e.stderr.decode('utf-8', errors='ignore')}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in cupsfilter: {type(e).__name__}: {e}")
            return False
    
    def _convert_with_pstopdf(self, input_file: str, output_file: str) -> bool:
        """Convert using macOS pstopdf command.
        
        Args:
            input_file: Input file path
            output_file: Output PDF path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ['pstopdf', input_file, '-o', output_file],
                capture_output=True,
                check=True,
                timeout=60
            )
            return os.path.exists(output_file) and os.path.getsize(output_file) > 0
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.debug(f"pstopdf conversion failed: {e}")
            return False
    
    def _convert_with_ghostscript(self, input_file: str, output_file: str) -> bool:
        """Convert using Ghostscript.
        
        Args:
            input_file: Input file path
            output_file: Output PDF path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                [
                    'gs',
                    '-dBATCH',
                    '-dNOPAUSE',
                    '-sDEVICE=pdfwrite',
                    '-dCompatibilityLevel=1.4',
                    '-dPDFSETTINGS=/printer',
                    f'-sOutputFile={output_file}',
                    input_file
                ],
                capture_output=True,
                check=True,
                timeout=60
            )
            return os.path.exists(output_file) and os.path.getsize(output_file) > 0
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.debug(f"Ghostscript conversion failed: {e}")
            return False
    
    def cleanup(self, pdf_path: str) -> None:
        """Delete temporary PDF file.
        
        Args:
            pdf_path: Path to PDF file to delete
        """
        try:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                logger.info(f"Cleaned up temporary PDF: {pdf_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup PDF {pdf_path}: {e}")
