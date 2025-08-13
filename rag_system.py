# rag_system.py
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, END, START
from typing_extensions import TypedDict
from utils import setup_logging

logger = setup_logging()

# Load environment variables
load_dotenv()

class GraphState(TypedDict):
    """State for the graph"""
    query: str
    translated_query: str
    context: str
    answer: str
    source_docs: List[Any]

class RAGSystem:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-4.1",
            temperature=0,  # Lower temperature to reduce randomness
            max_tokens=1000, # Limit response length
            top_p=0.9         # Reduce probability mass for more focused responses
        )
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = None
        self.retriever = None
        self.load_vectorstore()
        self.setup_prompt_templates()
        self.setup_graph()
    
    def load_vectorstore(self):
        """Load the FAISS vector store"""
        try:
            if os.path.exists("vectorstore"):
                self.vectorstore = FAISS.load_local(
                    "vectorstore", 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
                self.retriever = self.vectorstore.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 5}
                )
                logger.info("Vector store loaded successfully")
            else:
                logger.error("Vector store not found. Please run process_documents.py first.")
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
    
    def setup_prompt_templates(self):
        """Setup prompt templates for different stages"""
        self.translation_prompt = PromptTemplate(
            input_variables=["query", "language"],
            template="""
            You are an expert translator specializing in Philippine constitutional law and Ilocano language.
            
            Translate the following query into English if it's in Ilocano, or identify if it's already in English:
            Query: {query}
            Target Language: {language}
            
            If the query is in Ilocano, provide an accurate English translation.
            If the query is already in English, return it as-is.
            
            Translation:
            """
        )
        
        self.rag_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
            You are an expert on Philippine Constitutional Law with deep knowledge of Ilocano culture and language.
            Your role is to help Filipino citizens understand their constitutional rights in Ilocano dialect.
            
            Use the following constitutional documents as context to answer the question:
            {context}
            
            Question: {question}
            
            Instructions:
            1. Answer primarily in Ilocano (Ilokano) dialect
            2. Use simple, accessible language that ordinary citizens can understand
            3. Include relevant constitutional articles or sections
            4. Explain legal concepts using familiar Ilocano cultural references when appropriate
            5. If translating legal terms, provide both Ilocano and English versions
            6. Be accurate and cite specific constitutional provisions when possible
            7. Keep your response concise and avoid repetition
            8. Provide a single, clear explanation without repeating the same information multiple times
            9. ALWAYS provide an English translation after your Ilocano response
            
            Format your response exactly like this:
            
            **Ilocano:**
            [Your response in Ilocano here]
            
            **English Translation:**
            [Complete English translation of your Ilocano response here]
            
            Provide ONE clear, concise answer:
            """
        )
    
    def translate_node(self, state: GraphState) -> GraphState:
        """Node to handle translation if needed"""
        query = state["query"]
        
        # Enhanced Ilocano detection with more indicators
        ilocano_indicators = [
            "ti", "iti", "dagiti", "kadagiti", "ken", "wenno", "ania", "sadino", 
            "kasano", "apay", "kayat", "mabalin", "saan", "adda", "awan",
            "agsaludsod", "maipapan", "konstitusion"
        ]
        is_ilocano = any(indicator in query.lower() for indicator in ilocano_indicators)
        
        if is_ilocano:
            try:
                translation_chain = self.translation_prompt | self.llm
                translated = translation_chain.invoke({
                    "query": query,
                    "language": "English"
                })
                state["translated_query"] = translated.content.strip()
                logger.info(f"Translated: '{query}' -> '{state['translated_query']}'")
            except Exception as e:
                logger.error(f"Translation error: {str(e)}")
                state["translated_query"] = query
        else:
            state["translated_query"] = query
        
        return state
    
    def retrieve_node(self, state: GraphState) -> GraphState:
        """Node to retrieve relevant documents"""
        if self.retriever:
            try:
                docs = self.retriever.invoke(state["translated_query"])
                state["context"] = "\n\n".join([doc.page_content for doc in docs])
                state["source_docs"] = docs
                logger.info(f"Retrieved {len(docs)} relevant documents")
            except Exception as e:
                logger.error(f"Retrieval error: {str(e)}")
                state["context"] = "Error retrieving documents."
                state["source_docs"] = []
        else:
            state["context"] = "No documents available. Please run process_documents.py first."
            state["source_docs"] = []
        
        return state
    
    def generate_node(self, state: GraphState) -> GraphState:
        """Node to generate the final answer"""
        try:
            generation_chain = self.rag_prompt | self.llm
            response = generation_chain.invoke({
                "context": state["context"],
                "question": state["query"]
            })
            logger.info(f"Agent response: {response.content}")
            state["answer"] = response.content
            logger.info("Generated response successfully")
        except Exception as e:
            logger.error(f"Generation error: {str(e)}")
            state["answer"] = f"Error generating response: {str(e)}"
        
        return state
    
    def setup_graph(self):
        """Setup LangGraph workflow"""
        # Create the state graph with proper schema
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("translate", self.translate_node)
        workflow.add_node("retrieve", self.retrieve_node)
        workflow.add_node("generate", self.generate_node)
        
        # Set entry point using START
        workflow.add_edge(START, "translate")
        
        # Add edges between nodes
        workflow.add_edge("translate", "retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)
        
        # Compile the graph
        self.app = workflow.compile()
        logger.info("LangGraph workflow compiled successfully")
    
    def query(self, question: str) -> str:
        """Process a query through the RAG system"""
        try:
            if not self.retriever:
                return "Vector store not loaded. Please run `python process_documents.py` first."
            
            logger.info(f"Processing query: {question}")
            
            # Initialize state - use dict format, not GraphState constructor
            initial_state = {
                "query": question,
                "translated_query": "",
                "context": "",
                "answer": "",
                "source_docs": []
            }
            
            # Run through the graph
            result = self.app.invoke(initial_state)
            
            return result["answer"]
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            logger.error(f"{error_msg}")
            return error_msg