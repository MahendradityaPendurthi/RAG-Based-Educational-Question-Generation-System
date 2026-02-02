# Installation Guide
## Step-by-Step Instructions for Education RAG System

---

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Pre-Installation Steps](#pre-installation-steps)
3. [Installation Methods](#installation-methods)
4. [Post-Installation](#post-installation)
5. [Verification](#verification)

---

## System Requirements

### Minimum Requirements:
- **OS:** Windows 10+, macOS 10.14+, or Linux (Ubuntu 20.04+)
- **CPU:** 2 cores
- **RAM:** 4GB
- **Storage:** 10GB free space
- **Python:** 3.8 or higher
- **Internet:** Required for API calls and package downloads

### Recommended Requirements:
- **OS:** Latest stable version
- **CPU:** 4+ cores
- **RAM:** 8GB or more
- **Storage:** 20GB+ free space
- **Python:** 3.10 or higher

---

## Pre-Installation Steps

### Step 1: Check Python Installation

**Linux/Mac:**
```bash
python3 --version
```

Expected output: `Python 3.8.x` or higher

**Windows:**
```cmd
python --version
```

Expected output: `Python 3.8.x` or higher

### If Python is Not Installed:

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Mac (with Homebrew):**
```bash
# Install Homebrew first if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python3
```

**Windows:**
1. Download from https://www.python.org/downloads/
2. Run installer
3. **Important:** Check "Add Python to PATH" during installation
4. Restart command prompt after installation

### Step 2: Verify pip Installation

```bash
# Linux/Mac
python3 -m pip --version

# Windows
python -m pip --version
```

### Step 3: Get Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Click "Create Key"
5. **Save this key** - you'll need it later

---

## Installation Methods

Choose one of the following installation methods:

### Method 1: Automated Setup (Recommended)

**Linux/Mac:**
```bash
# Navigate to project directory
cd education-rag-system

# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

**Windows:**
```cmd
# Navigate to project directory
cd education-rag-system

# Run setup
setup.bat
```

The setup script will:
- Create virtual environment
- Install all dependencies
- Create .env file from template
- Run system tests

---

### Method 2: Manual Installation

#### Step 1: Create Virtual Environment

**Linux/Mac:**
```bash
cd education-rag-system
python3 -m venv venv
```

**Windows:**
```cmd
cd education-rag-system
python -m venv venv
```

#### Step 2: Activate Virtual Environment

**Linux/Mac:**
```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

If you get an error about execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Step 3: Upgrade pip

```bash
python -m pip install --upgrade pip
```

#### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This will take 3-5 minutes. You'll see packages being installed:
- chromadb
- anthropic
- pdfplumber
- sentence-transformers
- fastapi
- and more...

#### Step 5: Create Configuration File

```bash
# Linux/Mac
cp .env.example .env

# Windows
copy .env.example .env
```

#### Step 6: Edit Configuration

**Linux/Mac:**
```bash
nano .env
```

**Windows:**
```cmd
notepad .env
```

Add your Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

Save and close the file.

---

## Post-Installation

### Verify Directory Structure

Your directory should look like this:

```
education-rag-system/
├── config/
│   ├── __init__.py
│   └── config.py
├── scripts/
│   ├── __init__.py
│   ├── pdf_parser.py
│   ├── vector_db.py
│   ├── content_generator.py
│   ├── main_pipeline.py
│   ├── test_system.py
│   └── example_usage.py
├── uploads/              (empty initially)
├── outputs/              (empty initially)
├── vectordb/             (empty initially)
├── logs/                 (empty initially)
├── venv/                 (virtual environment)
├── api_server.py
├── requirements.txt
├── .env                  (your configuration)
├── .env.example
├── README.md
├── QUICK_START.md
├── INSTALLATION.md       (this file)
├── TROUBLESHOOTING.md
└── example_pdf_config.json
```

### Create Required Directories

If any are missing:

```bash
mkdir -p uploads outputs vectordb logs
```

---

## Verification

### Run System Test

```bash
python scripts/test_system.py
```

Expected output:
```
======================================================================
EDUCATION RAG SYSTEM - INSTALLATION TEST
======================================================================

TEST 1: Checking Package Imports
======================================================================
✅ ChromaDB - OK
✅ Anthropic API - OK
✅ PDF Parser - OK
✅ Sentence Transformers - OK
✅ FastAPI - OK
✅ LangChain - OK
✅ Pandas - OK
✅ NumPy - OK

TEST 2: Checking Configuration
======================================================================
✅ Configuration loaded
   - Vector DB Path: ./vectordb
   - Uploads Path: ./uploads
   - Outputs Path: ./outputs
   - Embedding Model: all-MiniLM-L6-v2
   - Claude Model: claude-sonnet-4-20250514
✅ Anthropic API key is set

TEST 3: Testing Vector Database
======================================================================
✅ Vector database initialized
✅ Successfully added test chunk
✅ Successfully searched database
✅ Database stats: 1 total chunks

TEST 4: Testing PDF Parser
======================================================================
✅ PDF parser initialized
✅ Content classification works: 'definition'

TEST 5: Testing Content Generator
======================================================================
✅ Content generator initialized
✅ Claude API connection successful

TEST 6: Testing API Server
======================================================================
✅ API server can be imported
   Start server with: python api_server.py

======================================================================
TEST SUMMARY
======================================================================
✅ PASSED - Package Imports
✅ PASSED - Configuration
✅ PASSED - Vector Database
✅ PASSED - PDF Parser
✅ PASSED - Content Generator
✅ PASSED - API Server

Total: 6/6 tests passed

🎉 All tests passed! System is ready to use.

Next steps:
1. Upload PDFs to ./uploads/ directory
2. Run: python scripts/main_pipeline.py --pdf your_file.pdf --class 8 --subject Math
3. Or start API server: python api_server.py
======================================================================
```

### If Tests Fail

If any test fails, check the [Troubleshooting Guide](TROUBLESHOOTING.md).

Common issues:
- Missing API key: Edit .env and add ANTHROPIC_API_KEY
- Import errors: Reinstall with `pip install -r requirements.txt`
- Permission errors: Check file permissions

---

## Post-Installation Setup

### 1. Download Embedding Model (First Run Only)

The first time you use the system, it will download the embedding model (~500MB):

```python
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
print('Model downloaded successfully')
"
```

This is a one-time download and will be cached.

### 2. Test with Sample Data

Create a simple test:

```python
python -c "
from scripts.vector_db import VectorDB

db = VectorDB()
print('✅ Database initialized')

# Add test data
test_chunks = [{
    'content': 'The Pythagorean theorem: a² + b² = c²',
    'metadata': {
        'class': 8,
        'subject': 'Mathematics',
        'chapter': 'Geometry',
        'topic': 'Triangles',
        'content_type': 'formula',
        'difficulty': 'medium',
        'page': 1
    }
}]

added = db.add_chunks(test_chunks)
print(f'✅ Added {added} test chunk')

# Search
results = db.search('Pythagorean theorem', n_results=1)
print(f'✅ Search works: found {len(results[\"documents\"][0])} result')
"
```

### 3. Test API Server

```bash
# Start server
python api_server.py &

# Wait a few seconds, then test
curl http://localhost:8000/

# Stop server
pkill -f api_server
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Education RAG API",
  "version": "1.0.0"
}
```

---

## Environment Variables Reference

Your `.env` file should contain:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional (defaults shown)
VECTOR_DB_PATH=./vectordb
COLLECTION_NAME=educational_content
EMBEDDING_MODEL=all-MiniLM-L6-v2
CLAUDE_MODEL=claude-sonnet-4-20250514
MAX_TOKENS=4000
TEMPERATURE=0.7
CHUNK_SIZE=500
CHUNK_OVERLAP=50
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

---

## Virtual Environment Management

### Activating Virtual Environment

You need to activate the virtual environment every time you start a new terminal session.

**Linux/Mac:**
```bash
cd education-rag-system
source venv/bin/activate
```

**Windows:**
```cmd
cd education-rag-system
venv\Scripts\activate
```

You should see `(venv)` in your prompt.

### Deactivating Virtual Environment

When you're done:
```bash
deactivate
```

### Updating Packages

To update all packages to latest versions:

```bash
pip install --upgrade -r requirements.txt
```

### Reinstalling Everything

If something goes wrong:

```bash
# Backup your .env file
cp .env .env.backup

# Remove virtual environment
rm -rf venv/

# Recreate
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Restore .env
cp .env.backup .env
```

---

## Platform-Specific Notes

### Linux

**Additional dependencies for PDF processing:**
```bash
sudo apt-get install libpoppler-dev
```

**For better performance:**
```bash
sudo apt-get install build-essential python3-dev
```

### Mac

**Install Xcode Command Line Tools:**
```bash
xcode-select --install
```

**If using M1/M2 Mac:**
- Everything should work natively
- If you encounter issues, ensure you're using ARM-compatible Python

### Windows

**Visual C++ Build Tools:**
Some packages require C++ compilation. If installation fails, install:
- Visual Studio Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/

**Long Path Support:**
Enable long path support in Windows 10/11:
1. Run PowerShell as Administrator
2. Execute: `New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force`
3. Restart computer

---

## Docker Installation (Advanced)

If you prefer Docker:

```bash
# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpoppler-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "api_server.py"]
EOF

# Build image
docker build -t education-rag .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/outputs:/app/outputs \
  -v $(pwd)/vectordb:/app/vectordb \
  -v $(pwd)/.env:/app/.env \
  education-rag
```

---

## Uninstallation

To completely remove the system:

```bash
# 1. Deactivate virtual environment
deactivate

# 2. Remove directory
cd ..
rm -rf education-rag-system

# 3. That's it! All dependencies were in the virtual environment
```

---

## Next Steps

After successful installation:

1. **Read the Quick Start Guide:** See [QUICK_START.md](QUICK_START.md)
2. **Upload your first PDF:** Copy a textbook to `uploads/` directory
3. **Process it:** Run the pipeline
4. **Generate content:** Try the examples

---

## Getting Help

If you encounter issues during installation:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Run `python scripts/test_system.py` to identify issues
3. Check the logs in `logs/` directory
4. Verify all steps were followed correctly

---

## Installation Checklist

Use this checklist to ensure everything is set up:

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created
- [ ] Anthropic API key added to `.env`
- [ ] System tests passed (`python scripts/test_system.py`)
- [ ] Embedding model downloaded
- [ ] Required directories exist (uploads, outputs, vectordb, logs)
- [ ] Can run example script
- [ ] API server starts successfully

---

**Installation complete! You're ready to start generating educational content! 🎉**

See [QUICK_START.md](QUICK_START.md) for your first steps.
