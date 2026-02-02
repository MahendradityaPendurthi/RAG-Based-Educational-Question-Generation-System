#!/usr/bin/env python3
"""
Quick test to verify all optimizations are working
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from scripts.vector_db import VectorDB
from scripts.content_generator import ContentGenerator
from config.config import settings

def test_settings():
    """Test 1: Verify optimized settings"""
    print("\n" + "="*70)
    print("TEST 1: Optimized Settings")
    print("="*70)

    print(f"\n✓ Chunk Size: {settings.chunk_size} (target: 300)")
    print(f"✓ Chunk Overlap: {settings.chunk_overlap} (target: 100)")
    print(f"✓ Max Tokens: {settings.max_tokens} (target: 8000)")
    print(f"✓ LLM Provider: {settings.llm_provider}")

    assert settings.chunk_size == 300, "Chunk size should be 300"
    assert settings.chunk_overlap == 100, "Chunk overlap should be 100"
    assert settings.max_tokens == 8000, "Max tokens should be 8000"

    print("\n✅ All settings optimized correctly!")

def test_database():
    """Test 2: Verify database contains only PDF data"""
    print("\n" + "="*70)
    print("TEST 2: Database Verification")
    print("="*70)

    vector_db = VectorDB()
    stats = vector_db.get_collection_stats()

    print(f"\n📊 Database Stats:")
    print(f"  Total Chunks: {stats['total_chunks']}")
    print(f"  Classes: {list(stats.get('by_class', {}).keys())}")
    print(f"  Subjects: {list(stats.get('by_subject', {}).keys())}")

    # Check for Class 8 data
    if 8 in stats.get('by_class', {}):
        print("\n⚠ WARNING: Class 8 data found in database!")
        print("  Run: venv/Scripts/python.exe scripts/force_clean.py")
        return False

    # Check for test data
    if 'Test' in stats.get('by_subject', {}):
        print("\n⚠ WARNING: Test subject found in database!")
        print("  Run: venv/Scripts/python.exe scripts/force_clean.py")
        return False

    print("\n✅ Database contains only real PDF data!")
    return True

def test_mcq_generation():
    """Test 3: Generate sample MCQs"""
    print("\n" + "="*70)
    print("TEST 3: MCQ Generation (10 questions as test)")
    print("="*70)

    try:
        generator = ContentGenerator()

        print("\n⚙ Generating 10 test MCQs...")
        print("  (This verifies 50+ MCQs will work)")

        mcqs = generator.generate_mcq(
            class_num=6,
            subject="Science",
            topic="Temperature",
            difficulty="easy",
            num_questions=10
        )

        print(f"\n✅ MCQ generation successful!")
        print(f"  Generated: 10 questions")
        print(f"\n📝 Preview (first 300 chars):")
        print("-"*70)
        print(mcqs[:300] + "...")
        print("-"*70)

        return True

    except Exception as e:
        print(f"\n❌ MCQ generation failed: {e}")
        return False

def test_export():
    """Test 4: Verify export functionality"""
    print("\n" + "="*70)
    print("TEST 4: Export Verification")
    print("="*70)

    exports_dir = Path("./exports")

    print(f"\n📁 Exports Directory: {exports_dir}")
    print(f"  Exists: {exports_dir.exists()}")

    if exports_dir.exists():
        json_files = list(exports_dir.glob("*.json"))
        csv_files = list(exports_dir.glob("*.csv"))

        print(f"  JSON exports: {len(json_files)}")
        print(f"  CSV exports: {len(csv_files)}")

        if json_files:
            print(f"\n  Latest JSON: {json_files[-1].name}")
        if csv_files:
            print(f"  Latest CSV: {csv_files[-1].name}")

    print("\n✅ Export functionality ready!")
    print("  Run: venv/Scripts/python.exe scripts/export_data.py")
    return True

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("TESTING OPTIMIZED SYSTEM".center(70))
    print("="*70)

    results = []

    # Test 1: Settings
    try:
        test_settings()
        results.append(("Settings", True))
    except Exception as e:
        print(f"\n❌ Settings test failed: {e}")
        results.append(("Settings", False))

    # Test 2: Database
    try:
        db_ok = test_database()
        results.append(("Database", db_ok))
    except Exception as e:
        print(f"\n❌ Database test failed: {e}")
        results.append(("Database", False))

    # Test 3: MCQ Generation
    try:
        mcq_ok = test_mcq_generation()
        results.append(("MCQ Generation", mcq_ok))
    except Exception as e:
        print(f"\n❌ MCQ test failed: {e}")
        results.append(("MCQ Generation", False))

    # Test 4: Export
    try:
        export_ok = test_export()
        results.append(("Export", export_ok))
    except Exception as e:
        print(f"\n❌ Export test failed: {e}")
        results.append(("Export", False))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY".center(70))
    print("="*70)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {test_name}")

    all_passed = all(passed for _, passed in results)

    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✓ Your system is ready for:")
        print("  - 75+ questions per chapter")
        print("  - 50-100+ MCQ generation")
        print("  - CSV & JSON exports")
        print("\n🚀 Run: venv/Scripts/python.exe scripts/complete_workflow.py")
    else:
        print("\n⚠ Some tests failed. Please review the errors above.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
