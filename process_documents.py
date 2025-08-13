import os
import sys
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document

# Load environment variables
load_dotenv()

class DocumentProcessor:
    def __init__(self):
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not found. Please set it in your .env file.")
        
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def load_documents(self, folder_path: str) -> List[Document]:
        """Load documents from the specified folder"""
        documents = []
        folder = Path(folder_path)
        
        if not folder.exists():
            raise FileNotFoundError(f"Folder {folder_path} not found")
        
        supported_extensions = {'.pdf', '.txt', '.docx'}
        
        for file_path in folder.iterdir():
            if file_path.suffix.lower() in supported_extensions:
                try:
                    print(f"Loading {file_path.name}...")
                    
                    if file_path.suffix.lower() == '.pdf':
                        loader = PyPDFLoader(str(file_path))
                    elif file_path.suffix.lower() == '.txt':
                        loader = TextLoader(str(file_path), encoding='utf-8')
                    elif file_path.suffix.lower() == '.docx':
                        loader = Docx2txtLoader(str(file_path))
                    
                    docs = loader.load()
                    
                    # Add metadata
                    for doc in docs:
                        doc.metadata.update({
                            'source': str(file_path),
                            'filename': file_path.name,
                            'file_type': file_path.suffix
                        })
                    
                    documents.extend(docs)
                    print(f"✅ Loaded {len(docs)} pages from {file_path.name}")
                    
                except Exception as e:
                    print(f"❌ Could not load {file_path.name}: {str(e)}")
        
        if not documents:
            raise ValueError("No documents were successfully loaded")
        
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks"""
        print("Splitting documents into chunks...")
        chunks = self.text_splitter.split_documents(documents)
        print(f"✅ Created {len(chunks)} chunks")
        return chunks
    
    def create_vector_store(self, chunks: List[Document]) -> FAISS:
        """Create and save FAISS vector store"""
        print("Creating vector embeddings...")
        
        # Create vector store
        vectorstore = FAISS.from_documents(chunks, self.embeddings)
        
        # Save to disk
        vectorstore.save_local("vectorstore")
        print("✅ Vector store saved to 'vectorstore' directory")
        
        return vectorstore

def main():
    """Main function to process documents"""
    print("🏛️ Ilocano Constitution Document Processor")
    print("=" * 50)
    
    try:
        # Check if data folder exists
        data_folder = Path("data")
        if not data_folder.exists():
            print("❌ 'data' folder not found!")
            print("Please create a 'data' folder and add your documents.")
            sys.exit(1)
        
        # Check if data folder has files
        files = list(data_folder.glob("*"))
        if not files:
            print("❌ No files found in 'data' folder!")
            print("Please add PDF, TXT, or DOCX files to the 'data' folder.")
            sys.exit(1)
        
        print(f"📁 Found {len(files)} files in data folder")
        
        # Initialize processor
        processor = DocumentProcessor()
        
        # Load documents
        documents = processor.load_documents("data")
        print(f"📄 Total documents loaded: {len(documents)}")
        
        # Split into chunks
        chunks = processor.split_documents(documents)
        
        # Create vector store
        vectorstore = processor.create_vector_store(chunks)
        
        print("\n🎉 Document processing completed successfully!")
        print("You can now run the Streamlit app: streamlit run app.py")
        
    except Exception as e:
        print(f"❌ Error processing documents: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()