#!/usr/bin/env python3
"""
Main pipeline script to process PDFs and populate vector database
"""

import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.pdf_parser import PDFParser
from scripts.vector_db import VectorDB
from config.config import settings

# Setup logging
log_file = Path(settings.logs_path) / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Pipeline:
    def __init__(self):
        """Initialize the pipeline"""
        self.parser = PDFParser()
        self.vector_db = VectorDB()
        logger.info("Pipeline initialized")
    
    def process_single_pdf(
        self,
        pdf_path: str,
        class_num: int,
        subject: str,
        auto_add: bool = True
    ) -> List[Dict[str, Any]]:
        """Process a single PDF file"""
        logger.info(f"Processing PDF: {pdf_path}")
        logger.info(f"Class: {class_num}, Subject: {subject}")
        
        # Check if file exists
        if not Path(pdf_path).exists():
            logger.error(f"File not found: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Parse PDF
        try:
            chunks = self.parser.parse_pdf(pdf_path, class_num, subject)
            logger.info(f"Extracted {len(chunks)} chunks from PDF")
            
            # Auto-add to vector database
            if auto_add and chunks:
                added = self.vector_db.add_chunks(chunks)
                logger.info(f"Added {added} chunks to vector database")
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise
    
    def process_multiple_pdfs(
        self,
        pdf_configs: List[Dict[str, Any]],
        auto_add: bool = True
    ) -> Dict[str, Any]:
        """
        Process multiple PDFs
        
        pdf_configs format:
        [
            {'path': 'file.pdf', 'class': 8, 'subject': 'Math'},
            {'path': 'file2.pdf', 'class': 9, 'subject': 'Science'}
        ]
        """
        logger.info(f"Processing {len(pdf_configs)} PDF files")
        
        results = {
            'total_pdfs': len(pdf_configs),
            'successful': 0,
            'failed': 0,
            'total_chunks': 0,
            'details': []
        }
        
        for config in pdf_configs:
            try:
                pdf_path = config['path']
                class_num = config['class']
                subject = config['subject']
                
                chunks = self.process_single_pdf(
                    pdf_path=pdf_path,
                    class_num=class_num,
                    subject=subject,
                    auto_add=auto_add
                )
                
                results['successful'] += 1
                results['total_chunks'] += len(chunks)
                results['details'].append({
                    'pdf': pdf_path,
                    'class': class_num,
                    'subject': subject,
                    'chunks': len(chunks),
                    'status': 'success'
                })
                
            except Exception as e:
                logger.error(f"Failed to process {config.get('path', 'unknown')}: {str(e)}")
                results['failed'] += 1
                results['details'].append({
                    'pdf': config.get('path', 'unknown'),
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results
    
    def process_from_config_file(self, config_file: str) -> Dict[str, Any]:
        """
        Process PDFs from a JSON configuration file
        
        Config file format:
        {
            "pdfs": [
                {"path": "file.pdf", "class": 8, "subject": "Math"},
                {"path": "file2.pdf", "class": 9, "subject": "Science"}
            ]
        }
        """
        logger.info(f"Loading configuration from: {config_file}")
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            pdf_configs = config.get('pdfs', [])
            return self.process_multiple_pdfs(pdf_configs)
            
        except Exception as e:
            logger.error(f"Error loading config file: {str(e)}")
            raise
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database"""
        return self.vector_db.get_collection_stats()
    
    def reset_database(self, confirm: bool = False):
        """Reset the vector database (WARNING: deletes all data)"""
        if not confirm:
            logger.warning("Database reset requires confirmation. Set confirm=True")
            return
        
        logger.warning("Resetting vector database - all data will be deleted!")
        self.vector_db.reset_database()
        logger.info("Database reset complete")
    
    def export_chunks_to_json(self, output_file: str, limit: int = None):
        """Export chunks to JSON file for inspection"""
        logger.info(f"Exporting chunks to {output_file}")
        
        try:
            # Get all chunks (or limited number)
            sample = self.vector_db.collection.get(limit=limit)
            
            export_data = {
                'total_chunks': len(sample['ids']),
                'export_date': datetime.now().isoformat(),
                'chunks': []
            }
            
            for i in range(len(sample['ids'])):
                chunk = {
                    'id': sample['ids'][i],
                    'content': sample['documents'][i],
                    'metadata': sample['metadatas'][i]
                }
                export_data['chunks'].append(chunk)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(export_data['chunks'])} chunks to {output_file}")
            
        except Exception as e:
            logger.error(f"Error exporting chunks: {str(e)}")
            raise

def main():
    """Main entry point with command-line interface"""
    import argparse
    
    parser_cli = argparse.ArgumentParser(
        description='Education RAG System - PDF Processing Pipeline'
    )
    
    parser_cli.add_argument(
        '--pdf',
        type=str,
        help='Path to single PDF file'
    )
    parser_cli.add_argument(
        '--class',
        dest='class_num',
        type=int,
        help='Class number (5-10)'
    )
    parser_cli.add_argument(
        '--subject',
        type=str,
        help='Subject name (e.g., Mathematics, Science)'
    )
    parser_cli.add_argument(
        '--config',
        type=str,
        help='Path to JSON config file with multiple PDFs'
    )
    parser_cli.add_argument(
        '--stats',
        action='store_true',
        help='Show database statistics'
    )
    parser_cli.add_argument(
        '--export',
        type=str,
        help='Export chunks to JSON file'
    )
    parser_cli.add_argument(
        '--reset',
        action='store_true',
        help='Reset database (WARNING: deletes all data)'
    )
    
    args = parser_cli.parse_args()
    
    # Initialize pipeline
    pipeline = Pipeline()
    
    # Process based on arguments
    if args.stats:
        print("\n" + "="*70)
        print("DATABASE STATISTICS")
        print("="*70)
        stats = pipeline.get_database_stats()
        print(json.dumps(stats, indent=2))
        
    elif args.reset:
        confirm = input("Are you sure you want to reset the database? Type 'yes' to confirm: ")
        if confirm.lower() == 'yes':
            pipeline.reset_database(confirm=True)
            print("Database reset successfully")
        else:
            print("Reset cancelled")
    
    elif args.export:
        pipeline.export_chunks_to_json(args.export)
        print(f"Chunks exported to {args.export}")
    
    elif args.config:
        print(f"\nProcessing PDFs from config file: {args.config}")
        results = pipeline.process_from_config_file(args.config)
        print("\n" + "="*70)
        print("PROCESSING RESULTS")
        print("="*70)
        print(json.dumps(results, indent=2))
    
    elif args.pdf and args.class_num and args.subject:
        print(f"\nProcessing single PDF:")
        print(f"  File: {args.pdf}")
        print(f"  Class: {args.class_num}")
        print(f"  Subject: {args.subject}")
        
        chunks = pipeline.process_single_pdf(
            pdf_path=args.pdf,
            class_num=args.class_num,
            subject=args.subject
        )
        
        print(f"\n✅ Successfully processed {len(chunks)} chunks")
        print(f"✅ Added to vector database")
        
        # Show sample
        if chunks:
            print("\nSample chunk:")
            print(f"Content: {chunks[0]['content'][:200]}...")
            print(f"Metadata: {json.dumps(chunks[0]['metadata'], indent=2)}")
    
    else:
        parser_cli.print_help()
        print("\n" + "="*70)
        print("QUICK START EXAMPLES")
        print("="*70)
        print("\n1. Process a single PDF:")
        print("   python main_pipeline.py --pdf textbook.pdf --class 8 --subject Mathematics")
        print("\n2. Process multiple PDFs from config:")
        print("   python main_pipeline.py --config pdfs_config.json")
        print("\n3. View database statistics:")
        print("   python main_pipeline.py --stats")
        print("\n4. Export chunks to JSON:")
        print("   python main_pipeline.py --export chunks_export.json")

if __name__ == "__main__":
    main()
