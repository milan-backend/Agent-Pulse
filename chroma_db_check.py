import os
import chromadb

def force_purge_old_collections():
    chroma_host = os.getenv("CHROMA_HOST", "https://chroma-production-2690.up.railway.app")
    chroma_token = os.getenv("CHROMA_TOKEN")
    
    print(f"🧹 Connecting to ChromaDB server at: {chroma_host}")
    client = chromadb.HttpClient(
        host=chroma_host.strip().rstrip("/"),
        headers={"Authorization": f"Bearer {chroma_token}"} if chroma_token else None
    )
    
    # List all active collections on the server instance
    all_collections = client.list_collections()
    print(f"🔍 Found {len(all_collections)} active collections in memory.")
    
    # 🎯 FORCE DELETE BOTH STALE COLLECTIONS
    collections_to_delete = ["rag_knowledge_vectors", "rag_enterprise_vectors_v1"]
    
    for col_name in collections_to_delete:
        try:
            client.delete_collection(name=col_name)
            print(f"🗑️ Successfully deleted corrupted collection: '{col_name}'")
        except Exception as e:
            print(f"⚠️ Collection '{col_name}' could not be deleted (might already be empty): {str(e)}")

    print("✅ Database volume successfully cleaned. Ready for fresh 3072 dimension matching!")

if __name__ == "__main__":
    force_purge_old_collections()