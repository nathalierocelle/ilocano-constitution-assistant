import streamlit as st
import os
from pathlib import Path
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from rag_system import RAGSystem

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Ilocano Constitution Chatbot",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
    }
    .bot-message {
        background-color: #f5f5f5;
        margin-right: 2rem;
    }
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "rag_system" not in st.session_state:
        st.session_state.rag_system = None

@st.cache_resource
def load_rag_system():
    """Load and initialize the RAG system"""
    try:
        rag_system = RAGSystem()
        return rag_system
    except Exception as e:
        st.error(f"Error initializing RAG system: {str(e)}")
        return None

def display_sidebar():
    """Display sidebar with information"""
    
    # About App
    st.sidebar.header("ℹ️ Sino ak ngata? (Who am I?)")
    st.sidebar.markdown("""
    Siyak apo ni **Ilocano Constitution Chatbot**!
    
    Addaak ditoy tapno tulonganka a maawatan ti Konstitusion ti Pilipinas iti Ilocano. 
    Mabalinmo ti agsaludsod kadagiti kasta:

    * Ania dagiti karbengan ti umili? 
    * Maipanggep iti wayawaya ti panagsao 
    * Dagiti karbengan iti konstitusion dagiti tattao
    * Kasano ti aramid ti eleksion? 

    Mabalin ka nga agsaludsod iti Ilocano wenno English - sumungbatakto iti dua a pagsasao! 🏛️
    """)
    
    with st.sidebar.expander("📖 English Translation"):
        st.markdown("""
            I am **Ilocano Constitution Chatbot**!
            
            I'm here to help you understand the Philippine Constitution in Ilocano. 
            You can ask me questions like:

            * What are citizen rights?
            * About freedom of speech
            * Constitutional rights of people
            * How is the election process?
            
            Feel free to ask in Ilocano or English - I'll respond in both languages! 🏛️
        """)
        
    # Footer in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem 0; color: #666; font-size: 11px;">
        <p style="margin: 0;">Developed by 🐱 <strong>A.I.C.A.T.S.</strong></p>
        <p style="margin: 0;">(Artificial Intelligence for Constitutional Advancement via Translation Strategy)</p>
        <p style="margin: 5px 0 0 0;">© 2025</p>
    </div>
    """, unsafe_allow_html=True)

def display_chat_interface():
    """Display the main chat interface"""
    st.markdown('<div class="main-header"><h1>🏛️ Ilocano Constitution Chatbot</h1><p>Gayyem mo nga makatulong kenka iti Philippine Constitution (Your friend that will help you about Philippine Constitution)</p></div>', unsafe_allow_html=True)
    
    # Initialize RAG system if not already done
    if st.session_state.rag_system is None:
        st.session_state.rag_system = load_rag_system()
    
    if st.session_state.rag_system is None:
        st.error("Failed to initialize RAG system. Please check your setup.")
        st.stop()
    
    # Add welcome message if no messages exist
    if len(st.session_state.messages) == 0:
        welcome_message = {
            "role": "assistant", 
            "content": """👋 **Hello gayyemko! Anya ngay ti maitulong ko kenyam? (Hello friend! How can I help you?)**

        """
        }
        st.session_state.messages.append(welcome_message)
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Agsaludsod ka maipapan iti konstitusion... (Ask about the constitution...)"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            try:
                with st.spinner("Agpampanunot... (Thinking...)"):
                    response = st.session_state.rag_system.query(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"Error generating response: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})


def main():
    """Main application function"""
    initialize_session_state()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        st.error("🔑 Please set your OPENAI_API_KEY environment variable to use this application.")
        st.stop()
    
    # Display sidebar
    display_sidebar()
    
    # Display main chat interface
    display_chat_interface()


if __name__ == "__main__":
    main()
    