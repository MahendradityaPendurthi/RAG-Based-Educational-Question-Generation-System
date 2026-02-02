#!/usr/bin/env python3
"""
Clear the entire vector database
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from scripts.vector_db import VectorDB

def main():
    print("\n" + "="*70)
    print("CLEAR VECTOR DATABASE")
    print("="*70)

    print("\nThis will delete ALL data from the vector database.")
    confirm = input("Are you sure you want to continue? (yes/no): ").strip().lower()

    if confirm != 'yes':
        print("\nOperation cancelled.")
        return

    print("\nClearing database...")
    vector_db = VectorDB()
    vector_db.reset_database()

    print("\n" + "="*70)
    print("DATABASE CLEARED SUCCESSFULLY")
    print("="*70)
    print("\nYou can now upload new PDFs without ID conflicts.")
    print("Run: venv/Scripts/python.exe scripts/complete_workflow.py")

if __name__ == "__main__":
    main()
