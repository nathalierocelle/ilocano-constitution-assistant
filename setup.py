# setup.py - Run this file to setup the project structure
import os
from pathlib import Path

def create_project_structure():
    """Create the required project structure"""
    
    # Create directories
    directories = [
        "data",
        "vectorstore",
        ".streamlit"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Create .streamlit/config.toml for better UX
    config_content = """
[theme]
primaryColor = "#3b82f6"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8f9fa"
textColor = "#1f2937"

[server]
maxUploadSize = 200
"""
    
    with open(".streamlit/config.toml", "w") as f:
        f.write(config_content)
    print("✅ Created Streamlit config")
    
    # Create sample .env file
    env_content = """
# Copy this to .env and add your actual OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
"""
    
    with open(".env.example", "w") as f:
        f.write(env_content)
    print("✅ Created .env.example file")
    
    # Create README
    readme_content = """
# Ilocano Constitution RAG Chatbot

A RAG-powered chatbot that helps Filipino citizens understand their constitutional rights in Ilocano dialect.

## Setup Instructions

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up OpenAI API Key:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   Or create a `.env` file:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

3. **Add your documents:**
   - Place PDF, TXT, or DOCX files in the `data/` folder
   - Documents should contain constitutional content in English/Filipino

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

5. **Process documents:**
   - Click "Process Documents" in the sidebar
   - Wait for processing to complete
   - Start asking questions!

## Features

- 🏛️ Constitutional knowledge in Ilocano
- 🔍 Smart document retrieval using FAISS
- 💬 Natural conversation interface
- 🌐 Translation between Ilocano and English
- 📚 Source document citations

## Usage

Ask questions like:
- "Ania dagiti karbengan ti ciudadano?" (What are citizen rights?)
- "Maipanggep iti freedom of speech"
- "Constitutional rights ti mga tao"

The chatbot will respond in Ilocano with relevant constitutional information.
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    print("✅ Created README.md")
    
    print("\n🎉 Project structure created successfully!")
    print("\nNext steps:")
    print("1. Set your OPENAI_API_KEY environment variable")
    print("2. Add constitutional documents to the 'data' folder")
    print("3. Run: streamlit run app.py")

if __name__ == "__main__":
    create_project_structure()