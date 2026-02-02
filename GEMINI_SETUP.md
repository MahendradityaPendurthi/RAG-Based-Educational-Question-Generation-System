# 🚀 FREE Gemini API Setup Guide

## Overview
Your Education RAG System now supports **Google's Gemini API** which is **100% FREE** for personal use! No more API credit issues.

## What Changed

### 1. **Switched from Anthropic (Claude) to Gemini (FREE!)**
   - Added support for Google's Gemini 1.5 Flash model
   - Keeps Anthropic support as optional (if you want to pay)
   - Default is now Gemini for free usage

### 2. **Made Everything Dynamic**
   - ❌ NO MORE hardcoded "Class 8 Mathematics" data
   - ✅ System automatically detects YOUR database content
   - ✅ Generates questions/flashcards from YOUR uploaded PDFs
   - ✅ All examples adapt to whatever data you have

### 3. **Smart Content Detection**
   - System scans your database to find:
     - Classes (5, 6, 7, 8, 9, 10)
     - Subjects (Math, Science, History, etc.)
     - Topics (from your PDFs)
   - Uses this info automatically - no manual configuration needed!

## 🔑 How to Get FREE Gemini API Key

1. **Go to Google AI Studio:**
   ```
   https://makersuite.google.com/app/apikey
   ```

2. **Sign in with your Google account**

3. **Click "Create API Key"**

4. **Copy your API key** (starts with `AIza...`)

5. **Add to your `.env` file:**
   ```bash
   # Open .env file and add:
   GEMINI_API_KEY=AIzaSy...your_key_here
   ```

That's it! The system is already configured to use Gemini by default.

## 📋 Your `.env` File Should Look Like This

```bash
# LLM Provider (gemini or anthropic)
LLM_PROVIDER=gemini

# API Keys
# Get free Gemini API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=AIzaSy...your_actual_key_here

# Anthropic API Configuration (optional, if using anthropic provider)
ANTHROPIC_API_KEY=sk-ant-api03-...

# Vector Database Configuration
VECTOR_DB_PATH=./vectordb
COLLECTION_NAME=educational_content

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# LLM Models
CLAUDE_MODEL=claude-sonnet-4-20250514
GEMINI_MODEL=gemini-2.5-flash

# Generation Settings
MAX_TOKENS=4000
TEMPERATURE=0.7

# Chunking Settings
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# API Server Settings
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

## 🎮 How to Use the System

### Quick Start

```bash
# Activate virtual environment
.\venv\Scripts\activate

# Run the dynamic example script
python scripts/example_usage.py
```

### What You'll See

```
======================================================================
EDUCATION RAG SYSTEM - DYNAMIC EXAMPLES
======================================================================

🎯 This system automatically detects your database content!
   No hardcoded data - everything is based on YOUR PDFs

✅ Database Status: 19 chunks found
   Classes: 6
   Subjects: Science

Available examples:
1. Process PDF & Add to Database
2. Generate MCQs (from YOUR data)
3. Generate Flashcards (from YOUR data)
4. Generate Notes (from YOUR data)
5. Generate Worksheet (from YOUR data)
6. Search Content
7. Database Stats
0. Run all examples

Enter example number (0-7):
```

### Example Workflow

1. **First Time? Add Your PDFs:**
   - Choose option `1` to process PDFs
   - System will find PDFs in `./uploads/` directory
   - Enter class number and subject when prompted

2. **Generate Study Materials:**
   - Choose option `2` for MCQs
   - Choose option `3` for Flashcards
   - Choose option `4` for Notes
   - System automatically uses YOUR PDF content!

3. **Search Your Content:**
   - Choose option `6` to search
   - System suggests queries based on your topics

## 🎯 Key Features

### 1. **Automatic Content Detection**
The system automatically discovers:
- Which classes you have content for
- Which subjects are in your database
- What topics are available
- Suggests relevant queries based on YOUR data

### 2. **Dynamic Question Generation**
```python
# System finds: Class 6 Science about "Temperature"
# Automatically generates:
📚 Found content in database:
   Classes: 6
   Subjects: Science
   Topics: Temperature, Weather, Air temperature

🎯 Generating 5 MCQs for:
   Class 6 | Science | Temperature
```

### 3. **Smart Search**
```python
🔍 Searching in: Class 6 Science
   Suggested query: What is Temperature?

Enter your search query (or press Enter for suggestion):
```

## 💰 Cost Comparison

| Provider | Free Tier | Cost After Free |
|----------|-----------|----------------|
| **Gemini 1.5 Flash** | ✅ 1500 requests/day FREE | Still very cheap |
| Anthropic Claude | ❌ No free tier | $3-15 per million tokens |

## 🔄 Switching Between Providers

Want to use Claude instead? Just change one line in `.env`:

```bash
# Use Gemini (FREE)
LLM_PROVIDER=gemini

# Or use Claude (paid)
LLM_PROVIDER=anthropic
```

## 📊 Your Current Database

You currently have:
- **19 chunks** of Class 6 Science content
- Topics include: Temperature, Weather, Air temperature
- Content types: definitions, examples, explanations, questions, formulas

## 🚨 Important Notes

1. **No More Hardcoded Data**: System adapts to whatever PDFs you upload
2. **Free API**: Gemini gives you 1500 requests/day for free
3. **Dynamic Examples**: All examples use YOUR actual content
4. **Search Works Offline**: Vector search doesn't need API (always free)

## 🎓 Next Steps

1. ✅ Get your free Gemini API key (link above)
2. ✅ Add it to `.env` file
3. ✅ Run `python scripts/example_usage.py`
4. ✅ Choose option 2 to generate MCQs from YOUR content!

## 📝 Testing Without API Key

Want to test without API key first?
- Option 6 (Search) works without any API!
- Option 7 (Database Stats) works without any API!

Try these first to see your content, then add API key for generation features.

## ❓ Troubleshooting

### "GEMINI_API_KEY not set"
- Make sure you added the key to `.env` file
- Check that `LLM_PROVIDER=gemini` is set in `.env`

### "No content in database"
- Run option 1 to process PDFs first
- Make sure PDFs are in `./uploads/` directory

### "Failed to send telemetry event"
- This is just a warning from ChromaDB telemetry
- Doesn't affect functionality - safe to ignore

## 🎉 Summary

You now have a **fully dynamic, FREE-to-use** education RAG system that:
- ✅ Uses free Gemini API
- ✅ Automatically detects your content
- ✅ Generates study materials from YOUR PDFs
- ✅ No hardcoded data anywhere

**Get your free API key and start generating!**
