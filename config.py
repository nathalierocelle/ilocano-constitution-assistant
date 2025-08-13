import os
from pathlib import Path

# Configuration settings
class Config:
    # Paths
    DATA_FOLDER = "data"
    VECTORSTORE_PATH = "vectorstore"
    
    # Model settings
    OPENAI_MODEL = "gpt-4"
    EMBEDDING_MODEL = "text-embedding-ada-002"
    
    # Chunking settings
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Retrieval settings
    TOP_K = 5
    
    @staticmethod
    def ensure_directories():
        """Ensure required directories exist"""
        Path(Config.DATA_FOLDER).mkdir(exist_ok=True)
        Path(Config.VECTORSTORE_PATH).mkdir(exist_ok=True)