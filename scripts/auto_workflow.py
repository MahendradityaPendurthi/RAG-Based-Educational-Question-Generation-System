#!/usr/bin/env python3
"""
Automated PDF Processing & Question Generation Workflow
- Automatically parses PDF with optimized chunking
- Generates all 5 question types (40 MCQs, 20 fill blanks, 20 short, 20 long, 20 very short)
- Exports everything to CSV & JSON
- No unnecessary prompts
"""

import sys
from pathlib import Path
from datetime import datetime
import re

sys.path.append(str(Path(__file__).parent.parent))

from scripts.pdf_parser import PDFParser
from scripts.vector_db import VectorDB
from scripts.content_generator import ContentGenerator
from scripts.export_data import export_all_data
from config.config import settings

def print_header(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(title.center(80))
    print("="*80)

def sanitize_filename(name):
    """Sanitize a string for use in filenames"""
    # Remove invalid characters for Windows/Unix filenames
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '')
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    # Remove multiple underscores
    while '__' in name:
        name = name.replace('__', '_')
    # Remove leading/trailing underscores
    name = name.strip('_')
    return name

def extract_class_subject_from_pdf(pdf_path):
    """Try to extract class and subject from PDF filename"""
    filename = Path(pdf_path).stem.lower()

    # Try to extract class number
    class_match = re.search(r'(\d{1,2})(th|st|nd|rd)?', filename)
    class_num = int(class_match.group(1)) if class_match else 6

    # Try to extract subject
    subjects = {
        'sci': 'Science',
        'science': 'Science',
        'math': 'Mathematics',
        'maths': 'Mathematics',
        'eng': 'English',
        'english': 'English',
        'sst': 'Social Studies',
        'social': 'Social Studies',
        'hindi': 'Hindi',
        'phy': 'Physics',
        'physics': 'Physics',
        'chem': 'Chemistry',
        'chemistry': 'Chemistry',
        'bio': 'Biology',
        'biology': 'Biology'
    }

    subject = "General"
    for key, value in subjects.items():
        if key in filename:
            subject = value
            break

    return class_num, subject

def process_pdf():
    """Step 1: Upload and parse PDF automatically"""
    print_header("STEP 1: UPLOAD & PARSE PDF")

    print(f"\nOptimized Settings:")
    print(f"  Chunk Size: {settings.chunk_size} (maximum chunks for maximum questions)")
    print(f"  Chunk Overlap: {settings.chunk_overlap} (better coverage)")
    print(f"  Max Tokens: {settings.max_tokens} (supports 50+ questions per type)")

    # Look for PDFs in uploads directory
    uploads_dir = Path("./uploads")
    pdf_files = list(uploads_dir.glob("*.pdf"))

    if not pdf_files:
        print("\nNo PDF files found in ./uploads/ directory")
        print("Please add your textbook PDF to ./uploads/ and try again")
        return None

    # Show available PDFs
    print(f"\nFound {len(pdf_files)} PDF(s):")
    for i, pdf in enumerate(pdf_files, 1):
        print(f"  {i}. {pdf.name}")

    # Select PDF
    if len(pdf_files) == 1:
        selected_pdf = pdf_files[0]
        print(f"\nAuto-selected: {selected_pdf.name}")
    else:
        choice = input(f"\nSelect PDF (1-{len(pdf_files)}): ").strip()
        if not choice.isdigit() or not (1 <= int(choice) <= len(pdf_files)):
            print("Invalid choice")
            return None
        selected_pdf = pdf_files[int(choice) - 1]

    # Auto-detect class and subject from filename
    class_num, subject = extract_class_subject_from_pdf(selected_pdf)

    print(f"\nAuto-detected:")
    print(f"  Class: {class_num}")
    print(f"  Subject: {subject}")

    confirm = input("Is this correct? (yes/no, or enter correct class and subject): ").strip().lower()
    if confirm != 'yes' and confirm != 'y':
        try:
            class_num = int(input("Enter Class number (5-10): ").strip())
            subject = input("Enter Subject name: ").strip()
        except:
            print("Invalid input")
            return None

    # Parse PDF
    print(f"\nParsing PDF with optimized chunking...")
    parser = PDFParser()

    try:
        chunks = parser.parse_pdf(
            pdf_path=str(selected_pdf),
            class_num=class_num,
            subject=subject
        )

        print(f"\nParsing Complete!")
        print(f"  Total Chunks: {len(chunks)}")
        print(f"  Class: {class_num}")
        print(f"  Subject: {subject}")
        print(f"  Source: {selected_pdf.name}")

        # Add to database
        print(f"\nAdding {len(chunks)} chunks to vector database...")
        vector_db = VectorDB()
        added = vector_db.add_chunks(chunks)

        print(f"Added {added} chunks to database")

        # Extract topics from chunks
        topics = set()
        for chunk in chunks:
            topic = chunk['metadata'].get('topic', '')
            if topic and topic not in ['Unknown', 'General']:
                topics.add(topic)

        return {
            'class': class_num,
            'subject': subject,
            'chunks': len(chunks),
            'source': selected_pdf.name,
            'topics': list(topics)
        }

    except Exception as e:
        print(f"\nError parsing PDF: {e}")
        return None

