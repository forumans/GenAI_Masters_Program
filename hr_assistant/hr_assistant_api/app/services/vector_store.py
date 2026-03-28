"""ChromaDB vector store service for HR policy document retrieval."""

import os
import logging
from typing import List

import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI

logger = logging.getLogger(__name__)

COLLECTION_NAME = "hr_policies"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split *text* into overlapping chunks of approximately *chunk_size* characters.

    Args:
        text: Full document text.
        chunk_size: Target character length per chunk.
        overlap: Number of characters to overlap between consecutive chunks.

    Returns:
        List of text chunks.
    """
    chunks: List[str] = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        # Try to end at a sentence boundary
        if end < text_length:
            boundary = text.rfind(".", start, end)
            if boundary > start:
                end = boundary + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap

    return chunks


def _extract_text_from_pdf(pdf_path: str) -> str:
    """Extract plain text from a PDF file.

    Tries PyPDF2 first, then falls back to pdfplumber if available.

    Args:
        pdf_path: Absolute or relative path to the PDF.

    Returns:
        Extracted text as a single string.
    """
    try:
        import PyPDF2
        text_parts: List[str] = []
        with open(pdf_path, "rb") as fh:
            reader = PyPDF2.PdfReader(fh)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)
    except ImportError:
        pass

    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)
    except ImportError:
        pass

    raise RuntimeError(
        "No PDF extraction library found. "
        "Install PyPDF2 (`pip install PyPDF2`) or pdfplumber (`pip install pdfplumber`)."
    )


class VectorStoreService:
    """Manages a ChromaDB collection of HR policy document embeddings.

    Attributes:
        persist_directory: Path where ChromaDB persists its data.
        openai_api_key: OpenAI API key used for generating embeddings.
        client: ChromaDB persistent client.
        collection: ChromaDB collection holding policy chunks.
        embedding_fn: OpenAI embedding function used by ChromaDB.
    """

    def __init__(self, persist_directory: str, openai_api_key: str) -> None:
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)

        self.client = chromadb.PersistentClient(path=persist_directory)

        self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
            api_key=openai_api_key,
            model_name="text-embedding-ada-002",
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

        logger.info(
            "VectorStoreService initialised. Collection '%s' has %d documents.",
            COLLECTION_NAME,
            self.collection.count(),
        )

    def load_pdf(self, pdf_path: str, source_label: str = "hr_policies") -> int:
        """Load a PDF, chunk it, and upsert chunks into the collection.

        If the document has already been loaded (same source_label) this method
        returns 0 without re-inserting duplicates.

        Args:
            pdf_path: Path to the PDF file to ingest.
            source_label: Metadata tag to identify the source document.

        Returns:
            Number of new chunks inserted.
        """
        existing = self.collection.get(where={"source": source_label})
        if existing and existing["ids"]:
            logger.info("Document '%s' already loaded (%d chunks). Skipping.", source_label, len(existing["ids"]))
            return 0

        logger.info("Extracting text from '%s' …", pdf_path)
        text = _extract_text_from_pdf(pdf_path)
        chunks = _chunk_text(text)

        if not chunks:
            logger.warning("No text extracted from '%s'.", pdf_path)
            return 0

        ids = [f"{source_label}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": source_label, "chunk_index": i} for i in range(len(chunks))]

        self.collection.upsert(documents=chunks, ids=ids, metadatas=metadatas)
        logger.info("Inserted %d chunks from '%s'.", len(chunks), source_label)
        return len(chunks)

    def query(self, question: str, n_results: int = 5) -> List[str]:
        """Return the most relevant document chunks for *question*.

        Args:
            question: Natural-language question to search for.
            n_results: Maximum number of chunks to return.

        Returns:
            List of relevant text chunks ordered by relevance (most relevant first).
        """
        if self.collection.count() == 0:
            return []

        results = self.collection.query(
            query_texts=[question],
            n_results=min(n_results, self.collection.count()),
        )
        documents = results.get("documents", [[]])[0]
        return documents
