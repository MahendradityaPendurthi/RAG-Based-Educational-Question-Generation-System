#!/usr/bin/env python3
"""
Force clean database - Remove ALL non-PDF data automatically
No confirmation needed
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from scripts.vector_db import VectorDB

def force_clean():
    """Remove all test/fake data without confirmation"""
    print("\n🧹 FORCE CLEANING DATABASE...")

    vector_db = VectorDB()

    # Get all data
    all_data = vector_db.collection.get(include=['metadatas'])

    # Find test data
    test_ids = []
    for i, metadata in enumerate(all_data['metadatas']):
        chunk_id = all_data['ids'][i]
        subject = metadata.get('subject', '')
        source_file = metadata.get('source_file', '')
        class_num = metadata.get('class')

        # Remove if:
        # - No source file (not from PDF)
        # - Subject is "Test"
        # - Class is 8 (example data)
        if not source_file or subject == 'Test' or 'test' in subject.lower() or class_num == 8:
            test_ids.append(chunk_id)
            print(f"❌ Removing: {chunk_id} (class={class_num}, subject={subject})")

    if test_ids:
        print(f"\n🗑️  Deleting {len(test_ids)} test chunks...")
        vector_db.collection.delete(ids=test_ids)
        print(f"✅ Deleted {len(test_ids)} chunks")
    else:
        print("\n✅ Database is clean!")

    # Verify
    stats = vector_db.get_collection_stats()
    print(f"\n📊 Clean Database:")
    print(f"   Total: {stats['total_chunks']}")
    print(f"   Classes: {list(stats.get('by_class', {}).keys())}")
    print(f"   Subjects: {list(stats.get('by_subject', {}).keys())}")

    if 8 in stats.get('by_class', {}) or 'Test' in stats.get('by_subject', {}):
        print("\n⚠️  WARNING: Still found Class 8 or Test data!")
        print("   Running cleanup again...")
        force_clean()  # Recursive clean
    else:
        print("\n🎉 Database clean! Only PDF data remains.")

if __name__ == "__main__":
    force_clean()
