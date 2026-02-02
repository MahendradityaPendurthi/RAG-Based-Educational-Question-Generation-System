# Project Structure Overview

```
education-rag-system/
│
├── 📁 config/                          # Configuration management
│   ├── __init__.py
│   └── config.py                       # Settings and environment variables
│
├── 📁 scripts/                         # Main application scripts
│   ├── __init__.py
│   ├── pdf_parser.py                   # PDF extraction and content classification
│   ├── vector_db.py                    # ChromaDB vector database operations
│   ├── content_generator.py            # Claude API content generation
│   ├── main_pipeline.py                # Main orchestration script with CLI
│   ├── test_system.py                  # System installation and health tests
│   └── example_usage.py                # Example code for all features
│
├── 📁 uploads/                         # ⬆️ Place your PDF textbooks here
│
├── 📁 outputs/                         # ⬇️ Generated content saved here
│   ├── mcqs_*.txt
│   ├── flashcards_*.json
│   ├── notes_*.txt
│   └── worksheets_*.txt
│
├── 📁 vectordb/                        # 💾 ChromaDB vector storage
│   └── (database files created automatically)
│
├── 📁 logs/                            # 📋 Application logs
│   └── app_*.log
│
├── 📁 venv/                            # 🐍 Python virtual environment
│   └── (created during installation)
│
├── 📄 api_server.py                    # 🌐 FastAPI REST API server
│
├── 📄 requirements.txt                 # 📦 Python dependencies
│
├── 📄 .env.example                     # ⚙️ Environment variables template
├── 📄 .env                             # ⚙️ Your actual configuration (created during setup)
│
├── 📄 example_pdf_config.json          # 📝 Example batch processing config
│
├── 📄 setup.sh                         # 🚀 Linux/Mac setup script
├── 📄 setup.bat                        # 🚀 Windows setup script
│
├── 📄 README.md                        # 📖 Main documentation
├── 📄 QUICK_START.md                   # ⚡ 10-minute getting started guide
├── 📄 INSTALLATION.md                  # 🔧 Detailed installation instructions
├── 📄 TROUBLESHOOTING.md               # 🆘 Common issues and solutions
├── 📄 PROJECT_STRUCTURE.md             # 📂 This file
└── 📄 LICENSE                          # ⚖️ MIT License

```

## Component Descriptions

### Core Components

#### 1. PDF Parser (`scripts/pdf_parser.py`)
- **Purpose:** Extract and structure content from PDF textbooks
- **Features:**
  - Chapter/section detection
  - Content type classification (definition, formula, example, etc.)
  - Difficulty level estimation
  - Metadata tagging
- **Key Functions:**
  - `parse_pdf()` - Process single PDF
  - `classify_content_type()` - Detect content type
  - `estimate_difficulty()` - Auto-assign difficulty

#### 2. Vector Database (`scripts/vector_db.py`)
- **Purpose:** Store and retrieve content using semantic search
- **Technology:** ChromaDB with sentence-transformers
- **Features:**
  - Embedding generation
  - Metadata filtering
  - Similarity search
  - Statistics and analytics
- **Key Functions:**
  - `add_chunks()` - Store content
  - `search()` - Find similar content
  - `get_collection_stats()` - Database statistics

#### 3. Content Generator (`scripts/content_generator.py`)
- **Purpose:** Generate educational content using Claude AI
- **Features:**
  - MCQ generation
  - Flashcard creation
  - Short notes summarization
  - Worksheet compilation
  - Exam paper generation
- **Key Functions:**
  - `generate_mcq()` - Multiple choice questions
  - `generate_flashcards()` - Study flashcards
  - `generate_short_notes()` - Chapter summaries
  - `generate_worksheet()` - Practice worksheets
  - `generate_exam_paper()` - Complete exam papers

#### 4. Main Pipeline (`scripts/main_pipeline.py`)
- **Purpose:** Orchestrate the entire workflow
- **Features:**
  - Single/batch PDF processing
  - Configuration file support
  - Database management
  - Export utilities
