import os
import time
import logging
from dotenv import load_dotenv

# LangChain imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# Configuration - No defaults, must be in .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR")
HR_POLICIES_PATH = os.getenv("HR_POLICIES_PATH")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")

# Validate required environment variables
required_vars = {
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "CHROMA_PERSIST_DIR": CHROMA_PERSIST_DIR,
    "HR_POLICIES_PATH": HR_POLICIES_PATH,
    "OPENAI_MODEL_NAME": OPENAI_MODEL_NAME,
    "EMBEDDING_MODEL_NAME": EMBEDDING_MODEL_NAME
}

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_llm():
    """Creates an LLM object and returns it."""
    llm = ChatOpenAI(temperature=0.3, model_name=OPENAI_MODEL_NAME, openai_api_key=OPENAI_API_KEY)
    return llm

def get_embedding():
    """Creates an embedding object and returns it."""
    embedding = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME, openai_api_key=OPENAI_API_KEY)
    return embedding

def create_or_load_chroma_db(docs, db_name=CHROMA_PERSIST_DIR, collection_name=None):
    """
    Creates a new Chroma DB or loads existing one.
    
    Args:
        docs: List of documents to store (for new DB creation)
        db_name: Name of the database directory
        collection_name: Name of the collection within the database
    
    Returns:
        Chroma vector store object
    """
    # Collection name is required
    if not collection_name:
        collection_name = os.getenv("CHROMA_COLLECTION_NAME")
        if not collection_name:
            raise RuntimeError("CHROMA_COLLECTION_NAME environment variable is required")
    
    # Use absolute path for persist directory
    persist_dir = os.path.abspath(db_name)
    
    # Check if Chroma DB already exists
    if os.path.exists(persist_dir):
        print(f"Loading existing Chroma DB from: {persist_dir}")
        vector_store = Chroma(
            persist_directory=persist_dir,
            embedding_function=get_embedding(),
            collection_name=collection_name
        )
    else:
        print(f"Creating new Chroma DB at: {persist_dir}")
        vector_store = Chroma.from_documents(
            docs, 
            embedding=get_embedding(), 
            collection_name=collection_name,
            persist_directory=persist_dir
        )
    
    return vector_store

def main():
    """Main function to process PDF and store in ChromaDB using LangChain."""
    print("=== PDF to ChromaDB Processing with LangChain ===")
    
    # All environment variables are already validated at the top
    
    if not os.path.exists(HR_POLICIES_PATH):
        raise RuntimeError(f"PDF file not found at {HR_POLICIES_PATH}")
    
    try:
        # Load PDF using LangChain
        print(f"Loading PDF from {HR_POLICIES_PATH}...")
        loader = PyPDFLoader(HR_POLICIES_PATH)
        documents = loader.load()
        print(f"Loaded {len(documents)} pages from PDF")
        
        # Get chunk size from environment
        chunk_size = int(os.getenv("CHUNK_SIZE"))
        chunk_overlap = int(os.getenv("CHUNK_OVERLAP"))
        
        # Split into chunks
        print("Splitting documents into chunks...")
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        docs = splitter.split_documents(documents)
        print(f"Created {len(docs)} chunks")
        
        # Create or load Chroma DB
        print("Creating/loading Chroma DB...")
        collection_name = os.getenv("CHROMA_COLLECTION_NAME")
        vector_store = create_or_load_chroma_db(docs, db_name=CHROMA_PERSIST_DIR, collection_name=collection_name)
        
        # Test retrieval
        print("Testing vector retrieval...")
        retriever = vector_store.as_retriever()
        results = retriever.invoke("What is the leave policy?")
        print(f"Found {len(results)} relevant documents")
        
        if results:
            print(f"First result preview: {results[0].page_content[:200]}...")
        
        print("✓ PDF to ChromaDB processing completed successfully!")
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


