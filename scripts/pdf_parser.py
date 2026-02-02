import pdfplumber
import re
import logging
from typing import List, Dict, Any
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFParser:
    def __init__(self):
        self.current_chapter = "Unknown"
        self.current_topic = "General"
        
    def extract_chapter(self, text: str) -> str:
        """Extract chapter name from text"""
        chapter_patterns = [
            r'Chapter\s+(\d+)[:\s]+(.+?)[\n\r]',
            r'CHAPTER\s+(\d+)[:\s]+(.+?)[\n\r]',
            r'Unit\s+(\d+)[:\s]+(.+?)[\n\r]',
            r'Lesson\s+(\d+)[:\s]+(.+?)[\n\r]'
        ]
        
        for pattern in chapter_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 2:
                    return f"Chapter {match.group(1)}: {match.group(2).strip()}"
                else:
                    return match.group(1).strip()
        
        return self.current_chapter
    
    def extract_topic(self, text: str) -> str:
        """Extract topic/section from text"""
        topic_patterns = [
            r'(\d+\.\d+)\s+(.+?)[\n\r]',
            r'Topic[:\s]+(.+?)[\n\r]',
            r'Section[:\s]+(.+?)[\n\r]'
        ]
        
        for pattern in topic_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip() if len(match.groups()) == 1 else match.group(2).strip()
        
        return self.current_topic
    
    def classify_content_type(self, text: str) -> str:
        """Classify the type of content"""
        text_lower = text.lower()
        
        # Definition indicators
        definition_keywords = ['definition:', 'is defined as', 'refers to', 'means that', 'is called']
        if any(keyword in text_lower for keyword in definition_keywords):
            return "definition"
        
        # Formula indicators
        formula_symbols = ['=', '+', '×', '÷', '−', '∫', '∑', '√', '²', '³', '∂']
        if any(symbol in text for symbol in formula_symbols):
            return "formula"
        
        # Example indicators
        example_keywords = ['example', 'for instance', 'solve:', 'solution:', 'let us']
        if any(keyword in text_lower for keyword in example_keywords):
            return "example"
        
        # Question indicators
        if '?' in text or text_lower.strip().startswith(('what', 'why', 'how', 'when', 'where')):
            return "question"
        
        # Theorem/Rule
        theorem_keywords = ['theorem', 'rule', 'law', 'principle', 'property']
        if any(keyword in text_lower for keyword in theorem_keywords):
            return "theorem"
        
        return "explanation"
    
    def estimate_difficulty(self, text: str, class_num: int) -> str:
        """Estimate difficulty level based on text complexity"""
        # Simple heuristic: longer sentences and complex words = harder
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # Check for complex mathematical notation
        has_complex_math = bool(re.search(r'[∫∑∂√²³⁴]|\\frac|\\sqrt', text))
        
        # Difficulty scoring
        score = 0
        if avg_word_length > 6:
            score += 1
        if avg_sentence_length > 15:
            score += 1
        if has_complex_math:
            score += 1
        if class_num >= 9:
            score += 1
            
        if score <= 1:
            return "easy"
        elif score <= 2:
            return "medium"
        else:
            return "hard"
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove page numbers
        text = re.sub(r'\b\d{1,3}\b(?=\s*$)', '', text)
        # Remove special characters but keep mathematical symbols
        text = text.strip()
        return text
    
    def parse_pdf(self, pdf_path: str, class_num: int, subject: str) -> List[Dict[str, Any]]:
        """Parse PDF and extract structured content"""
        logger.info(f"Starting to parse: {pdf_path}")
        
        chunks = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                logger.info(f"Total pages: {total_pages}")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    logger.info(f"Processing page {page_num}/{total_pages}")
                    
                    # Extract text
                    text = page.extract_text()
                    
                    if not text or len(text.strip()) < 50:
                        logger.warning(f"Page {page_num} has insufficient text, skipping")
                        continue
                    
                    # Update chapter and topic
                    chapter = self.extract_chapter(text)
                    if chapter != "Unknown":
                        self.current_chapter = chapter
                    
                    topic = self.extract_topic(text)
                    if topic != "General":
                        self.current_topic = topic
                    
                    # Split into paragraphs
                    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
                    
                    for para_idx, paragraph in enumerate(paragraphs):
                        cleaned_text = self.clean_text(paragraph)
                        
                        if len(cleaned_text) < 30:  # Skip very short chunks
                            continue
                        
                        content_type = self.classify_content_type(cleaned_text)
                        difficulty = self.estimate_difficulty(cleaned_text, class_num)
                        
                        chunk = {
                            'content': cleaned_text,
                            'metadata': {
                                'class': class_num,
                                'subject': subject,
                                'chapter': self.current_chapter,
                                'topic': self.current_topic,
                                'page': page_num,
                                'paragraph_index': para_idx,
                                'content_type': content_type,
                                'difficulty': difficulty,
                                'source_file': Path(pdf_path).name
                            }
                        }
                        
                        chunks.append(chunk)
                
                logger.info(f"Successfully extracted {len(chunks)} chunks from {total_pages} pages")
                
        except Exception as e:
            logger.error(f"Error parsing PDF {pdf_path}: {str(e)}")
            raise
        
        return chunks
    
    def parse_multiple_pdfs(self, pdf_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse multiple PDFs with their configurations"""
        all_chunks = []
        
        for config in pdf_configs:
            pdf_path = config['path']
            class_num = config['class']
            subject = config['subject']
            
            logger.info(f"Processing: Class {class_num} - {subject}")
            
            chunks = self.parse_pdf(pdf_path, class_num, subject)
            all_chunks.extend(chunks)
            
            logger.info(f"Total chunks so far: {len(all_chunks)}")
        
        return all_chunks

if __name__ == "__main__":
    # Test the parser
    parser = PDFParser()
    
    # Example usage
    test_config = [
        {
            'path': './uploads/sample_textbook.pdf',
            'class': 8,
            'subject': 'Mathematics'
        }
    ]
    
    try:
        chunks = parser.parse_multiple_pdfs(test_config)
        print(f"\nExtracted {len(chunks)} chunks")
        
        if chunks:
            print("\nSample chunk:")
            print(f"Content: {chunks[0]['content'][:200]}...")
            print(f"Metadata: {chunks[0]['metadata']}")
    except Exception as e:
        print(f"Error: {e}")
