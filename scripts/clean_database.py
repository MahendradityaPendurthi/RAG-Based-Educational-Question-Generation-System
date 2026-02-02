#!/usr/bin/env python3
"""
Clean database by removing test/fake data
Keep only real PDF content
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.vector_db import VectorDB
from config.config import settings

def clean_database():
    """Remove all test/fake data from database"""
    print("\n" + "="*70)
    print("DATABASE CLEANUP - REMOVING TEST/FAKE DATA")
    print("="*70)

    # Initialize database
    print("\n🔍 Connecting to vector database...")
    vector_db = VectorDB()

    # Get all data
    stats = vector_db.get_collection_stats()
    total_before = stats.get('total_chunks', 0)

    print(f"\n📊 Current Database:")
    print(f"   Total Chunks: {total_before}")
    print(f"   Classes: {', '.join(str(k) for k in stats.get('by_class', {}).keys())}")
    print(f"   Subjects: {', '.join(stats.get('by_subject', {}).keys())}")

    # Get all chunks
    all_data = vector_db.collection.get(
        include=['documents', 'metadatas']
    )

    # Identify test/fake data
    test_ids = []
    real_ids = []

    for i, metadata in enumerate(all_data['metadatas']):
        chunk_id = all_data['ids'][i]
        subject = metadata.get('subject', '')
        source_file = metadata.get('source_file', '')

        # Identify test data
        if subject == 'Test' or 'test' in subject.lower() or not source_file:
            test_ids.append(chunk_id)
            print(f"\n❌ Found test data: {chunk_id}")
            print(f"   Subject: {subject}")
            print(f"   Metadata: {metadata}")
        else:
            real_ids.append(chunk_id)

    if not test_ids:
        print("\n✅ No test data found! Database is clean.")
        return

    print(f"\n⚠️  Found {len(test_ids)} test/fake chunks to remove")
    print(f"✅ Keeping {len(real_ids)} real PDF chunks")

    # Ask for confirmation
    print("\n" + "="*70)
    print("CONFIRMATION")
    print("="*70)
    print(f"\nThis will DELETE {len(test_ids)} test chunks and keep {len(real_ids)} real chunks.")
    print("Test chunks to be removed:")
    for test_id in test_ids:
        print(f"  - {test_id}")

    response = input("\nProceed with cleanup? (yes/no): ").strip().lower()

    if response != 'yes':
        print("\n❌ Cleanup cancelled")
        return

    # Delete test chunks
    print(f"\n🗑️  Deleting {len(test_ids)} test chunks...")
    try:
        vector_db.collection.delete(ids=test_ids)
        print(f"✅ Deleted {len(test_ids)} test chunks")
    except Exception as e:
        print(f"❌ Error deleting chunks: {e}")
        return

    # Verify cleanup
    stats_after = vector_db.get_collection_stats()
    total_after = stats_after.get('total_chunks', 0)

    print("\n" + "="*70)
    print("CLEANUP COMPLETE")
    print("="*70)

    print(f"\n📊 Database Status:")
    print(f"   Before: {total_before} chunks")
    print(f"   After:  {total_after} chunks")
    print(f"   Removed: {total_before - total_after} chunks")

    print(f"\n✅ Clean Database:")
    print(f"   Total Chunks: {total_after}")
    print(f"   Classes: {', '.join(str(k) for k in stats_after.get('by_class', {}).keys())}")
    print(f"   Subjects: {', '.join(stats_after.get('by_subject', {}).keys())}")
    print(f"   Content Types: {', '.join(stats_after.get('by_content_type', {}).keys())}")

    print("\n🎉 Database now contains ONLY real PDF data!")
    print("   No more test/fake content.")

def main():
    """Main function"""
    try:
        clean_database()
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
