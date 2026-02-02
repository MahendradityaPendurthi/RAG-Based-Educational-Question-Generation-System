# Troubleshooting Guide
## Common Issues and Solutions

---

## Installation Issues

### Issue 1: "Python not found" or "python: command not found"

**Symptoms:**
```
bash: python: command not found
```

**Solutions:**

**On Linux/Mac:**
```bash
# Try python3 instead
python3 --version

# If not installed, install Python
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv

# Mac (with Homebrew):
brew install python3
```

**On Windows:**
1. Download Python from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Restart command prompt

---

### Issue 2: "pip: command not found"

**Solution:**
```bash
# Linux/Mac:
python3 -m pip --version

# If not installed:
sudo apt-get install python3-pip  # Ubuntu/Debian
brew install python3               # Mac

# Windows:
python -m pip --version
```

---

### Issue 3: Requirements installation fails

**Symptoms:**
```
ERROR: Could not build wheels for chromadb
```

**Solutions:**

**On Linux:**
```bash
# Install build dependencies
sudo apt-get install build-essential python3-dev

# Retry installation
pip install -r requirements.txt
```

**On Mac:**
```bash
# Install Xcode command line tools
xcode-select --install

# Retry
pip install -r requirements.txt
```

**On Windows:**
```cmd
# Install Microsoft C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Then retry
pip install -r requirements.txt
```

---

## Configuration Issues

### Issue 4: "ANTHROPIC_API_KEY not found"

**Symptoms:**
```
ValueError: ANTHROPIC_API_KEY not set in environment variables
```

**Solution:**
```bash
# 1. Check if .env file exists
ls -la .env

# 2. If not, create it
cp .env.example .env

# 3. Edit .env file
nano .env  # or use any text editor

# 4. Add your API key:
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here

# 5. Verify it's set
cat .env | grep ANTHROPIC_API_KEY
```

**Get API Key:**
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Go to API Keys section
4. Generate a new key
5. Copy and paste into .env file

---

### Issue 5: Invalid API key error

**Symptoms:**
```
anthropic.AuthenticationError: Invalid API key
```

**Solutions:**
1. Check for extra spaces in .env file
2. Make sure you copied the entire key
3. Verify key is active in Anthropic console
4. Try generating a new key

```bash
# Check .env file format
cat .env

# Should look like:
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx
# NO quotes, NO spaces before/after =
```

---

## PDF Processing Issues

### Issue 6: "File not found" when processing PDF

**Symptoms:**
```
FileNotFoundError: PDF file not found: uploads/file.pdf
```

**Solutions:**

```bash
# 1. Check if file exists
ls -la uploads/

# 2. Check file path
# Use absolute path if needed
python scripts/main_pipeline.py \
  --pdf /full/path/to/file.pdf \
  --class 8 \
  --subject Math

# 3. Check file permissions
chmod 644 uploads/your_file.pdf
```

---

### Issue 7: PDF parsing returns no chunks

**Symptoms:**
```
✅ Successfully processed 0 chunks
```

**Possible Causes:**
1. PDF is image-based (scanned), not text-based
2. PDF has DRM protection
3. PDF has unusual encoding
4. File is corrupted

**Solutions:**

**Check if PDF has text:**
```bash
# Install pdftotext
sudo apt-get install poppler-utils  # Linux
brew install poppler                  # Mac

# Extract text
pdftotext uploads/your_file.pdf test.txt

# Check if text.txt has content
cat test.txt
```

**If PDF is image-based:**
- You need OCR (Optical Character Recognition)
- Convert to text PDF first using tools like Adobe Acrobat
- Or use OCR libraries (not included in basic setup)

**If PDF has protection:**
- Remove protection using PDF tools
- Get unprotected version from publisher

---

### Issue 8: Extraction is very slow

**Symptoms:**
Processing takes hours for a single PDF

**Solutions:**

