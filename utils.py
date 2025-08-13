import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
from datetime import datetime

load_dotenv()

def check_openai_key():
    """Check if OpenAI API key is set"""
    return bool(os.getenv("OPENAI_API_KEY"))

def get_file_info(folder_path: str) -> dict:
    """Get information about files in the data folder"""
    folder = Path(folder_path)
    if not folder.exists():
        return {"total": 0, "files": [], "types": {}}
    
    files = list(folder.iterdir())
    file_types = {}
    
    for file in files:
        if file.is_file():
            ext = file.suffix.lower()
            file_types[ext] = file_types.get(ext, 0) + 1
    
    return {
        "total": len(files),
        "files": [f.name for f in files if f.is_file()],
        "types": file_types
    }

def format_sources(sources: list) -> str:
    """Format source documents for display"""
    if not sources:
        return "No sources found."
    
    formatted = "📚 **Sources:**\n"
    for i, source in enumerate(sources, 1):
        filename = source.metadata.get('filename', 'Unknown')
        formatted += f"{i}. {filename}\n"
    
    return formatted

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_filename = logs_dir / f"application_logs_{timestamp}.log"
    
    # Create logger for RAG system
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # Check if logger already has handlers to avoid duplicates
    if not logger.handlers:
        # Create file handler
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger