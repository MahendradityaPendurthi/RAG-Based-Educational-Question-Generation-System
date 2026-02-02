import logging
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config.config import settings
from scripts.vector_db import VectorDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentGenerator:
    def __init__(self):
        """Initialize LLM client and vector database"""
        self.llm_provider = settings.llm_provider.lower()
        self.vector_db = VectorDB()

        if self.llm_provider == "gemini":
            if not settings.gemini_api_key:
                raise ValueError("GEMINI_API_KEY not set in environment variables")
            import google.generativeai as genai
            genai.configure(api_key=settings.gemini_api_key)
            self.client = genai.GenerativeModel(settings.gemini_model)
            logger.info(f"Content generator initialized with Gemini ({settings.gemini_model})")
        elif self.llm_provider == "anthropic":
            if not settings.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY not set in environment variables")
            import anthropic
            self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            logger.info(f"Content generator initialized with Claude ({settings.claude_model})")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}. Use 'gemini' or 'anthropic'")

    def _call_llm(self, prompt: str, max_tokens: int = None) -> str:
        """Call LLM API with error handling"""
        try:
            if self.llm_provider == "gemini":
                # Gemini API call
                response = self.client.generate_content(
                    prompt,
                    generation_config={
                        "temperature": settings.temperature,
                        "max_output_tokens": max_tokens or settings.max_tokens,
                    }
                )
                return response.text
            elif self.llm_provider == "anthropic":
                # Claude API call
                response = self.client.messages.create(
                    model=settings.claude_model,
                    max_tokens=max_tokens or settings.max_tokens,
                    temperature=settings.temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
        except Exception as e:
            logger.error(f"Error calling {self.llm_provider.upper()} API: {str(e)}")
            raise

    def generate_mcq(
        self,
        class_num: int,
        subject: str,
        topic: str,
        difficulty: str = "medium",
        num_questions: int = 10
    ) -> str:
        """Generate MCQ questions (ONLY from real PDF data)"""
        logger.info(f"Generating {num_questions} MCQs for Class {class_num} {subject} - {topic} ({difficulty})")

        # Retrieve relevant content from real PDFs only
        # For large question sets (50+), retrieve more chunks for better coverage
        query = f"{topic} concepts definitions examples formulas"
        n_chunks = max(50, num_questions * 3)  # At least 50 chunks or 3x questions
        results = self.vector_db.search(
            query=query,
            filters={
                'class': class_num,
                'subject': subject
            },
            n_results=n_chunks
        )

        # Filter out test data - keep only real PDF content
        real_docs = []
        real_metas = []
        if results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i] if i < len(results['metadatas'][0]) else {}
                source_file = meta.get('source_file', '')
                subject_meta = meta.get('subject', '')

                # Only use content from actual PDFs
                if source_file and subject_meta != 'Test' and 'test' not in subject_meta.lower():
                    real_docs.append(doc)
                    real_metas.append(meta)

        if not real_docs:
            logger.warning("No relevant content found in database from real PDFs")
            raise ValueError(f"No content found for Class {class_num} {subject}. Please upload relevant PDFs first.")

        # Use more context for larger question sets
        context_limit = min(30, max(15, num_questions // 2))  # Scale context with question count
        context_chunks = real_docs[:context_limit]
        context = "\n\n".join([f"[Context {i+1}]: {chunk}" for i, chunk in enumerate(context_chunks)])

        prompt = f"""You are an expert educational content creator for Class {class_num} {subject}.

RETRIEVED TEXTBOOK CONTENT:
{context}

TASK: Create {num_questions} multiple-choice questions (MCQs) about {topic}.

REQUIREMENTS:
- Difficulty level: {difficulty}
- Each question must have exactly 4 options (A, B, C, D)
- Only ONE option should be correct
- Questions should test understanding and application, not just memorization
- Base all questions on the provided textbook content above
- Make questions clear and unambiguous
- Ensure wrong options are plausible but clearly incorrect
- Include variety: some conceptual, some numerical, some application-based

FORMAT (strictly follow this):
Question 1: [Clear, specific question text]
A) [First option]
B) [Second option]
C) [Third option]
D) [Fourth option]
Correct Answer: [A/B/C/D]
Explanation: [Brief 1-2 sentence explanation of why this is correct]

[Blank line between questions]

Generate all {num_questions} questions now following this exact format:"""

        # Use max_tokens from settings (default 8000 for 50+ questions)
        response = self._call_llm(prompt, max_tokens=settings.max_tokens)
        return response

    def generate_fill_blanks(
        self,
        class_num: int,
        subject: str,
        topic: str,
        num_questions: int = 20,
        difficulty: str = "medium"
    ) -> str:
        """Generate fill in the blanks questions (ONLY from real PDF data)"""
        logger.info(f"Generating {num_questions} {difficulty} fill in the blanks for Class {class_num} {subject} - {topic}")

        # Retrieve relevant content from real PDFs only
        query = f"{topic} definitions concepts key terms important facts"
        n_chunks = max(40, num_questions * 2)
        results = self.vector_db.search(
            query=query,
            filters={
                'class': class_num,
                'subject': subject
            },
            n_results=n_chunks
        )

        # Filter out test data - keep only real PDF content
        real_docs = []
        if results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i] if i < len(results['metadatas'][0]) else {}
                source_file = meta.get('source_file', '')
                subject_meta = meta.get('subject', '')

                if source_file and subject_meta != 'Test' and 'test' not in subject_meta.lower():
                    real_docs.append(doc)

        if not real_docs:
            raise ValueError(f"No content found for Class {class_num} {subject}. Please upload relevant PDFs first.")

        context_limit = min(25, max(15, num_questions // 2))
        context_chunks = real_docs[:context_limit]
        context = "\n\n".join([f"[Context {i+1}]: {chunk}" for i, chunk in enumerate(context_chunks)])

        prompt = f"""You are an expert educational content creator for Class {class_num} {subject}.

RETRIEVED TEXTBOOK CONTENT:
{context}

TASK: Create {num_questions} fill in the blanks questions about {topic}.

REQUIREMENTS:
- Difficulty level: {difficulty}
- Base all questions on the provided textbook content above
- Each question should have ONE blank marked with ________
- The blank should test key concepts, terms, or important facts
- Provide the correct answer after each question
- Questions must be UNIQUE and not repeat the same concept
- Make questions clear and unambiguous
- Include variety: definitions, facts, concepts, and relationships
- {difficulty} difficulty means: {"basic recall" if difficulty == "easy" else "moderate understanding" if difficulty == "medium" else "deep analysis"}

FORMAT (strictly follow this):
1. [Statement with ________ representing the blank]
   Answer: [Correct word/phrase]

2. [Statement with ________ representing the blank]
   Answer: [Correct word/phrase]

Generate all {num_questions} UNIQUE fill in the blanks questions now:"""

        response = self._call_llm(prompt, max_tokens=settings.max_tokens)
        return response

    def generate_short_answer_questions(
        self,
        class_num: int,
        subject: str,
        topic: str,
        num_questions: int = 20,
        difficulty: str = "medium"
    ) -> str:
        """Generate short answer questions ONLY (no answers) from real PDF data"""
        logger.info(f"Generating {num_questions} {difficulty} short answer questions for Class {class_num} {subject} - {topic}")

        # Retrieve relevant content from real PDFs only
        query = f"{topic} concepts explanations applications why how"
        n_chunks = max(40, num_questions * 2)
        results = self.vector_db.search(
            query=query,
            filters={
                'class': class_num,
                'subject': subject
            },
            n_results=n_chunks
        )

        # Filter out test data
        real_docs = []
        if results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i] if i < len(results['metadatas'][0]) else {}
                source_file = meta.get('source_file', '')
                subject_meta = meta.get('subject', '')

                if source_file and subject_meta != 'Test' and 'test' not in subject_meta.lower():
                    real_docs.append(doc)

        if not real_docs:
            raise ValueError(f"No content found for Class {class_num} {subject}. Please upload relevant PDFs first.")

        context_limit = min(25, max(15, num_questions // 2))
        context_chunks = real_docs[:context_limit]
        context = "\n\n".join([f"[Context {i+1}]: {chunk}" for i, chunk in enumerate(context_chunks)])

        prompt = f"""You are an expert educational content creator for Class {class_num} {subject}.

RETRIEVED TEXTBOOK CONTENT:
{context}

TASK: Create {num_questions} short answer questions about {topic}.

REQUIREMENTS:
- Difficulty level: {difficulty}
- Base all questions on the provided textbook content above
- Each question should require 2-3 sentences to answer (50-80 words)
- Questions should test understanding, not just recall
- Questions must be UNIQUE and cover different aspects of the topic
- Use question words: What, Why, How, Explain, Describe, Define
- DO NOT provide answers - only questions
- Make questions clear and specific
- {difficulty} difficulty means: {"simple recall" if difficulty == "easy" else "application of concepts" if difficulty == "medium" else "analysis and evaluation"}

FORMAT (strictly follow this):
1. [Clear, specific question]

2. [Clear, specific question]

3. [Clear, specific question]

Generate all {num_questions} UNIQUE short answer questions now (QUESTIONS ONLY, NO ANSWERS):"""

        response = self._call_llm(prompt, max_tokens=settings.max_tokens)
        return response

    def generate_long_answer_questions(
        self,
        class_num: int,
        subject: str,
        topic: str,
        num_questions: int = 20,
        difficulty: str = "medium"
    ) -> str:
        """Generate long answer questions ONLY (no answers) from real PDF data"""
        logger.info(f"Generating {num_questions} {difficulty} long answer questions for Class {class_num} {subject} - {topic}")

        # Retrieve relevant content from real PDFs only
        query = f"{topic} detailed explanations applications analysis evaluation"
        n_chunks = max(40, num_questions * 2)
        results = self.vector_db.search(
            query=query,
            filters={
                'class': class_num,
                'subject': subject
            },
            n_results=n_chunks
        )

        # Filter out test data
        real_docs = []
        if results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i] if i < len(results['metadatas'][0]) else {}
                source_file = meta.get('source_file', '')
                subject_meta = meta.get('subject', '')

                if source_file and subject_meta != 'Test' and 'test' not in subject_meta.lower():
                    real_docs.append(doc)

        if not real_docs:
            raise ValueError(f"No content found for Class {class_num} {subject}. Please upload relevant PDFs first.")

        context_limit = min(30, max(20, num_questions // 2))
        context_chunks = real_docs[:context_limit]
        context = "\n\n".join([f"[Context {i+1}]: {chunk}" for i, chunk in enumerate(context_chunks)])

        prompt = f"""You are an expert educational content creator for Class {class_num} {subject}.

RETRIEVED TEXTBOOK CONTENT:
{context}

TASK: Create {num_questions} long answer questions about {topic}.

REQUIREMENTS:
- Difficulty level: {difficulty}
- Base all questions on the provided textbook content above
- Each question should require detailed answers (150-200 words or more)
- Questions should test deep understanding, analysis, and application
- Questions must be UNIQUE and cover different major aspects
- Use prompts like: Explain in detail, Describe with examples, Analyze, Compare and contrast, Evaluate, Discuss
- DO NOT provide answers - only questions
- Make questions comprehensive and thought-provoking
- {difficulty} difficulty means: {"straightforward explanations" if difficulty == "easy" else "connections and applications" if difficulty == "medium" else "critical thinking and synthesis"}

FORMAT (strictly follow this):
1. [Comprehensive, detailed question]

2. [Comprehensive, detailed question]

3. [Comprehensive, detailed question]

Generate all {num_questions} UNIQUE long answer questions now (QUESTIONS ONLY, NO ANSWERS):"""

        response = self._call_llm(prompt, max_tokens=settings.max_tokens)
        return response

    def generate_very_short_answer_questions(
        self,
        class_num: int,
        subject: str,
        topic: str,
        num_questions: int = 20,
        difficulty: str = "medium"
    ) -> str:
        """Generate very short answer questions ONLY (no answers) from real PDF data"""
        logger.info(f"Generating {num_questions} {difficulty} very short answer questions for Class {class_num} {subject} - {topic}")

        # Retrieve relevant content from real PDFs only
        query = f"{topic} terms definitions facts key points"
        n_chunks = max(40, num_questions * 2)
        results = self.vector_db.search(
            query=query,
            filters={
                'class': class_num,
                'subject': subject
            },
            n_results=n_chunks
        )

        # Filter out test data
        real_docs = []
        if results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i] if i < len(results['metadatas'][0]) else {}
                source_file = meta.get('source_file', '')
                subject_meta = meta.get('subject', '')

                if source_file and subject_meta != 'Test' and 'test' not in subject_meta.lower():
                    real_docs.append(doc)

        if not real_docs:
            raise ValueError(f"No content found for Class {class_num} {subject}. Please upload relevant PDFs first.")

        context_limit = min(25, max(15, num_questions // 2))
        context_chunks = real_docs[:context_limit]
        context = "\n\n".join([f"[Context {i+1}]: {chunk}" for i, chunk in enumerate(context_chunks)])

        prompt = f"""You are an expert educational content creator for Class {class_num} {subject}.

RETRIEVED TEXTBOOK CONTENT:
{context}

TASK: Create {num_questions} very short answer questions about {topic}.

REQUIREMENTS:
- Difficulty level: {difficulty}
- Base all questions on the provided textbook content above
- Each question should require 1-2 word or one sentence answers (10-20 words max)
- Questions should be direct and specific
- Questions must be UNIQUE and not repeat concepts
- Focus on: definitions, names, terms, simple facts, dates, formulas
- DO NOT provide answers - only questions
- Make questions clear and concise
- {difficulty} difficulty means: {"common terms" if difficulty == "easy" else "moderate vocabulary" if difficulty == "medium" else "specialized terminology"}

FORMAT (strictly follow this):
1. [Brief, specific question]

2. [Brief, specific question]

3. [Brief, specific question]

Generate all {num_questions} UNIQUE very short answer questions now (QUESTIONS ONLY, NO ANSWERS):"""

        response = self._call_llm(prompt, max_tokens=settings.max_tokens)
        return response

    def generate_flashcards(
        self,
        class_num: int,
        subject: str,
        topic: str,
        num_cards: int = 20
    ) -> List[Dict[str, str]]:
        """Generate flashcards (ONLY from real PDF data)"""
        logger.info(f"Generating {num_cards} flashcards for Class {class_num} {subject} - {topic}")

        # Retrieve definitions and formulas from real PDFs only
        query = f"{topic} definitions key terms formulas rules theorems"
        results = self.vector_db.search(
            query=query,
            filters={
                'class': class_num,
                'subject': subject
            },
            n_results=30
        )

        # Filter out test data
        real_docs = []
        if results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i] if i < len(results['metadatas'][0]) else {}
                source_file = meta.get('source_file', '')
                subject_meta = meta.get('subject', '')

                # Only use content from actual PDFs
                if source_file and subject_meta != 'Test' and 'test' not in subject_meta.lower():
                    real_docs.append(doc)

        if not real_docs:
            raise ValueError(f"No content found for Class {class_num} {subject}. Please upload relevant PDFs first.")

        context = "\n\n".join(real_docs[:20])

        prompt = f"""Based on this Class {class_num} {subject} content about {topic}:

{context}

Create {num_cards} flashcards for students to study.

Each flashcard should have:
- Front: A clear, specific question or term
- Back: Complete but concise answer or definition
- Hint (optional): A helpful memory aid or connection

Return as a JSON array in this exact format:
{{
  "flashcards": [
    {{
      "front": "What is the Pythagorean theorem?",
      "back": "In a right triangle, a² + b² = c² where c is the hypotenuse",
      "hint": "Think: 3-4-5 triangle"
    }}
  ]
}}

Generate all {num_cards} flashcards now:"""

        response = self._call_llm(prompt, max_tokens=settings.max_tokens)

        # Parse JSON response
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            return data.get('flashcards', [])
        except Exception as e:
            logger.error(f"Error parsing flashcards JSON: {str(e)}")
            return []

    def generate_short_notes(
        self,
        class_num: int,
        subject: str,
        chapter: str
    ) -> str:
        """Generate concise revision notes for a chapter (ONLY from real PDF data)"""
        logger.info(f"Generating short notes for Class {class_num} {subject} - {chapter}")

        query = f"{chapter} key concepts main points important topics"
        results = self.vector_db.search(
            query=query,
            filters={
                'class': class_num,
                'subject': subject
            },
            n_results=50
        )

        # Filter out test data
        real_docs = []
        if results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i] if i < len(results['metadatas'][0]) else {}
                source_file = meta.get('source_file', '')
                subject_meta = meta.get('subject', '')

                # Only use content from actual PDFs
                if source_file and subject_meta != 'Test' and 'test' not in subject_meta.lower():
                    real_docs.append(doc)

        if not real_docs:
            raise ValueError(f"No content found for Class {class_num} {subject}. Please upload relevant PDFs first.")

        context = "\n\n".join(real_docs)

        prompt = f"""Create comprehensive but concise revision notes for Class {class_num} students.

CHAPTER CONTENT:
{context}

Create structured notes covering:

1. KEY CONCEPTS (3-5 main ideas with brief explanations)
2. IMPORTANT DEFINITIONS (key terms with clear definitions)
3. FORMULAS & THEOREMS (list all important formulas)
4. QUICK TIPS (exam tips and memory aids)
5. COMMON MISTAKES (typical errors students make)

Keep it focused and exam-oriented. Maximum 2 pages. Use bullet points where appropriate.

Generate the complete notes now:"""

        response = self._call_llm(prompt, max_tokens=settings.max_tokens)
        return response

    def generate_worksheet(
        self,
        class_num: int,
        subject: str,
        topics: List[str],
        difficulty: str = "medium",
        num_questions: int = 15
    ) -> str:
        """Generate a mixed worksheet covering multiple topics"""
        logger.info(f"Generating worksheet: {num_questions} questions covering {len(topics)} topics")

        all_questions = []
        questions_per_topic = max(1, num_questions // len(topics))

        for topic in topics:
            mcqs = self.generate_mcq(
                class_num=class_num,
                subject=subject,
                topic=topic,
                difficulty=difficulty,
                num_questions=questions_per_topic
            )
            all_questions.append(mcqs)

        # Combine all questions
        worksheet = f"""
{'='*60}
WORKSHEET - CLASS {class_num} {subject.upper()}
Difficulty: {difficulty.upper()}
Total Questions: {num_questions}
Topics: {', '.join(topics)}
{'='*60}

Instructions:
- Answer all questions
- Each question carries equal marks
- Select the most appropriate answer from the given options

{'='*60}

"""
        worksheet += "\n\n".join(all_questions)
        worksheet += f"\n\n{'='*60}\nEND OF WORKSHEET\n{'='*60}"

        return worksheet

    def generate_exam_paper(
        self,
        class_num: int,
        subject: str,
        chapters: List[str],
        total_marks: int = 100,
        duration_minutes: int = 180
    ) -> str:
        """Generate a complete exam paper"""
        logger.info(f"Generating exam paper for Class {class_num} {subject}")

        # Distribute marks across difficulty levels
        easy_marks = int(total_marks * 0.3)
        medium_marks = int(total_marks * 0.5)
        hard_marks = total_marks - easy_marks - medium_marks

        exam_paper = f"""
{'='*70}
CLASS {class_num} - {subject.upper()}
EXAMINATION PAPER
{'='*70}

Time Allowed: {duration_minutes} minutes
Maximum Marks: {total_marks}

General Instructions:
1. All questions are compulsory
2. The paper consists of sections with varying difficulty levels
3. Read each question carefully before answering
4. Write your answers neatly and legibly

{'='*70}

"""

        # Section A - Easy questions (30% marks)
        exam_paper += f"\nSECTION A - EASY ({easy_marks} marks)\n"
        exam_paper += "="*70 + "\n\n"

        easy_questions = self.generate_mcq(
            class_num=class_num,
            subject=subject,
            topic=chapters[0] if chapters else "General",
            difficulty="easy",
            num_questions=int(easy_marks / 2)
        )
        exam_paper += easy_questions + "\n\n"

        # Section B - Medium questions (50% marks)
        exam_paper += f"\nSECTION B - MEDIUM ({medium_marks} marks)\n"
        exam_paper += "="*70 + "\n\n"

        medium_questions = self.generate_mcq(
            class_num=class_num,
            subject=subject,
            topic=chapters[0] if chapters else "General",
            difficulty="medium",
            num_questions=int(medium_marks / 3)
        )
        exam_paper += medium_questions + "\n\n"

        # Section C - Hard questions (20% marks)
        exam_paper += f"\nSECTION C - HARD ({hard_marks} marks)\n"
        exam_paper += "="*70 + "\n\n"

        hard_questions = self.generate_mcq(
            class_num=class_num,
            subject=subject,
            topic=chapters[0] if chapters else "General",
            difficulty="hard",
            num_questions=int(hard_marks / 5)
        )
        exam_paper += hard_questions + "\n\n"

        exam_paper += "="*70 + "\nEND OF EXAMINATION\n" + "="*70

        return exam_paper

if __name__ == "__main__":
    # Test the content generator
    try:
        generator = ContentGenerator()

        print("Testing MCQ generation...")
        mcqs = generator.generate_mcq(
            class_num=6,
            subject="Science",
            topic="Temperature",
            difficulty="easy",
            num_questions=3
        )
        print("\nGenerated MCQs:")
        print(mcqs)

        print("\n" + "="*70)
        print("Testing flashcard generation...")
        flashcards = generator.generate_flashcards(
            class_num=6,
            subject="Science",
            topic="Temperature",
            num_cards=5
        )
        print(f"\nGenerated {len(flashcards)} flashcards")
        if flashcards:
            print("\nSample flashcard:")
            print(f"Front: {flashcards[0].get('front', 'N/A')}")
            print(f"Back: {flashcards[0].get('back', 'N/A')}")

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have:")
        print("1. Set GEMINI_API_KEY or ANTHROPIC_API_KEY in .env file")
        print("2. Set LLM_PROVIDER to 'gemini' or 'anthropic' in .env file")
        print("3. Added some content to the vector database")
