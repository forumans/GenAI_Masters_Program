"""Check what holiday data is in ChromaDB."""

from app.services.vector_store import VectorStoreService

def check_holiday_data():
    """Check what holiday data exists in the vector store."""
    print("=== Checking Holiday Data in ChromaDB ===")
    
    try:
        # Get vector store
        vector_store = VectorStoreService()
        
        # Search for holidays
        results = vector_store.vector_store.similarity_search(
            "public holidays 2026",
            k=10
        )
        
        print(f"\nFound {len(results)} documents about holidays:")
        print("=" * 60)
        
        for i, doc in enumerate(results, 1):
            print(f"\nDocument {i}:")
            print(f"Source: {doc.metadata.get('source', 'Unknown')}")
            print(f"Content preview: {doc.page_content[:300]}...")
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_holiday_data()
