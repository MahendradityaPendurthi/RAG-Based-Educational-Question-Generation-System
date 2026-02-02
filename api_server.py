#!/usr/bin/env python3
"""
FastAPI server for Education RAG System
Provides REST API endpoints for content generation
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import sys
from pathlib import Path
import shutil
import logging
from datetime import datetime
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.content_generator import ContentGenerator
from scripts.pdf_parser import PDFParser
from scripts.vector_db import VectorDB
from config.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Education RAG API",
    description="API for generating educational content using RAG",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
generator = ContentGenerator()
pdf_parser = PDFParser()
vector_db = VectorDB()

# Pydantic models for request/response
class MCQRequest(BaseModel):
    class_num: int = Field(..., ge=5, le=10, description="Class number (5-10)")
    subject: str = Field(..., description="Subject name")
    topic: str = Field(..., description="Topic name")
    difficulty: str = Field("medium", description="Difficulty level: easy, medium, hard")
    num_questions: int = Field(10, ge=1, le=50, description="Number of questions")

class FlashcardRequest(BaseModel):
    class_num: int = Field(..., ge=5, le=10)
    subject: str
    topic: str
    num_cards: int = Field(20, ge=1, le=100)

class ShortNotesRequest(BaseModel):
    class_num: int = Field(..., ge=5, le=10)
    subject: str
    chapter: str

class WorksheetRequest(BaseModel):
    class_num: int = Field(..., ge=5, le=10)
    subject: str
    topics: List[str]
    difficulty: str = Field("medium")
    num_questions: int = Field(15, ge=5, le=50)

class ExamPaperRequest(BaseModel):
    class_num: int = Field(..., ge=5, le=10)
    subject: str
    chapters: List[str]
    total_marks: int = Field(100, ge=10, le=200)
    duration_minutes: int = Field(180, ge=30, le=300)

class PDFUploadResponse(BaseModel):
    success: bool
    message: str
    filename: str
    chunks_extracted: int

# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Education RAG API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Database statistics endpoint
@app.get("/api/stats")
async def get_stats():
    """Get vector database statistics"""
    try:
        stats = vector_db.get_collection_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Upload PDF endpoint
@app.post("/api/upload-pdf", response_model=PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    class_num: int = Form(...),
    subject: str = Form(...)
):
    """Upload and process a PDF textbook"""
    try:
        # Save uploaded file
        upload_dir = Path(settings.uploads_path)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / f"{class_num}_{subject}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Uploaded file saved: {file_path}")
        
        # Process PDF
        chunks = pdf_parser.parse_pdf(str(file_path), class_num, subject)
        
        # Add to vector database
        added = vector_db.add_chunks(chunks)
        
        return PDFUploadResponse(
            success=True,
            message=f"Successfully processed and added to database",
            filename=file.filename,
            chunks_extracted=added
        )
        
    except Exception as e:
        logger.error(f"Error uploading PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# MCQ generation endpoint
@app.post("/api/generate/mcq")
async def generate_mcq(request: MCQRequest):
    """Generate MCQ questions"""
    try:
        logger.info(f"Generating MCQs: {request}")
        
        mcqs = generator.generate_mcq(
            class_num=request.class_num,
            subject=request.subject,
            topic=request.topic,
            difficulty=request.difficulty,
            num_questions=request.num_questions
        )
        
        # Save to outputs
        output_file = Path(settings.outputs_path) / f"mcq_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(mcqs)
        
        return {
            "success": True,
            "content": mcqs,
            "output_file": str(output_file),
            "metadata": {
                "class": request.class_num,
                "subject": request.subject,
                "topic": request.topic,
                "difficulty": request.difficulty,
                "num_questions": request.num_questions
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating MCQs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Flashcard generation endpoint
@app.post("/api/generate/flashcards")
async def generate_flashcards(request: FlashcardRequest):
    """Generate flashcards"""
    try:
        logger.info(f"Generating flashcards: {request}")
        
        flashcards = generator.generate_flashcards(
            class_num=request.class_num,
            subject=request.subject,
            topic=request.topic,
            num_cards=request.num_cards
        )
        
        # Save to outputs
        output_file = Path(settings.outputs_path) / f"flashcards_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(flashcards, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "flashcards": flashcards,
            "count": len(flashcards),
            "output_file": str(output_file)
        }
        
    except Exception as e:
        logger.error(f"Error generating flashcards: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Short notes generation endpoint
@app.post("/api/generate/notes")
async def generate_notes(request: ShortNotesRequest):
    """Generate short notes"""
    try:
        logger.info(f"Generating notes: {request}")
        
        notes = generator.generate_short_notes(
            class_num=request.class_num,
            subject=request.subject,
            chapter=request.chapter
        )
        
        # Save to outputs
        output_file = Path(settings.outputs_path) / f"notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(notes)
        
        return {
            "success": True,
            "content": notes,
            "output_file": str(output_file)
        }
        
    except Exception as e:
        logger.error(f"Error generating notes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Worksheet generation endpoint
@app.post("/api/generate/worksheet")
async def generate_worksheet(request: WorksheetRequest):
    """Generate worksheet"""
    try:
        logger.info(f"Generating worksheet: {request}")
        
        worksheet = generator.generate_worksheet(
            class_num=request.class_num,
            subject=request.subject,
            topics=request.topics,
            difficulty=request.difficulty,
            num_questions=request.num_questions
        )
        
        # Save to outputs
        output_file = Path(settings.outputs_path) / f"worksheet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(worksheet)
        
        return {
            "success": True,
            "content": worksheet,
            "output_file": str(output_file)
        }
        
    except Exception as e:
        logger.error(f"Error generating worksheet: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Exam paper generation endpoint
@app.post("/api/generate/exam")
async def generate_exam(request: ExamPaperRequest):
    """Generate exam paper"""
    try:
        logger.info(f"Generating exam paper: {request}")
        
        exam_paper = generator.generate_exam_paper(
            class_num=request.class_num,
            subject=request.subject,
            chapters=request.chapters,
            total_marks=request.total_marks,
            duration_minutes=request.duration_minutes
        )
        
        # Save to outputs
        output_file = Path(settings.outputs_path) / f"exam_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(exam_paper)
        
        return {
            "success": True,
            "content": exam_paper,
            "output_file": str(output_file),
            "metadata": {
                "total_marks": request.total_marks,
                "duration": request.duration_minutes
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating exam paper: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Search content endpoint
@app.get("/api/search")
async def search_content(
    query: str,
    class_num: Optional[int] = None,
    subject: Optional[str] = None,
    topic: Optional[str] = None,
    n_results: int = 10
):
    """Search for content in vector database"""
    try:
        filters = {}
        if class_num:
            filters['class'] = class_num
        if subject:
            filters['subject'] = subject
        if topic:
            filters['topic'] = topic
        
        results = vector_db.search(
            query=query,
            filters=filters if filters else None,
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })
        
        return {
            "success": True,
            "query": query,
            "results": formatted_results,
            "count": len(formatted_results)
        }
        
    except Exception as e:
        logger.error(f"Error searching content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Download file endpoint
@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download generated content file"""
    try:
        file_path = Path(settings.outputs_path) / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    print("="*70)
    print("Education RAG API Server")
    print("="*70)
    print(f"Starting server at http://{settings.api_host}:{settings.api_port}")
    print(f"API Documentation: http://{settings.api_host}:{settings.api_port}/docs")
    print("="*70)
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level="info"
    )
