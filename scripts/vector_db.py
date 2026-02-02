import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings as ChromaSettings
import logging
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path
import hashlib
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDB:
    def __init__(self, collection_name: str = None):
        """Initialize ChromaDB client and collection"""
        self.collection_name = collection_name or settings.collection_name
        
        logger.info(f"Initializing ChromaDB at {settings.vector_db_path}")
        
        # Create persistent client
        self.client = chromadb.PersistentClient(
            path=settings.vector_db_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding function
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=settings.embedding_model
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Loaded existing collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "Educational content for classes 5-10"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
    
    def add_chunks(self, chunks: List[Dict[str, Any]], batch_size: int = 100) -> int:
        """Add chunks to vector database in batches"""
        logger.info(f"Adding {len(chunks)} chunks to database in batches of {batch_size}")

        total_added = 0
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]

            documents = [chunk['content'] for chunk in batch]
            metadatas = [chunk['metadata'] for chunk in batch]

            # Generate unique IDs using filename, timestamp, and content hash
            ids = []
            for j, chunk in enumerate(batch):
                source_file = chunk['metadata'].get('source_file', 'unknown')
                filename = Path(source_file).stem  # Get filename without extension
                content_hash = hashlib.md5(chunk['content'].encode()).hexdigest()[:8]
                unique_id = f"{filename}_{timestamp}_{i+j}_{content_hash}"
                ids.append(unique_id)

            try:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                total_added += len(batch)

                if (i + batch_size) % 500 == 0:
                    logger.info(f"Progress: {total_added}/{len(chunks)} chunks added")

            except Exception as e:
                logger.error(f"Error adding batch {i}-{i+batch_size}: {str(e)}")
                continue

        logger.info(f"Successfully added {total_added} chunks to database")
        return total_added
    
    def search(
        self,
        query: str,
        n_results: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search for similar content in vector database"""

        # Build where filter conditions
        where_conditions = []
        if filters:
            if 'class' in filters:
                where_conditions.append({'class': filters['class']})
            if 'subject' in filters:
                where_conditions.append({'subject': filters['subject']})
            if 'topic' in filters:
                where_conditions.append({'topic': {'$contains': filters['topic']}})
            if 'content_type' in filters:
                if isinstance(filters['content_type'], list):
                    where_conditions.append({'content_type': {'$in': filters['content_type']}})
                else:
                    where_conditions.append({'content_type': filters['content_type']})
            if 'difficulty' in filters:
                where_conditions.append({'difficulty': filters['difficulty']})
            if 'chapter' in filters:
                where_conditions.append({'chapter': {'$contains': filters['chapter']}})

        # Combine conditions with $and if multiple conditions exist
        if len(where_conditions) > 1:
            where_filter = {'$and': where_conditions}
        elif len(where_conditions) == 1:
            where_filter = where_conditions[0]
        else:
            where_filter = None

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter if where_filter else None
            )

            logger.info(f"Search returned {len(results['documents'][0])} results")
            return results

        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            return {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            
            # Try to get a sample to analyze
            sample = self.collection.get(limit=1000)
            
            stats = {
                'total_chunks': count,
                'collection_name': self.collection_name
            }
            
            if sample and sample['metadatas']:
                metadatas = sample['metadatas']
                
                # Count by class
                classes = {}
                subjects = {}
                content_types = {}
                difficulties = {}
                
                for meta in metadatas:
                    # Classes
                    class_num = meta.get('class', 'Unknown')
                    classes[class_num] = classes.get(class_num, 0) + 1
                    
                    # Subjects
                    subject = meta.get('subject', 'Unknown')
                    subjects[subject] = subjects.get(subject, 0) + 1
                    
                    # Content types
                    content_type = meta.get('content_type', 'Unknown')
                    content_types[content_type] = content_types.get(content_type, 0) + 1
                    
                    # Difficulties
                    difficulty = meta.get('difficulty', 'Unknown')
                    difficulties[difficulty] = difficulties.get(difficulty, 0) + 1
                
                stats['by_class'] = classes
                stats['by_subject'] = subjects
                stats['by_content_type'] = content_types
                stats['by_difficulty'] = difficulties
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {'total_chunks': 0, 'error': str(e)}
    
    def delete_collection(self):
        """Delete the entire collection"""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
    
    def reset_database(self):
        """Reset the entire database"""
        try:
            self.client.reset()
            logger.info("Database reset successfully")
        except Exception as e:
            logger.error(f"Error resetting database: {str(e)}")

if __name__ == "__main__":
    # Test the vector database
    db = VectorDB()
    
    # Test adding sample data
    test_chunks = [
        {
            'content': 'The Pythagorean theorem states that in a right-angled triangle, the square of the hypotenuse equals the sum of squares of the other two sides.',
            'metadata': {
                'class': 8,
                'subject': 'Mathematics',
                'chapter': 'Triangles',
                'topic': 'Pythagorean Theorem',
                'content_type': 'definition',
                'difficulty': 'medium',
                'page': 15
            }
        },
        {
            'content': 'Example: If a=3 and b=4, then c² = 3² + 4² = 9 + 16 = 25, so c=5',
            'metadata': {
                'class': 8,
                'subject': 'Mathematics',
                'chapter': 'Triangles',
                'topic': 'Pythagorean Theorem',
                'content_type': 'example',
                'difficulty': 'easy',
                'page': 16
            }
        }
    ]
    
    # Add test data
    print("Adding test chunks...")
    count = db.add_chunks(test_chunks)
    print(f"Added {count} chunks")
    
    # Test search
    print("\nTesting search...")
    results = db.search(
        query="What is Pythagorean theorem?",
        filters={'class': 8, 'subject': 'Mathematics'},
        n_results=2
    )
    
    print(f"Found {len(results['documents'][0])} results:")
    for i, doc in enumerate(results['documents'][0]):
        print(f"\nResult {i+1}:")
        print(f"Content: {doc[:100]}...")
        print(f"Metadata: {results['metadatas'][0][i]}")
    
    # Get stats
    print("\nDatabase Statistics:")
    stats = db.get_collection_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