- **CLI Commands:**
  - `--pdf` - Process single PDF
  - `--config` - Batch process from config
  - `--stats` - View database statistics
  - `--export` - Export data to JSON
  - `--reset` - Reset database

#### 5. API Server (`api_server.py`)
- **Purpose:** RESTful API for integrations
- **Technology:** FastAPI
- **Endpoints:**
  - `POST /api/upload-pdf` - Upload and process PDF
  - `POST /api/generate/mcq` - Generate MCQs
  - `POST /api/generate/flashcards` - Generate flashcards
  - `POST /api/generate/notes` - Generate notes
  - `POST /api/generate/worksheet` - Generate worksheet
  - `POST /api/generate/exam` - Generate exam paper
  - `GET /api/search` - Search content
  - `GET /api/stats` - Database statistics
- **Features:**
  - CORS enabled
  - File upload support
  - Interactive documentation at `/docs`

### Configuration

#### Environment Variables (`.env`)
```bash
# API Configuration
ANTHROPIC_API_KEY=your-key-here

# Paths
VECTOR_DB_PATH=./vectordb
UPLOADS_PATH=./uploads
OUTPUTS_PATH=./outputs

# Models
EMBEDDING_MODEL=all-MiniLM-L6-v2
CLAUDE_MODEL=claude-sonnet-4-20250514

# Generation
MAX_TOKENS=4000
TEMPERATURE=0.7

# Chunking
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# Server
API_HOST=0.0.0.0
API_PORT=8000
```

### Data Flow

```
┌─────────────┐
│   PDF File  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  pdf_parser.py  │ ── Extract & Classify
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Embeddings     │ ── sentence-transformers
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  vector_db.py   │ ── Store in ChromaDB
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  User Query     │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Semantic       │ ── Find similar chunks
│  Search         │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  content_       │ ── Generate with Claude
│  generator.py   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Final Output   │
└─────────────────┘
```

### Usage Patterns

#### Pattern 1: CLI Workflow
```bash
# 1. Process PDF
python scripts/main_pipeline.py --pdf textbook.pdf --class 8 --subject Math

# 2. Generate content
python scripts/example_usage.py
```

#### Pattern 2: Programmatic Usage
```python
from scripts.content_generator import ContentGenerator

gen = ContentGenerator()
mcqs = gen.generate_mcq(8, "Math", "Algebra", "medium", 10)
```

#### Pattern 3: API Integration
```bash
# Start server
python api_server.py

# Make requests
curl -X POST http://localhost:8000/api/generate/mcq \
  -H "Content-Type: application/json" \
  -d '{"class_num": 8, "subject": "Math", "topic": "Algebra", "difficulty": "medium", "num_questions": 10}'
```

### File Formats

#### Input (PDFs)
- Text-based PDFs (not scanned images)
- Structured with chapters and sections
- Classes 5-10 textbooks

#### Output Files

**MCQs** (`outputs/mcq_*.txt`):
```
Question 1: [Question text]
A) Option 1
B) Option 2
C) Option 3
D) Option 4
Correct Answer: A
Explanation: [Explanation]
```

**Flashcards** (`outputs/flashcards_*.json`):
```json
{
  "flashcards": [
    {
      "front": "Question",
      "back": "Answer",
      "hint": "Memory aid"
    }
  ]
}
```

**Notes** (`outputs/notes_*.txt`):
```
1. KEY CONCEPTS
- Concept 1: Explanation
- Concept 2: Explanation

2. IMPORTANT DEFINITIONS
...
```

### Database Schema

#### Content Blocks
```python
{
    'content': str,              # Actual text content
    'metadata': {
        'class': int,            # 5-10
        'subject': str,          # Mathematics, Science, etc.
        'chapter': str,          # Chapter name
        'topic': str,            # Topic/section name
        'content_type': str,     # definition, formula, example, etc.
        'difficulty': str,       # easy, medium, hard
        'page': int,             # Page number
        'source_file': str       # Original PDF filename
    }
}
```

### Dependencies

