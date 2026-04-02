"""Simplified ChromaDB vector store service using LangChain for HR policy document retrieval."""

import os
import logging
from typing import List, Optional

# LangChain imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from app.config import settings

logger = logging.getLogger(__name__)

# Use settings for all configuration values


class VectorStoreService:
    """Simplified vector store service using LangChain for HR policy document retrieval.

    Attributes:
        persist_directory: Path where ChromaDB persists its data.
        openai_api_key: OpenAI API key used for generating embeddings.
        vector_store: LangChain Chroma vector store instance.
        embedding_fn: LangChain OpenAI embedding function.
    """

    def __init__(self, persist_directory: str, openai_api_key: str) -> None:
        self.persist_directory = persist_directory
        self.openai_api_key = openai_api_key
        
        # Initialize embedding function with model from settings
        self.embedding_fn = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL_NAME,
            openai_api_key=openai_api_key
        )
        
        # Initialize vector store (will be loaded with documents)
        self.vector_store: Optional[Chroma] = None
        
        logger.info(f"VectorStoreService initialized with {settings.EMBEDDING_MODEL_NAME} model")

    def load_pdf(self, pdf_path: str, source_label: str = "hr_policies") -> int:
        """Load a PDF using LangChain, chunk it, and store in ChromaDB.

        Args:
            pdf_path: Path to the PDF file to ingest.
            source_label: Metadata tag to identify the source document.

        Returns:
            Number of new chunks inserted.
        """
        try:
            # Check if vector store already exists and has documents
            if os.path.exists(self.persist_directory):
                logger.info("Loading existing ChromaDB...")
                self.vector_store = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embedding_fn,
                    collection_name=settings.CHROMA_COLLECTION_NAME
                )
                
                # Check if documents already exist
                if self.vector_store._collection.count() > 0:
                    logger.info("Document already loaded (%d chunks). Skipping.", 
                              self.vector_store._collection.count())
                    return 0
            
            # Load PDF using LangChain
            logger.info("Extracting text from '%s' using LangChain...", pdf_path)
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            if not documents:
                logger.warning("No documents extracted from '%s'.", pdf_path)
                return 0
            
            # Split into chunks using LangChain
            logger.info("Splitting documents into chunks...")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP
            )
            chunks = text_splitter.split_documents(documents)
            
            if not chunks:
                logger.warning("No chunks created from '%s'.", pdf_path)
                return 0
            
            # Create vector store with documents
            logger.info("Creating embeddings and storing %d chunks in ChromaDB...", len(chunks))
            self.vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embedding_fn,
                collection_name=settings.CHROMA_COLLECTION_NAME,
                persist_directory=self.persist_directory
            )
            
            logger.info("Successfully inserted %d chunks from '%s'.", len(chunks), pdf_path)
            return len(chunks)
            
        except Exception as e:
            logger.error("Failed to load PDF '%s': %s", pdf_path, str(e))
            raise RuntimeError(f"PDF loading failed: {str(e)}") from e

    def query(self, question: str, n_results: int = 5) -> List[str]:
        """Return the most relevant document chunks for *question*.

        Args:
            question: Natural-language question to search for.
            n_results: Maximum number of chunks to return.

        Returns:
            List of relevant text chunks ordered by relevance (most relevant first).
        """
        if not self.vector_store:
            logger.warning("Vector store not initialized. No documents to query.")
            return []
        
        try:
            # Use LangChain similarity search
            docs = self.vector_store.similarity_search(
                question, 
                k=min(n_results, self.vector_store._collection.count())
            )
            
            # Extract page content from documents
            return [doc.page_content for doc in docs]
            
        except Exception as e:
            logger.error("Vector store query failed: %s", e)
            return []

    def count(self) -> int:
        """Return the number of documents in the vector store."""
        if not self.vector_store:
            return 0
        return self.vector_store._collection.count()


# Legacy functions for backward compatibility
def _chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """Legacy chunking function - use VectorStoreService.load_pdf() instead."""
    # This is kept for backward compatibility but should not be used
    logger.warning("_chunk_text is deprecated. Use VectorStoreService.load_pdf() instead.")
    return []


def _extract_text_from_pdf(pdf_path: str) -> str:
    """Legacy PDF extraction function - use VectorStoreService.load_pdf() instead."""
    # This is kept for backward compatibility but should not be used
    logger.warning("_extract_text_from_pdf is deprecated. Use VectorStoreService.load_pdf() instead.")
    return ""
