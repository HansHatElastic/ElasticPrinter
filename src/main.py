"""Main orchestrator for ElasticPrinter."""
import sys
import os
import logging
from typing import Optional

from utils.config_loader import ConfigLoader
from utils.logger import setup_logger
from converter.pdf_generator import PDFGenerator
from converter.metadata_extractor import MetadataExtractor
from elastic.client import ElasticClient


def process_print_job(
    input_file: str,
    job_id: str,
    user: str,
    title: str,
    copies: int,
    config: ConfigLoader,
    logger
) -> bool:
    """Process a print job: convert to PDF and index in Elasticsearch.
    
    Args:
        input_file: Path to print job input file
        job_id: Print job ID
        user: Username
        title: Job title
        copies: Number of copies
        config: Configuration loader
        logger: Logger instance
        
    Returns:
        True if successful, False otherwise
    """
    pdf_path = None
    
    try:
        # Initialize components
        processing_config = config.processing
        temp_dir = processing_config.get('temp_dir', '/tmp/elasticprinter')
        keep_pdfs = processing_config.get('keep_pdfs', False)
        
        # Generate PDF
        logger.info(f"Processing print job {job_id} from user {user}")
        pdf_generator = PDFGenerator(temp_dir=temp_dir)
        pdf_path = pdf_generator.convert_to_pdf(
            input_file=input_file,
            job_id=job_id,
            user=user
        )
        
        # Extract metadata
        logger.info(f"Extracting metadata from job and PDF")
        metadata_extractor = MetadataExtractor()
        job_metadata = metadata_extractor.extract_from_environment(
            job_id=job_id,
            user=user,
            title=title,
            copies=copies
        )
        pdf_metadata = metadata_extractor.extract_from_pdf(pdf_path)
        combined_metadata = metadata_extractor.combine_metadata(
            job_metadata,
            pdf_metadata
        )
        
        # Index in Elasticsearch
        logger.info(f"Indexing PDF in Elasticsearch")
        es_config = config.elasticsearch
        elastic_client = ElasticClient(
            host=es_config.get('host'),
            index=es_config.get('index', 'print-jobs'),
            pipeline=es_config.get('pipeline', 'attachment'),
            api_key_id=es_config.get('api_key_id'),
            api_key=es_config.get('api_key'),
            username=es_config.get('username'),
            password=es_config.get('password'),
            verify_certs=es_config.get('verify_certs', True)
        )
        
        # Ensure index and pipeline exist
        elastic_client.ensure_index_exists()
        elastic_client.ensure_pipeline_exists()
        
        # Index the document
        response = elastic_client.index_pdf(
            pdf_path=pdf_path,
            metadata=combined_metadata,
            doc_id=f"print-job-{job_id}"
        )
        
        logger.info(f"Successfully indexed document: {response['_id']}")
        elastic_client.close()
        
        # Cleanup
        if not keep_pdfs and pdf_path:
            pdf_generator.cleanup(pdf_path)
        
        return True
    except Exception as e:
        logger.error(f"Failed to process print job: {e}", exc_info=True)
        return False
    finally:
        # Cleanup on error if configured
        if pdf_path and not config.processing.get('keep_pdfs', False):
            try:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
            except:
                pass


def main():
    """Main entry point for CUPS backend."""
    # CUPS backend is called with specific arguments:
    # backend job-id user title copies options [file]
    
    # Load configuration
    config = ConfigLoader()
    
    # Setup logging
    log_config = config.logging_config
    log_level = log_config.get('level', 'INFO')
    
    # Set root logger level so all child loggers inherit it
    logging.basicConfig(level=getattr(logging, log_level.upper()))
    
    logger = setup_logger(
        name='elasticprinter',
        log_file=log_config.get('file'),
        level=log_level,
        console=True
    )
    
    logger.info("ElasticPrinter backend started")
    logger.info(f"Arguments: {sys.argv}")
    
    # Check if called correctly
    if len(sys.argv) < 6:
        logger.error("Usage: elasticprinter job-id user title copies options [file]")
        sys.exit(1)
    
    # Parse arguments
    job_id = sys.argv[1]
    user = sys.argv[2]
    title = sys.argv[3]
    copies = int(sys.argv[4])
    # options = sys.argv[5]  # Not used currently
    
    # Determine input source
    if len(sys.argv) == 7:
        # File provided as argument
        input_file = sys.argv[6]
        logger.info(f"Reading from file: {input_file}")
    else:
        # Read from stdin
        import tempfile
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.ps') as tmp:
            tmp.write(sys.stdin.buffer.read())
            input_file = tmp.name
        logger.info(f"Reading from stdin, saved to: {input_file}")
    
    # Process the print job
    success = process_print_job(
        input_file=input_file,
        job_id=job_id,
        user=user,
        title=title,
        copies=copies,
        config=config,
        logger=logger
    )
    
    # Cleanup temp file if created from stdin
    if len(sys.argv) != 7:
        try:
            os.remove(input_file)
        except:
            pass
    
    # Exit with appropriate code
    if success:
        logger.info("Print job processed successfully")
        sys.exit(0)
    else:
        logger.error("Print job processing failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