```bash
# 1. Reduce chunk size in .env
CHUNK_SIZE=300
CHUNK_OVERLAP=30

# 2. Process in batches
# Split large PDF into smaller files

# 3. Check system resources
top  # Linux/Mac
# Windows: Task Manager

# 4. Close other applications
# Give more RAM to the process
```

---

## Database Issues

### Issue 9: ChromaDB errors

**Symptoms:**
```
chromadb.errors.InvalidCollectionException
```

**Solutions:**

```bash
# 1. Reset database
python scripts/main_pipeline.py --reset
# Type 'yes' to confirm

# 2. Delete vector database folder
rm -rf vectordb/
mkdir vectordb

# 3. Reinstall ChromaDB
pip uninstall chromadb
pip install chromadb==0.4.22

# 4. Reprocess PDFs
```

---

### Issue 10: "Database is locked"

**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**

```bash
# 1. Close any running processes
pkill -f "python.*pipeline"
pkill -f "python.*api_server"

# 2. Remove lock file
rm vectordb/*.lock

# 3. Restart process
```

---

## Generation Issues

### Issue 11: Generated content is poor quality

**Symptoms:**
- Questions don't make sense
- Answers are incorrect
- Content is irrelevant

**Solutions:**

**1. Check if database has content:**
```bash
python scripts/main_pipeline.py --stats
```

If `total_chunks: 0`, process PDFs first.

**2. Be more specific in queries:**
```python
# ❌ Too vague
topic="Math"

# ✅ Specific
topic="Quadratic Equations"
```

**3. Check retrieved content:**
```python
from scripts.vector_db import VectorDB

db = VectorDB()
results = db.search(
    query="your topic",
    filters={'class': 8, 'subject': 'Math'},
    n_results=10
)

# Check if results are relevant
for doc in results['documents'][0]:
    print(doc[:200])
```

**4. Adjust retrieval parameters:**
```python
# Get more context
results = db.search(query, n_results=20)  # Instead of 10

# Try different query phrasing
query = "algebra equations solving methods"  # Instead of just "algebra"
```

**5. Check Claude model:**
```bash
# In .env file
CLAUDE_MODEL=claude-sonnet-4-20250514  # Use Sonnet for better quality
# Or try Opus for best quality (more expensive)
CLAUDE_MODEL=claude-opus-4-5-20251101
```

---

### Issue 12: API rate limit errors

**Symptoms:**
```
anthropic.RateLimitError: Rate limit exceeded
```

**Solutions:**

```python
# Add delays between requests
import time

for i in range(10):
    result = generator.generate_mcq(...)
    time.sleep(2)  # Wait 2 seconds between calls
```

**Check your rate limits:**
- Go to https://console.anthropic.com/
- Check your usage and limits
- Upgrade plan if needed

---

### Issue 13: "Context too long" error

**Symptoms:**
```
anthropic.BadRequestError: prompt is too long
```

**Solutions:**

```bash
# 1. Reduce retrieval count
# In content_generator.py, change:
n_results=10  # Instead of 20

# 2. Reduce max_tokens in .env
MAX_TOKENS=3000  # Instead of 4000

# 3. Split generation into smaller batches
# Instead of 50 questions, generate 10 at a time
```

---

## API Server Issues

### Issue 14: Port already in use

**Symptoms:**
```
OSError: [Errno 48] Address already in use
```

**Solutions:**

```bash
# 1. Find process using port 8000
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# 2. Kill the process
kill -9 <PID>  # Linux/Mac
taskkill /F /PID <PID>  # Windows

# 3. Or use different port
# In .env:
API_PORT=8001

# Or when starting:
uvicorn api_server:app --port 8001
```

---

### Issue 15: CORS errors in browser

**Symptoms:**
```
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solution:**

API already has CORS enabled for all origins. If still having issues:

```python
# In api_server.py, modify CORS settings:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Memory Issues

### Issue 16: Out of memory errors

**Symptoms:**
```
MemoryError: Unable to allocate array
```

**Solutions:**

