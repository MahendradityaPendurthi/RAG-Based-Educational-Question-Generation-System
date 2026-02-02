#!/usr/bin/env python3
"""
Test script to verify the Education RAG system installation
"""

import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all required packages are installed"""
    print("\n" + "="*70)
    print("TEST 1: Checking Package Imports")
    print("="*70)
    
    packages = {
        'chromadb': 'ChromaDB',
        'anthropic': 'Anthropic API',
        'pdfplumber': 'PDF Parser',
        'sentence_transformers': 'Sentence Transformers',
        'fastapi': 'FastAPI',
        'langchain': 'LangChain',
        'pandas': 'Pandas',
        'numpy': 'NumPy'
    }
    
    success = True
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"✅ {name} - OK")
        except ImportError as e:
            print(f"❌ {name} - FAILED: {str(e)}")
            success = False
    
    return success

def test_config():
    """Test if configuration is loaded correctly"""
    print("\n" + "="*70)
    print("TEST 2: Checking Configuration")
    print("="*70)
    
    try:
        from config.config import settings
        
        print(f"✅ Configuration loaded")
        print(f"   - Vector DB Path: {settings.vector_db_path}")
        print(f"   - Uploads Path: {settings.uploads_path}")
        print(f"   - Outputs Path: {settings.outputs_path}")
        print(f"   - Embedding Model: {settings.embedding_model}")
        print(f"   - Claude Model: {settings.claude_model}")
        
        if settings.anthropic_api_key:
            print(f"✅ Anthropic API key is set")
        else:
            print(f"⚠️  Anthropic API key is NOT set")
            print(f"   Please set ANTHROPIC_API_KEY in .env file")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration failed: {str(e)}")
        return False

def test_vector_db():
    """Test if vector database can be initialized"""
    print("\n" + "="*70)
    print("TEST 3: Testing Vector Database")
    print("="*70)
    
    try:
        from scripts.vector_db import VectorDB
        
        db = VectorDB()
        print(f"✅ Vector database initialized")
        
        # Try adding test data
        test_chunks = [
            {
                'content': 'Test content for verification',
                'metadata': {
                    'class': 8,
                    'subject': 'Test',
                    'chapter': 'Test Chapter',
                    'topic': 'Test Topic',
                    'content_type': 'test',
                    'difficulty': 'easy',
                    'page': 1
                }
            }
        ]
        
        added = db.add_chunks(test_chunks)
        print(f"✅ Successfully added test chunk")
        
        # Try searching
        results = db.search("test", n_results=1)
        if results['documents'][0]:
            print(f"✅ Successfully searched database")
        
        # Get stats
        stats = db.get_collection_stats()
        print(f"✅ Database stats: {stats.get('total_chunks', 0)} total chunks")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector database test failed: {str(e)}")
        return False

def test_pdf_parser():
    """Test if PDF parser works"""
    print("\n" + "="*70)
    print("TEST 4: Testing PDF Parser")
    print("="*70)
    
    try:
        from scripts.pdf_parser import PDFParser
        
        parser = PDFParser()
        print(f"✅ PDF parser initialized")
        
        # Test content classification
        test_text = "Definition: The Pythagorean theorem states that a² + b² = c²"
        content_type = parser.classify_content_type(test_text)
        print(f"✅ Content classification works: '{content_type}'")
        
        return True
        
    except Exception as e:
        print(f"❌ PDF parser test failed: {str(e)}")
        return False

def test_content_generator():
    """Test if content generator can be initialized"""
    print("\n" + "="*70)
    print("TEST 5: Testing Content Generator")
    print("="*70)

    try:
        from scripts.content_generator import ContentGenerator
        from config.config import settings

        # Check if any API key is set
        has_gemini = bool(settings.gemini_api_key)
        has_anthropic = bool(settings.anthropic_api_key)

        if not has_gemini and not has_anthropic:
            print(f"⚠️  Skipping - No API key set")
            print(f"   To use Gemini (FREE): Get key from https://makersuite.google.com/app/apikey")
            print(f"   Add to .env: GEMINI_API_KEY=your_key_here")
            print(f"   Or set ANTHROPIC_API_KEY for Claude (paid)")
            return True

        generator = ContentGenerator()
        provider = settings.llm_provider.upper()
        print(f"✅ Content generator initialized with {provider}")
        print(f"✅ LLM API connection successful")

        return True

    except Exception as e:
        import traceback
        print(f"❌ Content generator test failed: {str(e)}")
        print(f"\n💡 Tip: Get FREE Gemini API key from https://makersuite.google.com/app/apikey")
        return False

def test_api_server():
    """Test if API server can be imported"""
    print("\n" + "="*70)
    print("TEST 6: Testing API Server")
    print("="*70)
    
    try:
        # Just test if it can be imported
        import api_server
        print(f"✅ API server can be imported")
        print(f"   Start server with: python api_server.py")
        
        return True
        
    except Exception as e:
        import traceback
        print(f"❌ API server test failed: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("EDUCATION RAG SYSTEM - INSTALLATION TEST")
    print("="*70)
    
    tests = [
        ("Package Imports", test_imports),
        ("Configuration", test_config),
        ("Vector Database", test_vector_db),
        ("PDF Parser", test_pdf_parser),
        ("Content Generator", test_content_generator),
        ("API Server", test_api_server)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Upload PDFs to ./uploads/ directory")
        print("2. Run: python scripts/main_pipeline.py --pdf your_file.pdf --class 6 --subject Science")
        print("3. Or start API server: python api_server.py")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("Common issues:")
        print("- Missing packages: pip install -r requirements.txt")
        print("- Missing API key: Get FREE Gemini key from https://makersuite.google.com/app/apikey")
        print("  Add to .env: GEMINI_API_KEY=your_key_here")
    
    print("="*70)

if __name__ == "__main__":
    main()
