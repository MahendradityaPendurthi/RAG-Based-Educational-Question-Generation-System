#!/usr/bin/env python3
"""
Dynamic example script that automatically detects database content and runs examples
No hardcoded class/subject data - everything is discovered from your database!
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.content_generator import ContentGenerator
from scripts.pdf_parser import PDFParser
from scripts.vector_db import VectorDB
from datetime import datetime
import json

def get_database_info():
    """Dynamically discover what's in the database (ONLY real PDF data)"""
    vector_db = VectorDB()
    stats = vector_db.get_collection_stats()

    if stats['total_chunks'] == 0:
        return None

    # Get sample documents to find topics
    sample = vector_db.collection.get(limit=100)

    # Filter out test/fake data
    real_classes = []
    real_subjects = []
    real_topics = set()

    if sample and sample['metadatas']:
        for meta in sample['metadatas']:
            subject = meta.get('subject', '')
            source_file = meta.get('source_file', '')

            # Skip test data (must have source_file from PDF)
            if not source_file or subject == 'Test' or 'test' in subject.lower():
                continue

            # Collect real data
            class_num = meta.get('class')
            if class_num and class_num not in real_classes:
                real_classes.append(class_num)

            if subject and subject not in real_subjects:
                real_subjects.append(subject)

            topic = meta.get('topic', '')
            if topic and topic not in ['Unknown', 'Test Topic']:
                real_topics.add(topic)

    info = {
        'classes': sorted(real_classes),
        'subjects': real_subjects,
        'total_chunks': len([m for m in sample['metadatas'] if m.get('source_file')]),
        'content_types': stats.get('by_content_type', {}),
        'topics': list(real_topics)[:5]  # Limit to first 5 topics
    }

    return info

def example_1_process_pdf():
    """Example 1: Process a PDF and add to database"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Processing a PDF")
    print("="*70)

    parser = PDFParser()
    vector_db = VectorDB()

    # Look for PDFs in uploads directory
    uploads_dir = Path("./uploads")
    pdf_files = list(uploads_dir.glob("*.pdf"))

    if not pdf_files:
        print("\n❌ No PDF files found in ./uploads/ directory")
        print("   Please add a PDF file to ./uploads/ and try again")
        return

    # Use the first PDF found
    pdf_path = str(pdf_files[0])
    print(f"\nProcessing PDF: {pdf_path}")

    # Ask user for class and subject
    print("\nEnter details for this PDF:")
    try:
        class_num = int(input("Class number (5-10): ").strip())
        subject = input("Subject name: ").strip()
    except:
        print("❌ Invalid input")
        return

    try:
        chunks = parser.parse_pdf(
            pdf_path=pdf_path,
            class_num=class_num,
            subject=subject
        )

        print(f"✅ Extracted {len(chunks)} chunks")

        # Show sample chunk
        if chunks:
            print("\nSample chunk:")
            print(f"Content: {chunks[0]['content'][:150]}...")
            print(f"Type: {chunks[0]['metadata']['content_type']}")
            print(f"Difficulty: {chunks[0]['metadata']['difficulty']}")

        # Add to database
        added = vector_db.add_chunks(chunks)
        print(f"\n✅ Added {added} chunks to vector database")

    except FileNotFoundError:
        print(f"❌ File not found: {pdf_path}")
    except Exception as e:
        print(f"❌ Error: {e}")

def example_2_generate_mcqs():
    """Example 2: Generate MCQ questions using database content"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Generating MCQ Questions")
    print("="*70)

    # Get database info dynamically
    db_info = get_database_info()
    if not db_info:
        print("\n❌ No content in database. Please add some PDFs first (Example 1)")
        return

    print(f"\n📚 Found content in database:")
    print(f"   Classes: {', '.join(str(c) for c in db_info['classes'])}")
    print(f"   Subjects: {', '.join(db_info['subjects'])}")
    print(f"   Topics: {', '.join(db_info['topics'][:3])} (and more)")

    # Use the first class, subject, and topic found
    class_num = int(db_info['classes'][0])
    subject = db_info['subjects'][0]
    topic = db_info['topics'][0] if db_info['topics'] else "General"

    print(f"\n🎯 Generating 5 MCQs for:")
    print(f"   Class {class_num} | {subject} | {topic}")

    try:
        generator = ContentGenerator()

        mcqs = generator.generate_mcq(
            class_num=class_num,
            subject=subject,
            topic=topic,
            difficulty="easy",
            num_questions=5
        )

        print("\n" + "-"*70)
        print(mcqs)
        print("-"*70)

        # Save to file
        output_file = f"./outputs/mcqs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(mcqs)

        print(f"\n✅ Saved to: {output_file}")

    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\n⚠️  To use Gemini API (FREE):")
        print("   1. Get free API key from: https://makersuite.google.com/app/apikey")
        print("   2. Add to .env file: GEMINI_API_KEY=your_key_here")
        print("   3. Make sure LLM_PROVIDER=gemini in .env")
    except Exception as e:
        print(f"❌ Error: {e}")

