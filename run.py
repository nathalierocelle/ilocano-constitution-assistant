import os
import subprocess
import sys
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    issues = []
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        issues.append("❌ OPENAI_API_KEY environment variable not set")
    
    # Check if data folder exists and has files
    data_folder = Path("data")
    if not data_folder.exists():
        issues.append("❌ 'data' folder not found")
    elif not any(data_folder.iterdir()):
        issues.append("⚠️  'data' folder is empty - add some documents")
    
    # Check if requirements are installed
    try:
        import streamlit
        import langchain
        import openai
        import faiss
    except ImportError as e:
        issues.append(f"❌ Missing required package: {e.name}")
    
    return issues

def main():
    """Main function to run the application"""
    print("🏛️ Ilocano Constitution RAG Chatbot")
    print("=" * 40)
    
    # Check requirements
    issues = check_requirements()
    
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  {issue}")
        print("\nPlease fix these issues before running the application.")
        print("See README.md for setup instructions.")
        return
    
    print("✅ All requirements met!")
    print("🚀 Starting Streamlit application...")
    
    # Run Streamlit
    try:
        subprocess.run(["streamlit", "run", "app.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Error running Streamlit application")
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")

if __name__ == "__main__":
    main()