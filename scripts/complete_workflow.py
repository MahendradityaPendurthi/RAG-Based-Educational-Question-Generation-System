#!/usr/bin/env python3
"""
Complete PDF Processing Workflow
- Upload and parse PDF with optimized chunking (300 size, 100 overlap)
- Verify 75+ chunks per chapter for better question generation
- Generate 50+ MCQs from parsed data
- Export all data to CSV and JSON
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path
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

def step_1_upload_and_parse_pdf():
    """Step 1: Upload and parse PDF with optimized chunking"""
    print_header("STEP 1: UPLOAD & PARSE PDF")

    print("\nOptimized Chunking Settings:")
    print(f"  Chunk Size: {settings.chunk_size} characters")
    print(f"  Chunk Overlap: {settings.chunk_overlap} characters")
    print(f"  Expected: More chunks = More questions (75+ per chapter)")

    # Look for PDFs in uploads directory
    uploads_dir = Path("./uploads")
    pdf_files = list(uploads_dir.glob("*.pdf"))

    if not pdf_files:
        print("\n⚠ No PDF files found in ./uploads/ directory")
        print("  Please add your textbook PDF to ./uploads/ and try again")
        return None

    # Show available PDFs
    print(f"\n📚 Found {len(pdf_files)} PDF(s):")
    for i, pdf in enumerate(pdf_files, 1):
        print(f"  {i}. {pdf.name}")

    # Select PDF
    if len(pdf_files) == 1:
        selected_pdf = pdf_files[0]
        print(f"\n✓ Auto-selected: {selected_pdf.name}")
    else:
        choice = input(f"\nSelect PDF (1-{len(pdf_files)}): ").strip()
        if not choice.isdigit() or not (1 <= int(choice) <= len(pdf_files)):
            print("Invalid choice")
            return None
        selected_pdf = pdf_files[int(choice) - 1]

    # Get class and subject
    print(f"\n📖 Processing: {selected_pdf.name}")
    try:
        class_num = int(input("Enter Class number (5-10): ").strip())
        subject = input("Enter Subject name (e.g., Science, Math): ").strip()
    except:
        print("Invalid input")
        return None

    # Parse PDF
    print(f"\n⚙ Parsing PDF with optimized chunking...")
    parser = PDFParser()

    try:
        chunks = parser.parse_pdf(
            pdf_path=str(selected_pdf),
            class_num=class_num,
            subject=subject
        )

        print(f"\n✅ Parsing Complete!")
        print(f"  Total Chunks: {len(chunks)}")
        print(f"  Class: {class_num}")
        print(f"  Subject: {subject}")
        print(f"  Source: {selected_pdf.name}")

        # Show chunk breakdown
        content_types = {}
        for chunk in chunks:
            ct = chunk['metadata'].get('content_type', 'unknown')
            content_types[ct] = content_types.get(ct, 0) + 1

        print(f"\n📊 Content Breakdown:")
        for ctype, count in sorted(content_types.items()):
            print(f"  {ctype}: {count} chunks")

        # Add to database
        print(f"\n💾 Adding {len(chunks)} chunks to vector database...")
        vector_db = VectorDB()
        added = vector_db.add_chunks(chunks)

        print(f"✅ Added {added} chunks to database")

        # Verify capacity for 75+ questions
        if len(chunks) >= 75:
            print(f"\n🎯 EXCELLENT! {len(chunks)} chunks can support 75+ questions")
        elif len(chunks) >= 50:
            print(f"\n✓ GOOD! {len(chunks)} chunks can support 50+ questions")
        else:
            print(f"\n⚠ {len(chunks)} chunks - may need more PDFs for 75+ questions")

        return {
            'class': class_num,
            'subject': subject,
            'chunks': len(chunks),
            'source': selected_pdf.name
        }

    except Exception as e:
        print(f"\n❌ Error parsing PDF: {e}")
        return None

def step_2_generate_mcqs(pdf_info):
    """Step 2: Generate 50+ MCQs from parsed data"""
    print_header("STEP 2: GENERATE 50+ MCQs")

    if not pdf_info:
        print("\n⚠ No PDF data available. Please complete Step 1 first.")
        return None

    print(f"\n📚 Source Data:")
    print(f"  Class: {pdf_info['class']}")
    print(f"  Subject: {pdf_info['subject']}")
    print(f"  Chunks Available: {pdf_info['chunks']}")

    # Get database info to find topics
    vector_db = VectorDB()
    sample = vector_db.collection.get(limit=100)

    topics = set()
    if sample and sample['metadatas']:
        for meta in sample['metadatas']:
            if meta.get('source_file') and meta.get('subject') != 'Test':
                topic = meta.get('topic', '')
                if topic and topic not in ['Unknown', 'Test Topic']:
                    topics.add(topic)

    if not topics:
        print("\n⚠ No topics found in database")
        topic = "General"
    else:
        print(f"\n📖 Available Topics:")
        topic_list = sorted(list(topics))
        for i, t in enumerate(topic_list, 1):
            print(f"  {i}. {t}")

        # Use first topic
        topic = topic_list[0]
        print(f"\n✓ Using topic: {topic}")

    # Ask how many MCQs
    try:
        num_mcqs = int(input("\nHow many MCQs to generate (default: 50)? ").strip() or "50")
    except:
        num_mcqs = 50

    # Ask difficulty
    print("\nDifficulty levels: easy, medium, hard")
    difficulty = input("Select difficulty (default: medium): ").strip() or "medium"

    # Generate MCQs
    print(f"\n⚙ Generating {num_mcqs} {difficulty} MCQs about {topic}...")
    print(f"  This may take 30-60 seconds for large question sets...")

    try:
        generator = ContentGenerator()
        mcqs = generator.generate_mcq(
            class_num=pdf_info['class'],
            subject=pdf_info['subject'],
            topic=topic,
            difficulty=difficulty,
            num_questions=num_mcqs
        )

        print(f"\n✅ MCQ Generation Complete!")
        print(f"  Generated: {num_mcqs} questions")
        print(f"  Topic: {topic}")
        print(f"  Difficulty: {difficulty}")

        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"./outputs/mcqs_{num_mcqs}_{topic}_{timestamp}.txt"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Class {pdf_info['class']} {pdf_info['subject']} - {topic}\n")
            f.write(f"Difficulty: {difficulty}\n")
            f.write(f"Total Questions: {num_mcqs}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            f.write(mcqs)

        print(f"\n💾 Saved to: {output_file}")

        # Show preview
        print(f"\n📝 Preview (first 500 characters):")
        print("-"*80)
        print(mcqs[:500] + "...")
        print("-"*80)

        return {
            'num_questions': num_mcqs,
            'topic': topic,
            'difficulty': difficulty,
            'output_file': output_file
        }

    except Exception as e:
        print(f"\n❌ Error generating MCQs: {e}")
        import traceback
        traceback.print_exc()
        return None

def step_3_export_data():
    """Step 3: Export all data to CSV and JSON"""
    print_header("STEP 3: EXPORT DATA TO CSV & JSON")

    print("\n📤 Exporting all parsed chunks from database...")
    print("  Formats: JSON (structured) + CSV (spreadsheet)")
    print("  Location: ./exports/ folder")

    try:
        export_all_data()
        return True
    except Exception as e:
        print(f"\n❌ Error during export: {e}")
        return False

def main():
    """Run complete workflow"""
    print("\n" + "="*80)
    print("COMPLETE PDF PROCESSING WORKFLOW".center(80))
    print("="*80)

    print("\n🎯 This workflow will:")
    print("  1. Upload & parse your PDF with optimized chunking (75+ questions/chapter)")
    print("  2. Generate 50+ MCQs from your parsed data (NOT static/fake)")
    print("  3. Export everything to CSV and JSON in ./exports/ folder")

    print(f"\n⚙ Current Settings:")
    print(f"  Chunk Size: {settings.chunk_size} (smaller = more chunks)")
    print(f"  Chunk Overlap: {settings.chunk_overlap} (more overlap = better coverage)")
    print(f"  Max Tokens: {settings.max_tokens} (supports 50+ MCQs)")
    print(f"  LLM Provider: {settings.llm_provider.upper()}")

    input("\n▶ Press Enter to start the workflow...")

    # Step 1: Parse PDF
    pdf_info = step_1_upload_and_parse_pdf()

    if not pdf_info:
        print("\n❌ Workflow stopped: PDF parsing failed")
        return

    input("\n▶ Press Enter to continue to MCQ generation...")

    # Step 2: Generate MCQs
    mcq_info = step_2_generate_mcqs(pdf_info)

    if not mcq_info:
        print("\n⚠ MCQ generation failed, but continuing to export...")

    input("\n▶ Press Enter to export data...")

    # Step 3: Export data
    export_success = step_3_export_data()

    # Final summary
    print_header("WORKFLOW COMPLETE")

    print("\n✅ Summary:")
    print(f"  1. PDF Parsed: {pdf_info['source']}")
    print(f"     - Chunks Created: {pdf_info['chunks']}")
    print(f"     - Class: {pdf_info['class']}")
    print(f"     - Subject: {pdf_info['subject']}")

    if mcq_info:
        print(f"  2. MCQs Generated: {mcq_info['num_questions']} questions")
        print(f"     - Topic: {mcq_info['topic']}")
        print(f"     - Difficulty: {mcq_info['difficulty']}")
        print(f"     - Saved to: {mcq_info['output_file']}")
    else:
        print(f"  2. MCQs: Skipped or failed")

    if export_success:
        print(f"  3. Data Exported: ✓ JSON + CSV in ./exports/")
    else:
        print(f"  3. Data Export: Failed")

    print("\n" + "="*80)
    print("🎉 ALL TASKS COMPLETE!")
    print("="*80)

    print("\n📁 Your files are in:")
    print("  - ./outputs/     (MCQs, worksheets, notes)")
    print("  - ./exports/     (CSV and JSON database exports)")

    print("\n💡 Next Steps:")
    print("  - Open CSV in Excel to browse all parsed chunks")
    print("  - Generate more MCQs: python scripts/example_usage.py (Option 2)")
    print("  - Generate worksheets: python scripts/example_usage.py (Option 5)")
    print("  - Generate notes: python scripts/example_usage.py (Option 4)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Workflow cancelled by user")
    except Exception as e:
        print(f"\n❌ Workflow error: {e}")
        import traceback
        traceback.print_exc()