def example_3_generate_flashcards():
    """Example 3: Generate flashcards using database content"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Generating Flashcards")
    print("="*70)

    # Get database info dynamically
    db_info = get_database_info()
    if not db_info:
        print("\n❌ No content in database. Please add some PDFs first (Example 1)")
        return

    # Use the first class, subject, and topic found
    class_num = int(db_info['classes'][0])
    subject = db_info['subjects'][0]
    topic = db_info['topics'][0] if db_info['topics'] else "General"

    print(f"\n🎯 Generating 10 flashcards for:")
    print(f"   Class {class_num} | {subject} | {topic}")

    try:
        generator = ContentGenerator()

        flashcards = generator.generate_flashcards(
            class_num=class_num,
            subject=subject,
            topic=topic,
            num_cards=10
        )

        print(f"\n✅ Generated {len(flashcards)} flashcards")

        # Display first 3
        print("\nSample flashcards:")
        for i, card in enumerate(flashcards[:3], 1):
            print(f"\n--- Flashcard {i} ---")
            print(f"Front: {card.get('front', 'N/A')}")
            print(f"Back: {card.get('back', 'N/A')}")
            if card.get('hint'):
                print(f"Hint: {card['hint']}")

        # Save to file
        output_file = f"./outputs/flashcards_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(flashcards, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Saved all {len(flashcards)} flashcards to: {output_file}")

    except Exception as e:
        print(f"❌ Error: {e}")

def example_4_generate_notes():
    """Example 4: Generate short notes using database content"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Generating Short Notes")
    print("="*70)

    # Get database info dynamically
    db_info = get_database_info()
    if not db_info:
        print("\n❌ No content in database. Please add some PDFs first (Example 1)")
        return

    # Use the first class and subject found
    class_num = int(db_info['classes'][0])
    subject = db_info['subjects'][0]
    chapter = db_info['topics'][0] if db_info['topics'] else "General"

    print(f"\n🎯 Generating notes for:")
    print(f"   Class {class_num} | {subject} | {chapter}")

    try:
        generator = ContentGenerator()

        notes = generator.generate_short_notes(
            class_num=class_num,
            subject=subject,
            chapter=chapter
        )

        print("\n" + "-"*70)
        print(notes[:500] + "...")  # Show first 500 chars
        print("-"*70)

        # Save to file
        output_file = f"./outputs/notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(notes)

        print(f"\n✅ Saved complete notes to: {output_file}")

    except Exception as e:
        print(f"❌ Error: {e}")

def example_5_generate_worksheet():
    """Example 5: Generate a complete worksheet using database content"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Generating Complete Worksheet")
    print("="*70)

    # Get database info dynamically
    db_info = get_database_info()
    if not db_info:
        print("\n❌ No content in database. Please add some PDFs first (Example 1)")
        return

    # Use the first class and subject found
    class_num = int(db_info['classes'][0])
    subject = db_info['subjects'][0]
    topics = db_info['topics'][:2] if len(db_info['topics']) >= 2 else db_info['topics']

    if not topics:
        topics = ["General"]

    print(f"\n🎯 Generating worksheet for:")
    print(f"   Class {class_num} | {subject}")
    print(f"   Topics: {', '.join(topics)}")

    try:
        generator = ContentGenerator()

        worksheet = generator.generate_worksheet(
            class_num=class_num,
            subject=subject,
            topics=topics,
            difficulty="easy",
            num_questions=10
        )

        print("\n" + "-"*70)
        print(worksheet[:800] + "...")  # Show beginning
        print("-"*70)

        # Save to file
        output_file = f"./outputs/worksheet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(worksheet)

        print(f"\n✅ Saved complete worksheet to: {output_file}")

    except Exception as e:
        print(f"❌ Error: {e}")

def example_6_search_content():
    """Example 6: Search for content in database"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Searching Vector Database")
    print("="*70)

    # Get database info dynamically
    db_info = get_database_info()
    if not db_info:
        print("\n❌ No content in database. Please add some PDFs first (Example 1)")
        return

    vector_db = VectorDB()

    # Use first class and subject for filtering
    class_num = int(db_info['classes'][0])
    subject = db_info['subjects'][0]

    # Suggest a query based on topics
    suggested_query = f"What is {db_info['topics'][0]}?" if db_info['topics'] else "Explain the concept"

    print(f"\n🔍 Searching in: Class {class_num} {subject}")
    print(f"   Suggested query: {suggested_query}")
    query = input("\nEnter your search query (or press Enter for suggestion): ").strip()

    if not query:
        query = suggested_query

    print(f"\nSearching for: '{query}'")

    results = vector_db.search(
        query=query,
        filters={'class': class_num, 'subject': subject},
        n_results=5
    )

    print(f"\n✅ Found {len(results['documents'][0])} results")

    # Display results
    for i, doc in enumerate(results['documents'][0][:3], 1):
        print(f"\n--- Result {i} ---")
        print(f"Content: {doc[:200]}...")
        print(f"Metadata: {results['metadatas'][0][i-1]}")

