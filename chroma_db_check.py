import os
import chromadb

def purge_all_stale_vectors():
    # 1. Grab environmental variables matching your production cluster
    chroma_host = os.getenv("CHROMA_HOST", "https://chroma-production-2690.up.railway.app")
    chroma_token = os.getenv("CHROMA_TOKEN")
    
    print(f"🧹 Connecting to ChromaDB instance: {chroma_host}")
    client = chromadb.HttpClient(
        host=chroma_host.strip().rstrip("/"),
        headers={"Authorization": f"Bearer {chroma_token}"} if chroma_token else None
    )
    
    try:
        # 2. Fetch our active dense 3072-dimension collection box
        collection = client.get_collection(name="rag_enterprise_vectors_v1")
        
        if collection:
            # Check total items currently sitting in the collection
            before_count = collection.count()
            print(f"📊 Current total chunks inside collection BEFORE purge: {before_count}")
            
            # 🎯 THE TRICK: Purge everything by recreating or deleting the collection cleanly
            client.delete_collection(name="rag_enterprise_vectors_v1")
            print("🗑️ Successfully wiped out the collection volume from disk.")
            
            # Recreate it instantly fresh, empty, and clean
            client.get_or_create_collection(
                name="rag_enterprise_vectors_v1",
                metadata={"hnsw:space": "cosine"}
            )
            print("🆕 Recreated a pristine, empty 'rag_enterprise_vectors_v1' collection box!")
            print("✅ All old stale 'undefined' files have been completely blasted from disk memory!")
            
    except Exception as error:
        print(f"❌ Error encountered during dynamic database reset loop: {str(error)}")

if __name__ == "__main__":
    purge_all_stale_vectors()