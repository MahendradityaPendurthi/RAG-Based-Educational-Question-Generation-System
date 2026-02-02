# Education RAG System
## AI-Powered Educational Content Generation Using Retrieval Augmented Generation

A complete, production-ready system for generating educational content (MCQs, flashcards, worksheets, exam papers) from textbook PDFs using RAG (Retrieval Augmented Generation) with Claude AI.

---

## 📋 Table of Contents
- [Features](#features)
- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

### Content Generation
- **MCQ Questions** - Multiple choice questions with explanations
- **Fill in the Blank** - Fill in the blanks for assessment
- **Very Short Questions** - Vsaqs for quick learning
- **Short Questions** - Saqs for conceptual learning
- **Long Questions** - Laqs for deep learning

### Generated Content
- **Easy**
- **Medium**
- **Hard**

### Smart Processing
- **PDF Parsing** - Automatic extraction of chapters, topics, and concepts
- **Content Classification** - Auto-tagging as definitions, formulas, examples, etc.
- **Difficulty Detection** - Automatic difficulty level assignment
- **Vector Search** - Semantic search for relevant content
- **Metadata Tracking** - Class, subject, chapter, topic tracking

### API & Interface
- **REST API** - FastAPI-based REST API for integrations
- **Command Line** - CLI tools for batch processing
- **File Upload** - Upload and process PDFs via API
- **Export Options** - Save generated content as text/JSON files

---

## 🏗️ System Architecture

```
┌──────────────┐
│   PDF File   │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│  PDF Parser      │  ← Extract text, classify content
│  - Chapters      │     Auto-tag difficulty, type
│  - Topics        │
│  - Content Type  │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Create          │  ← Convert text to vectors
│  Embeddings      │     (sentence-transformers)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  ChromaDB        │  ← Store vectors + metadata
│  Vector Database │     Fast semantic search
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  User Query      │  ← "Generate 10 MCQs on
│                  │     Algebra for Class 8"
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Vector Search   │  ← Find relevant chunks
│                  │     (semantic similarity)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Gemini API      │  ← Generate questions
│                  │     using retrieved context
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Final Output    │  ← MCQs/Flashcards/Notes
└──────────────────┘
```

---

## 📦 Prerequisites

- **Python 3.8+**
- **Gemini API Key** (for Claude AI)
- **2GB+ RAM** (for embedding models)
- **10GB+ Storage** (for vector database)

---

## 🚀 Installation

### Step 1: Clone/Extract the System

```bash
cd education-rag-system
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `chromadb` - Vector database
- `anthropic` - Claude AI API client
- `pdfplumber` - PDF parsing
- `sentence-transformers` - Embeddings
- `fastapi` - API server
- `langchain` - Text processing utilities
- And more...

### Step 4: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file and add your Anthropic API key
nano .env  # or use any text editor
```

In `.env` file, set:
```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

**Get your API key from:** https://console.anthropic.com/

### Step 5: Test Installation

```bash
python scripts/test_system.py
```

You should see:
```
✅ All tests passed! System is ready to use.
```

---

## 🎯 Quick Start

### Option 1: Process a Single PDF

```bash
python scripts/main_pipeline.py \
  --pdf uploads/textbook.pdf \
  --class 8 \
  --subject Mathematics
```

### Option 2: Process Multiple PDFs from Config

1. Edit `example_pdf_config.json`:
```json
{
  "pdfs": [
    {
      "path": "./uploads/class_8_math.pdf",
      "class": 8,
      "subject": "Mathematics"
    }
  ]
}
```

2. Run:
```bash
python scripts/main_pipeline.py --config example_pdf_config.json
```

### Option 3: Start API Server

```bash
python api_server.py
```

Then visit: http://localhost:8000/docs for interactive API documentation.

---

## 📖 Usage

### Command Line Interface (CLI)

#### 1. Upload and Process PDF
```bash
python scripts/main_pipeline.py \
  --pdf uploads/class_8_science.pdf \
  --class 8 \
  --subject Science
```

#### 2. View Database Statistics
```bash
python scripts/main_pipeline.py --stats
```

Output:
```json
{
  "total_chunks": 1523,
  "by_class": {"8": 1523},
  "by_subject": {"Mathematics": 800, "Science": 723},
  "by_content_type": {
    "definition": 234,
    "formula": 156,
    "example": 445,
    "explanation": 688
  }
}
```

#### 3. Export Chunks to JSON
```bash
python scripts/main_pipeline.py --export chunks_backup.json
```

#### 4. Reset Database
```bash
python scripts/main_pipeline.py --reset
# Type 'yes' to confirm
```

### Python API

#### Generate MCQs
```python
from scripts.content_generator import ContentGenerator

generator = ContentGenerator()

mcqs = generator.generate_mcq(
    class_num=8,
    subject="Mathematics",
    topic="Algebra",
    difficulty="medium",
    num_questions=10
)

print(mcqs)
```

#### Generate Flashcards
```python
flashcards = generator.generate_flashcards(
    class_num=9,
    subject="Science",
    topic="Cell Biology",
    num_cards=20
)

for card in flashcards:
    print(f"Q: {card['front']}")
    print(f"A: {card['back']}\n")
```

#### Generate Short Notes
```python
notes = generator.generate_short_notes(
    class_num=10,
    subject="Mathematics",
    chapter="Trigonometry"
)

print(notes)
```

#### Generate Complete Exam Paper
```python
exam = generator.generate_exam_paper(
    class_num=10,
    subject="Mathematics",
    chapters=["Algebra", "Geometry", "Trigonometry"],
    total_marks=100,
    duration_minutes=180
)

print(exam)
```

---

## 🌐 API Documentation

### Start API Server
```bash
python api_server.py
```

Server runs at: `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

### API Endpoints

#### 1. Upload PDF
```bash
POST /api/upload-pdf
```

Example with curl:
```bash
curl -X POST "http://localhost:8000/api/upload-pdf" \
  -F "file=@textbook.pdf" \
  -F "class_num=8" \
  -F "subject=Mathematics"
```

#### 2. Generate MCQs
```bash
POST /api/generate/mcq
```

Request body:
```json
{
  "class_num": 8,
  "subject": "Mathematics",
  "topic": "Algebra",
  "difficulty": "medium",
  "num_questions": 10
}
```

Example:
```bash
curl -X POST "http://localhost:8000/api/generate/mcq" \
  -H "Content-Type: application/json" \
  -d '{
    "class_num": 8,
    "subject": "Mathematics",
    "topic": "Algebra",
    "difficulty": "medium",
    "num_questions": 10
  }'
```

#### 3. Generate Flashcards
```bash
POST /api/generate/flashcards
```

Request body:
```json
{
  "class_num": 9,
  "subject": "Science",
  "topic": "Photosynthesis",
  "num_cards": 20
}
```

#### 4. Generate Short Notes
```bash
POST /api/generate/notes
```

Request body:
```json
{
  "class_num": 10,
  "subject": "Mathematics",
  "chapter": "Trigonometry"
}
```

#### 5. Search Content
```bash
GET /api/search?query=pythagoras&class_num=8&subject=Mathematics
```

#### 6. Get Statistics
```bash
GET /api/stats
```

---

## 📁 Directory Structure

```
education-rag-system/
│
├── config/
│   └── config.py              # Configuration management
│
├── scripts/
│   ├── pdf_parser.py          # PDF extraction & parsing
│   ├── vector_db.py           # Vector database operations
│   ├── content_generator.py   # Claude-based generation
│   ├── main_pipeline.py       # Main orchestration script
│   └── test_system.py         # System tests
│
├── uploads/                   # Put your PDF files here
├── outputs/                   # Generated content saved here
├── vectordb/                  # ChromaDB storage
├── logs/                      # Application logs
│
├── api_server.py              # FastAPI server
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── example_pdf_config.json   # Example config
└── README.md                 # This file
```

---

## 🎓 Example Workflow

### Full Workflow: From PDF to Questions

```bash
# Step 1: Upload your PDFs to uploads folder
cp ~/Downloads/class_8_math.pdf uploads/

# Step 2: Process the PDF
python scripts/main_pipeline.py \
  --pdf uploads/class_8_math.pdf \
  --class 8 \
  --subject Mathematics

# Output:
# ✅ Successfully processed 847 chunks
# ✅ Added to vector database

# Step 3: Check what was added
python scripts/main_pipeline.py --stats

# Step 4: Generate MCQs
python -c "
from scripts.content_generator import ContentGenerator
gen = ContentGenerator()
mcqs = gen.generate_mcq(8, 'Mathematics', 'Algebra', 'medium', 10)
print(mcqs)
"

# Or use the API:
python api_server.py
# Then open http://localhost:8000/docs
# Use the interactive UI to generate content
```

---

## 🔧 Configuration Options

Edit `.env` file to customize:

```bash
# API Key
ANTHROPIC_API_KEY=your_key_here

# Claude Model (change for different models)
CLAUDE_MODEL=claude-sonnet-4-20250514
# Options: claude-opus-4-5, claude-sonnet-4-5, claude-haiku-4-5

# Generation Settings
MAX_TOKENS=4000
TEMPERATURE=0.7

# Chunking (adjust based on your content)
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2
# Options: all-MiniLM-L6-v2 (fast), all-mpnet-base-v2 (better quality)

# Server
API_PORT=8000
```

---

## 💡 Tips & Best Practices

### For Best Results:

1. **PDF Quality**
   - Use clean, text-based PDFs (not scanned images)
   - Ensure clear chapter/section headings
   - Avoid PDFs with complex layouts

2. **Processing**
   - Process one textbook at a time initially
   - Check stats after each upload to verify chunks
   - Start with smaller PDFs to test

3. **Content Generation**
   - Be specific in topic queries
   - Use appropriate difficulty levels
   - Review generated content for accuracy

4. **Performance**
   - First run downloads embedding model (~500MB)
   - Subsequent runs are much faster
   - Vector search is very fast (milliseconds)

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "ANTHROPIC_API_KEY not found"
**Solution:**
```bash
# Make sure .env file exists
cp .env.example .env

# Edit .env and add your API key
nano .env
```

### Issue: PDF parsing fails
**Solution:**
- Check if PDF is text-based (not scanned image)
- Try opening PDF in a PDF reader first
- Check file permissions

### Issue: No results in search
**Solution:**
```bash
# Check if database has content
python scripts/main_pipeline.py --stats

# If total_chunks is 0, process PDFs first
python scripts/main_pipeline.py --pdf your_file.pdf --class 8 --subject Math
```

### Issue: Generated content is poor quality
**Solution:**
- Ensure you have good source content in database
- Try more specific topics in queries
- Increase number of retrieved chunks
- Check if PDF was processed correctly

### Issue: Out of memory
**Solution:**
- Process PDFs one at a time
- Reduce CHUNK_SIZE in .env
- Use a machine with more RAM
- Consider using a smaller embedding model

---

## 📊 System Requirements

### Minimum:
- **CPU:** 2 cores
- **RAM:** 2GB
- **Storage:** 5GB
- **Network:** For API calls to Claude

### Recommended:
- **CPU:** 4+ cores
- **RAM:** 8GB
- **Storage:** 20GB
- **GPU:** Optional (speeds up embeddings)

---

## 💰 Cost Estimation

### One-time Setup:
- Embedding generation: **FREE** (using sentence-transformers locally)
- Vector database: **FREE** (ChromaDB is open-source)

### Per Request (Claude API):
Assuming Claude Sonnet:
- **Input:** $3 per million tokens
- **Output:** $15 per million tokens

Example costs:
- 10 MCQs: ~$0.03
- 20 Fill ins: ~$0.04
- 20 VSAQs: ~$0.04
- 20 SAQs: ~$0.04
- 20 LAQs: ~$0.04

---

## 🆘 Support & Contact

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Run the test script: `python scripts/test_system.py`
3. Check logs in `./logs/` directory
4. Review Anthropic API documentation

---

## 📝 License

This is an internal educational tool. Ensure you have rights to process the PDF textbooks you upload.

---

## 🎉 You're All Set!

Your Education RAG System is ready to generate educational content!

**Next Steps:**
1. Upload your textbooks to `./uploads/`
2. Process them with the pipeline
3. Start generating amazing educational content!

**Happy Teaching! 🚀**
