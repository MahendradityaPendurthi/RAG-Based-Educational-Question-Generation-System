# 🚀 Quick Start Guide
## Get Your Education RAG System Running in 10 Minutes

---

## Prerequisites Checklist

Before you start, make sure you have:
- [ ] Python 3.8 or higher installed
- [ ] Anthropic API key (get from https://console.anthropic.com/)
- [ ] At least one PDF textbook to process
- [ ] 5GB free disk space
- [ ] Internet connection

---

## Installation (5 minutes)

### Linux/Mac:

```bash
# 1. Navigate to the project directory
cd education-rag-system

# 2. Run the setup script
chmod +x setup.sh
./setup.sh
```

### Windows:

```cmd
# 1. Navigate to the project directory
cd education-rag-system

# 2. Run the setup script
setup.bat
```

### Manual Installation (All platforms):

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate it
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
```

---

## Configuration (1 minute)

Edit the `.env` file and add your Anthropic API key:

```bash
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx
```

**Get your API key:** https://console.anthropic.com/

---

## Test Installation (1 minute)

```bash
python scripts/test_system.py
```

You should see:
```
✅ All tests passed! System is ready to use.
```

---

## Process Your First PDF (3 minutes)

### Step 1: Place PDF in uploads folder

```bash
cp ~/Downloads/class_8_math.pdf uploads/
```

### Step 2: Process it

```bash
python scripts/main_pipeline.py \
  --pdf uploads/class_8_math.pdf \
  --class 8 \
  --subject Mathematics
```

Output:
```
✅ Successfully processed 847 chunks
✅ Added to vector database
```

---

## Generate Your First Content (2 minutes)

### Option 1: Using Python

```python
python scripts/example_usage.py
# Select option 2 to generate MCQs
```

### Option 2: Using API

```bash
# Start the server
python api_server.py

# In another terminal, generate MCQs
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

### Option 3: Using Python script directly

```python
from scripts.content_generator import ContentGenerator

generator = ContentGenerator()

# Generate MCQs
mcqs = generator.generate_mcq(
    class_num=8,
    subject="Mathematics",
    topic="Algebra",
    difficulty="medium",
    num_questions=10
)

print(mcqs)
```

---

## Common Tasks

### View What's in Database

```bash
python scripts/main_pipeline.py --stats
```

### Generate Flashcards

```python
from scripts.content_generator import ContentGenerator

gen = ContentGenerator()
flashcards = gen.generate_flashcards(
    class_num=8,
    subject="Mathematics",
    topic="Geometry",
    num_cards=20
)

for card in flashcards:
    print(f"Q: {card['front']}")
    print(f"A: {card['back']}\n")
```

### Generate Complete Exam Paper

```python
from scripts.content_generator import ContentGenerator

gen = ContentGenerator()
exam = gen.generate_exam_paper(
    class_num=10,
    subject="Mathematics",
    chapters=["Algebra", "Geometry"],
    total_marks=100,
    duration_minutes=180
)

print(exam)
```

### Search for Content

```python
from scripts.vector_db import VectorDB

db = VectorDB()
results = db.search(
    query="Pythagorean theorem",
    filters={'class': 8, 'subject': 'Mathematics'},
    n_results=5
)

for doc in results['documents'][0]:
    print(doc)
```

---

## Process Multiple PDFs at Once

Create a config file `my_pdfs.json`:

```json
{
  "pdfs": [
    {
      "path": "./uploads/class_8_math.pdf",
      "class": 8,
      "subject": "Mathematics"
    },
    {
      "path": "./uploads/class_8_science.pdf",
      "class": 8,
      "subject": "Science"
    },
    {
      "path": "./uploads/class_9_math.pdf",
      "class": 9,
      "subject": "Mathematics"
    }
  ]
}
```

Then run:

```bash
python scripts/main_pipeline.py --config my_pdfs.json
```

---

## Using the API Server

### Start Server

```bash
python api_server.py
```

Server runs at: http://localhost:8000

### Interactive Documentation

Open in browser: http://localhost:8000/docs

This gives you a visual interface to test all API endpoints.

### Example API Calls

**Upload PDF:**
```bash
curl -X POST "http://localhost:8000/api/upload-pdf" \
  -F "file=@uploads/textbook.pdf" \
  -F "class_num=8" \
  -F "subject=Mathematics"
```

**Generate MCQs:**
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

**Get Statistics:**
```bash
curl http://localhost:8000/api/stats
```

---

## Troubleshooting

### Problem: "No module named 'chromadb'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Problem: "ANTHROPIC_API_KEY not found"

**Solution:**
```bash
# Make sure .env file exists
ls -la .env

# If not, create it
cp .env.example .env

# Edit and add your API key
nano .env
```

### Problem: "File not found"

**Solution:**
```bash
# Make sure PDF is in uploads folder
ls -la uploads/

# Use full path if needed
python scripts/main_pipeline.py \
  --pdf /full/path/to/file.pdf \
  --class 8 \
  --subject Math
```

### Problem: Generated content is poor

**Solution:**
- Make sure you processed the PDF first
- Check database has content: `python scripts/main_pipeline.py --stats`
- Use more specific topic names
- Ensure PDF was processed correctly (check logs)

---

## Next Steps

Now that your system is running:

1. **Process all your textbooks**
   - Create a config file with all PDFs
   - Run batch processing

2. **Build your application**
   - Use the API to integrate with your app
   - Create custom generation templates
   - Add your own UI

3. **Scale up**
   - Process more textbooks
   - Generate more content types
   - Customize prompts for better results

4. **Optimize**
   - Adjust chunking parameters
   - Fine-tune difficulty detection
   - Cache frequently used content

---

## Complete Example Workflow

```bash
# 1. Setup (one-time)
./setup.sh
# Edit .env and add ANTHROPIC_API_KEY

# 2. Process PDFs
python scripts/main_pipeline.py --pdf uploads/class_8_math.pdf --class 8 --subject Math
python scripts/main_pipeline.py --pdf uploads/class_9_math.pdf --class 9 --subject Math

# 3. Check database
python scripts/main_pipeline.py --stats

# 4. Generate content
python -c "
from scripts.content_generator import ContentGenerator
gen = ContentGenerator()

# MCQs
mcqs = gen.generate_mcq(8, 'Mathematics', 'Algebra', 'medium', 10)
print(mcqs)

# Flashcards
cards = gen.generate_flashcards(8, 'Mathematics', 'Geometry', 20)
print(f'Generated {len(cards)} flashcards')

# Notes
notes = gen.generate_short_notes(8, 'Mathematics', 'Trigonometry')
print(notes)
"

# 5. Or use API
python api_server.py
# Open http://localhost:8000/docs
```

---

## Summary

✅ **5 minutes** - Installation
✅ **1 minute** - Configuration
✅ **1 minute** - Testing
✅ **3 minutes** - Process first PDF
✅ **2 minutes** - Generate first content

**Total: ~10 minutes to working system!**

---

## Support

If you get stuck:
1. Check logs: `cat logs/*.log`
2. Run tests: `python scripts/test_system.py`
3. Check README.md for detailed docs
4. Review example_usage.py for code samples

---

**Happy Teaching! 🎓🚀**
