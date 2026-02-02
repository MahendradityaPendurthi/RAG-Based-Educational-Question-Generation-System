#!/usr/bin/env python3
"""
Export all parsed chunks from the vector database to JSON and CSV formats
This allows you to verify that all your PDF content has been properly analyzed
"""

import sys
from pathlib import Path
import json
import csv
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.vector_db import VectorDB
from config.config import settings

def export_to_json(chunks_data, output_file):
    """Export all chunks to JSON format"""
    print(f"\n📄 Exporting to JSON: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunks_data, f, indent=2, ensure_ascii=False)

    print(f"✅ JSON export complete: {output_file}")
    return output_file

def export_to_csv(chunks_data, output_file):
    """Export all chunks to CSV format"""
    print(f"\n📊 Exporting to CSV: {output_file}")

    if not chunks_data['chunks']:
        print("❌ No data to export")
        return None

    # Get all unique metadata keys
    all_keys = set()
    for chunk in chunks_data['chunks']:
        all_keys.update(chunk['metadata'].keys())

    # Create CSV with all fields
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        # Define field names
        fieldnames = ['chunk_id', 'content', 'content_length'] + sorted(list(all_keys))
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        # Write header
        writer.writeheader()

        # Write rows
        for chunk in chunks_data['chunks']:
            row = {
                'chunk_id': chunk['id'],
                'content': chunk['content'],
                'content_length': len(chunk['content'])
            }
            # Add all metadata fields
            for key in all_keys:
                row[key] = chunk['metadata'].get(key, '')

            writer.writerow(row)

    print(f"✅ CSV export complete: {output_file}")
    return output_file

def export_all_data():
    """Export all data from the vector database"""
    print("\n" + "="*70)
    print("EXPORT ALL PARSED DATA FROM DATABASE")
    print("="*70)

    # Initialize database
    print("\n🔍 Connecting to vector database...")
    vector_db = VectorDB()

    # Get statistics
    stats = vector_db.get_collection_stats()
    total_chunks = stats.get('total_chunks', 0)

    if total_chunks == 0:
        print("\n❌ No data in database!")
        print("   Please add some PDFs first using Example 1")
        return

    print(f"\n📊 Database Statistics:")
    print(f"   Total Chunks: {total_chunks}")
    print(f"   Classes: {', '.join(str(k) for k in stats.get('by_class', {}).keys())}")
    print(f"   Subjects: {', '.join(stats.get('by_subject', {}).keys())}")
    print(f"   Content Types: {', '.join(stats.get('by_content_type', {}).keys())}")

    # Retrieve ALL chunks
    print(f"\n📥 Retrieving all {total_chunks} chunks...")
    all_data = vector_db.collection.get(
        limit=total_chunks,
        include=['documents', 'metadatas', 'embeddings']
    )

    # Organize data
    chunks_data = {
        'export_info': {
            'timestamp': datetime.now().isoformat(),
            'total_chunks': total_chunks,
            'database_path': settings.vector_db_path,
            'collection_name': settings.collection_name,
            'statistics': stats
        },
        'chunks': []
    }

    # Process each chunk
    for i in range(len(all_data['ids'])):
        chunk = {
            'id': all_data['ids'][i],
            'content': all_data['documents'][i],
            'metadata': all_data['metadatas'][i],
            'has_embedding': all_data['embeddings'][i] is not None if 'embeddings' in all_data else False
        }
        chunks_data['chunks'].append(chunk)

    print(f"✅ Retrieved {len(chunks_data['chunks'])} chunks")

    # Create output directory
    output_dir = Path("./exports")
    output_dir.mkdir(exist_ok=True)

    # Generate filenames with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_file = output_dir / f"database_export_{timestamp}.json"
    csv_file = output_dir / f"database_export_{timestamp}.csv"

    # Export to both formats
    json_path = export_to_json(chunks_data, json_file)
    csv_path = export_to_csv(chunks_data, csv_file)

    # Show summary
    print("\n" + "="*70)
    print("EXPORT SUMMARY")
    print("="*70)

    print(f"\n📊 Data Overview:")
    print(f"   Total Chunks Exported: {len(chunks_data['chunks'])}")
    print(f"   Export Timestamp: {chunks_data['export_info']['timestamp']}")

    print(f"\n📁 Output Files:")
    print(f"   JSON: {json_path}")
    print(f"   CSV:  {csv_path}")

    # Content breakdown
    print(f"\n📚 Content Breakdown:")
    for content_type, count in stats.get('by_content_type', {}).items():
        print(f"   {content_type}: {count} chunks")

    # Sample data
    if chunks_data['chunks']:
        print(f"\n📝 Sample Data (first chunk):")
        sample = chunks_data['chunks'][0]
        print(f"   ID: {sample['id']}")
        print(f"   Content Length: {len(sample['content'])} characters")
        print(f"   Content Preview: {sample['content'][:150]}...")
        print(f"   Metadata: {sample['metadata']}")

    print("\n" + "="*70)
    print("✅ EXPORT COMPLETE!")
    print("="*70)
    print(f"\nYou can now open these files to verify all your data:")
    print(f"  - {json_path} (structured data with full metadata)")
    print(f"  - {csv_path} (spreadsheet format for Excel/Google Sheets)")
    print("\n💡 Tip: Open CSV in Excel to analyze your data easily!")

def main():
    """Main function"""
    try:
        export_all_data()
    except Exception as e:
        print(f"\n❌ Error during export: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