#### Core Dependencies
- **chromadb** (0.4.22) - Vector database
- **anthropic** (0.18.1) - Claude API client
- **pdfplumber** (0.10.3) - PDF parsing
- **sentence-transformers** (2.3.1) - Embeddings
- **fastapi** (0.109.0) - API framework
- **uvicorn** (0.27.0) - ASGI server
- **langchain** (0.1.4) - Text processing
- **python-dotenv** (1.0.0) - Environment management

#### Supporting Libraries
- **pandas** - Data manipulation
- **numpy** - Numerical operations
- **pydantic** - Data validation
- **python-multipart** - File uploads
- **python-docx** - Word document generation
- **openpyxl** - Excel support

### Security Considerations

1. **API Key Storage**
   - Never commit `.env` file
   - Keep API key secure
   - Rotate keys periodically

2. **File Uploads**
   - Validate PDF files
   - Limit file sizes
   - Sanitize filenames

3. **API Access**
   - Consider adding authentication
   - Rate limiting recommended
   - HTTPS for production

### Performance Tips

1. **Processing Large PDFs**
   - Process in batches
   - Use smaller chunk sizes
   - Enable caching

2. **Generation Speed**
   - Cache frequent queries
   - Batch similar requests
   - Use appropriate models (Haiku for speed, Sonnet for quality)

3. **Database Optimization**
   - Regular vacuuming
   - Index key metadata fields
   - Limit result counts

### Extending the System

#### Adding New Content Types

1. Add generator function in `content_generator.py`
2. Add API endpoint in `api_server.py`
3. Add example in `example_usage.py`
4. Update documentation

#### Adding New Features

1. **Custom Templates:**
   - Edit prompt templates in `content_generator.py`
   
2. **New Metadata Fields:**
   - Update `pdf_parser.py` classification
   - Update database schema
   
3. **Additional Models:**
   - Update `config.py` with new models
   - Test compatibility

### Maintenance

#### Regular Tasks

1. **Backup Database:**
   ```bash
   tar -czf vectordb_backup.tar.gz vectordb/
   ```

2. **Update Dependencies:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **Clean Logs:**
   ```bash
   find logs/ -name "*.log" -mtime +30 -delete
   ```

4. **Monitor Usage:**
   ```bash
   python scripts/main_pipeline.py --stats
   ```

### Testing

Run comprehensive tests:
```bash
python scripts/test_system.py
```

Test individual components:
```python
# Test PDF parser
from scripts.pdf_parser import PDFParser
parser = PDFParser()
chunks = parser.parse_pdf("test.pdf", 8, "Math")

# Test vector DB
from scripts.vector_db import VectorDB
db = VectorDB()
stats = db.get_collection_stats()

# Test generator (requires API key)
from scripts.content_generator import ContentGenerator
gen = ContentGenerator()
mcqs = gen.generate_mcq(8, "Math", "Algebra", "medium", 5)
```

---

## Quick Reference

### Most Used Commands

```bash
# Process PDF
python scripts/main_pipeline.py --pdf uploads/file.pdf --class 8 --subject Math

# View statistics
python scripts/main_pipeline.py --stats

# Run tests
python scripts/test_system.py

# Start API server
python api_server.py

# Run examples
python scripts/example_usage.py
```

### Most Used Python Functions

```python
from scripts.content_generator import ContentGenerator

gen = ContentGenerator()

# MCQs
gen.generate_mcq(class_num, subject, topic, difficulty, num_questions)

# Flashcards
gen.generate_flashcards(class_num, subject, topic, num_cards)

# Notes
gen.generate_short_notes(class_num, subject, chapter)

# Worksheet
gen.generate_worksheet(class_num, subject, topics, difficulty, num_questions)

# Exam
gen.generate_exam_paper(class_num, subject, chapters, total_marks, duration)
```

---

**For more details, see the other documentation files:**
- [README.md](README.md) - Main documentation
- [QUICK_START.md](QUICK_START.md) - Getting started guide
- [INSTALLATION.md](INSTALLATION.md) - Installation instructions
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Problem solving