def generate_all_questions(pdf_info):
    """Step 2: Generate all 5 question types automatically"""
    print_header("STEP 2: GENERATE ALL QUESTION TYPES")

    if not pdf_info:
        print("\nNo PDF data available. Please complete Step 1 first.")
        return None

    print(f"\nSource Data:")
    print(f"  Class: {pdf_info['class']}")
    print(f"  Subject: {pdf_info['subject']}")
    print(f"  Chunks: {pdf_info['chunks']}")
    print(f"  Topics: {', '.join(pdf_info['topics'][:3]) if pdf_info['topics'] else 'General'}")

    # Use first available topic or 'General'
    topic = pdf_info['topics'][0] if pdf_info['topics'] else 'General'
    print(f"\nUsing topic: {topic}")

    # Sanitize topic name for use in filenames
    safe_topic = sanitize_filename(topic)

    try:
        generator = ContentGenerator()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path("./outputs")
        output_dir.mkdir(exist_ok=True)

        results = {}

        # Question type configurations: (display_name, method, total_count, easy, medium, hard)
        question_types = [
            ("MCQs", generator.generate_mcq, 40, 14, 13, 13),
            ("Fill in the Blanks", generator.generate_fill_blanks, 20, 7, 7, 6),
            ("Short Answer", generator.generate_short_answer_questions, 20, 7, 7, 6),
            ("Long Answer", generator.generate_long_answer_questions, 20, 7, 7, 6),
            ("Very Short Answer", generator.generate_very_short_answer_questions, 20, 7, 7, 6),
        ]

        step = 1
        for q_name, q_method, total, easy_count, medium_count, hard_count in question_types:
            print(f"\n[{step}/5] Generating {total} {q_name} (Easy: {easy_count}, Medium: {medium_count}, Hard: {hard_count})...")

            all_questions = []

            # Generate for each difficulty level
            for difficulty, count in [("easy", easy_count), ("medium", medium_count), ("hard", hard_count)]:
                print(f"    Generating {count} {difficulty} questions...")

                # All methods now support difficulty parameter
                questions = q_method(
                    class_num=pdf_info['class'],
                    subject=pdf_info['subject'],
                    topic=topic,
                    difficulty=difficulty,
                    num_questions=count
                )

                # Add section header and questions
                all_questions.append(f"\n{'='*80}")
                all_questions.append(f"{difficulty.upper()} LEVEL ({count} questions)")
                all_questions.append(f"{'='*80}\n")
                all_questions.append(questions)

            # Save all questions to file
            filename_key = q_name.lower().replace(" ", "_")
            output_file = output_dir / f"{filename_key}_{total}_{safe_topic}_{timestamp}.txt"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Class {pdf_info['class']} {pdf_info['subject']} - {topic}\n")
                f.write(f"{total} {q_name}\n")
                f.write("="*80 + "\n")
                f.write("\n".join(all_questions))

            print(f"    Saved: {output_file.name}")
            results[filename_key] = output_file
            step += 1

        print(f"\nAll questions generated successfully!")
        return results

    except Exception as e:
        print(f"\nError generating questions: {e}")
        import traceback
        traceback.print_exc()
        return None

def export_data():
    """Step 3: Export all data to CSV and JSON"""
    print_header("STEP 3: EXPORT DATA TO CSV & JSON")

    print("\nExporting all parsed chunks from database...")
    try:
        export_all_data()
        return True
    except Exception as e:
        print(f"\nError during export: {e}")
        return False

def main():
    """Run automated workflow"""
    print("\n" + "="*80)
    print("AUTOMATED PDF PROCESSING & QUESTION GENERATION".center(80))
    print("="*80)

    print("\nThis workflow will:")
    print("  1. Parse your PDF with optimized chunking (300 size, 100 overlap)")
    print("  2. Generate ALL question types:")
    print("     - 40 Multiple Choice Questions (MCQs)")
    print("     - 20 Fill in the Blanks")
    print("     - 20 Short Answer Questions")
    print("     - 20 Long Answer Questions")
    print("     - 20 Very Short Answer Questions")
    print("  3. Export everything to CSV and JSON in ./exports/")

    print(f"\nCurrent Settings:")
    print(f"  Chunk Size: {settings.chunk_size}")
    print(f"  Chunk Overlap: {settings.chunk_overlap}")
    print(f"  Max Tokens: {settings.max_tokens}")
    print(f"  LLM Provider: {settings.llm_provider.upper()}")

    input("\nPress Enter to start...")

    # Step 1: Parse PDF
    pdf_info = process_pdf()

    if not pdf_info:
        print("\nWorkflow stopped: PDF parsing failed")
        return

    input("\nPress Enter to generate questions...")

    # Step 2: Generate all questions
    question_results = generate_all_questions(pdf_info)

    if not question_results:
        print("\nWarning: Question generation failed")

    input("\nPress Enter to export data...")

    # Step 3: Export data
    export_success = export_data()

    # Final summary
    print_header("WORKFLOW COMPLETE")

    print("\nSummary:")
    print(f"  1. PDF Parsed: {pdf_info['source']}")
    print(f"     - Chunks Created: {pdf_info['chunks']}")
    print(f"     - Class: {pdf_info['class']}")
    print(f"     - Subject: {pdf_info['subject']}")

    if question_results:
        print(f"\n  2. Questions Generated:")
        print(f"     - 40 MCQs: {question_results['mcqs'].name}")
        print(f"     - 20 Fill Blanks: {question_results['fill_blanks'].name}")
        print(f"     - 20 Short Answer: {question_results['short_answer'].name}")
        print(f"     - 20 Long Answer: {question_results['long_answer'].name}")
        print(f"     - 20 Very Short: {question_results['very_short_answer'].name}")
    else:
        print(f"\n  2. Questions: Generation failed or skipped")

    if export_success:
        print(f"\n  3. Data Exported: JSON + CSV in ./exports/")
    else:
        print(f"\n  3. Data Export: Failed")

    print("\n" + "="*80)
    print("ALL TASKS COMPLETE!")
    print("="*80)

    print("\nYour files are in:")
    print("  - ./outputs/     (All question files)")
    print("  - ./exports/     (CSV and JSON database exports)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nWorkflow cancelled by user")
    except Exception as e:
        print(f"\nWorkflow error: {e}")
        import traceback
        traceback.print_exc()