**1. Process in smaller batches:**
```python
# Instead of processing all at once
batch_size = 100
for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i+batch_size]
    vector_db.add_chunks(batch)
```

**2. Use smaller embedding model:**
```bash
# In .env:
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Smaller, faster

# Instead of:
EMBEDDING_MODEL=all-mpnet-base-v2  # Larger, uses more RAM
```

**3. Increase system swap:**
```bash
# Linux: Check current swap
free -h

# Increase if needed
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**4. Close other applications:**
- Close browser tabs
- Stop unnecessary services
- Restart system if needed

---

## Permission Issues

### Issue 17: Permission denied errors

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**

```bash
# Fix file permissions
chmod -R 755 education-rag-system/

# Fix specific directories
chmod 755 uploads/ outputs/ logs/ vectordb/

# If using sudo, don't - use virtual environment instead
```

---

## Import Issues

### Issue 18: ModuleNotFoundError

**Symptoms:**
```
ModuleNotFoundError: No module named 'anthropic'
```

**Solutions:**

```bash
# 1. Verify virtual environment is activated
which python  # Should show venv/bin/python

# If not activated:
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Reinstall requirements
pip install -r requirements.txt

# 3. Check installation
pip list | grep anthropic
```

---

### Issue 19: Relative import errors

**Symptoms:**
```
ImportError: attempted relative import with no known parent package
```

**Solutions:**

```bash
# Run scripts from project root, not from scripts/ directory
cd education-rag-system
python scripts/main_pipeline.py ...

# Not:
cd scripts
python main_pipeline.py ...  # ❌ Will fail
```

---

## Debugging Tips

### Enable Detailed Logging

```python
# At the top of your script
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Check Log Files

```bash
# View latest log
ls -lt logs/
tail -f logs/app.log

# Search for errors
grep -i error logs/*.log
grep -i exception logs/*.log
```

### Test Components Individually

```python
# Test PDF parser only
from scripts.pdf_parser import PDFParser
parser = PDFParser()
chunks = parser.parse_pdf("test.pdf", 8, "Math")
print(f"Got {len(chunks)} chunks")

# Test vector DB only
from scripts.vector_db import VectorDB
db = VectorDB()
stats = db.get_collection_stats()
print(stats)

# Test Claude API only
from anthropic import Anthropic
client = Anthropic(api_key="your-key")
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=100,
    messages=[{"role": "user", "content": "Test"}]
)
print(response.content[0].text)
```

---

## Getting Help

If none of these solutions work:

1. **Check logs:**
   ```bash
   cat logs/app.log
   ```

2. **Run system test:**
   ```bash
   python scripts/test_system.py
   ```

3. **Check versions:**
   ```bash
   python --version
   pip list
   ```

4. **Search error message:**
   - Google the exact error message
   - Check ChromaDB GitHub issues
   - Check Anthropic API docs

5. **Verify file structure:**
   ```bash
   tree -L 2 education-rag-system/
   ```

6. **Try fresh installation:**
   ```bash
   # Backup .env file first
   cp .env .env.backup
   
   # Remove virtual environment
   rm -rf venv/
   
   # Reinstall
   ./setup.sh  # or setup.bat on Windows
   
   # Restore .env
   cp .env.backup .env
   ```

---

## Common Error Reference

| Error | Likely Cause | Quick Fix |
|-------|--------------|-----------|
| `ImportError` | Wrong directory or venv not activated | Run from project root with venv active |
| `FileNotFoundError` | Wrong path | Use absolute path or check file exists |
| `AuthenticationError` | Wrong API key | Check .env file |
| `RateLimitError` | Too many API calls | Add delays between calls |
| `MemoryError` | Not enough RAM | Process in smaller batches |
| `PermissionError` | File permissions | Run `chmod 755` on directories |
| `ModuleNotFoundError` | Package not installed | `pip install -r requirements.txt` |
| `ConnectionError` | No internet | Check internet connection |

---

**Still stuck? The system test should help identify the issue:**
```bash
python scripts/test_system.py
```