def example_7_database_stats():
    """Example 7: Get database statistics"""
    print("\n" + "="*70)
    print("EXAMPLE 7: Database Statistics")
    print("="*70)

    vector_db = VectorDB()
    stats = vector_db.get_collection_stats()

    if stats['total_chunks'] == 0:
        print("\n❌ Database is empty. Please add some PDFs first (Example 1)")
        return

    print("\n📊 Current Database Statistics:")
    print(json.dumps(stats, indent=2))

    # Show helpful summary
    print(f"\n📚 Summary:")
    print(f"   Total Content Chunks: {stats['total_chunks']}")
    print(f"   Classes: {', '.join(str(k) for k in stats.get('by_class', {}).keys())}")
    print(f"   Subjects: {', '.join(stats.get('by_subject', {}).keys())}")
    print(f"   Content Types: {', '.join(stats.get('by_content_type', {}).keys())}")

def example_8_export_all_data():
    """Example 8: Export all parsed data to JSON and CSV"""
    print("\n" + "="*70)
    print("EXAMPLE 8: Export All Data")
    print("="*70)

    print("\n📤 This will export ALL parsed chunks from your database")
    print("   to both JSON and CSV formats for complete verification.")

    try:
        # Import and run the export script
        from scripts import export_data
        export_data.export_all_data()

        print("\n💡 Tip: Open the CSV file in Excel to easily browse all your data!")

    except Exception as e:
        print(f"\n❌ Error during export: {e}")

def main():
    """Run examples with dynamic content detection"""
    print("\n" + "="*70)
    print("EDUCATION RAG SYSTEM - DYNAMIC EXAMPLES")
    print("="*70)
    print("\n🎯 This system automatically detects your database content!")
    print("   No hardcoded data - everything is based on YOUR PDFs")

    # Check if database has content
    db_info = get_database_info()

    if db_info and db_info['total_chunks'] > 0:
        print(f"\n✅ Database Status: {db_info['total_chunks']} chunks found")
        print(f"   Classes: {', '.join(str(c) for c in db_info['classes'])}")
        print(f"   Subjects: {', '.join(db_info['subjects'])}")
    else:
        print("\n⚠️  Database is empty. Start with Example 1 to add PDFs!")

    examples = [
        ("Process PDF & Add to Database", example_1_process_pdf),
        ("Generate MCQs (from YOUR data)", example_2_generate_mcqs),
        ("Generate Flashcards (from YOUR data)", example_3_generate_flashcards),
        ("Generate Notes (from YOUR data)", example_4_generate_notes),
        ("Generate Worksheet (from YOUR data)", example_5_generate_worksheet),
        ("Search Content", example_6_search_content),
        ("Database Stats", example_7_database_stats),
        ("Export All Data (JSON + CSV)", example_8_export_all_data)
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    print("0. Run all examples")

    choice = input("\nEnter example number (0-8): ").strip()

    if choice == "0":
        # Run all examples
        for name, func in examples:
            try:
                func()
            except Exception as e:
                print(f"\n❌ Error in {name}: {e}")
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        # Run selected example
        idx = int(choice) - 1
        name, func = examples[idx]
        try:
            func()
        except Exception as e:
            print(f"\n❌ Error: {e}")
    else:
        print("Invalid choice")

    print("\n" + "="*70)
    print("Examples complete!")
    print("="*70)

if __name__ == "__main__":
    main()
