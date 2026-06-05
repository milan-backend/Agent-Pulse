import os
import time
import chromadb
from datetime import datetime, timedelta
from chromadb.utils import embedding_functions

CHROMA_DATA_PATH = os.path.join(os.getcwd(), "data")
db_client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)

# We update the collection name to _v2 to force ChromaDB to re-seed 
# and show your "is_stale_document": True telemetry logic!
def get_labs_collection():
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    return db_client.get_or_create_collection(
        name="labs_knowledge_retrieval_v2",
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine"}
    )

def tracked_vector_query(query_text: str, n_results: int = 2):
    """
    Finalized Version: Tracks Hit Rate, Failures, Stale Docs, and exact Retrieval Query.
    """
    collection = get_labs_collection()
    
    if collection.count() == 0:
        documents = [
            "Our corporate enterprise premium plan costs $40 per user per month billed annually.",
            "Refund policy rules state that users can request a 100% full refund within 14 days of purchase."
        ]
        
        fresh_date = datetime.now().strftime("%Y-%m-%d")
        stale_date = (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d")
        
        metadatas = [
            {"source_file": "pricing.pdf", "page_number": 1, "last_updated": fresh_date},
            {"source_file": "refund_policy.pdf", "page_number": 3, "last_updated": stale_date}
        ]
        ids = ["pricing_chunk_001", "refund_chunk_001"]
        collection.add(documents=documents, metadatas=metadatas, ids=ids)
        print("[Labs DB] Experimental tracking documents seeded into ChromaDB successfully.")

    start_time = time.time()
    
    try:
        raw_results = collection.query(query_texts=[query_text], n_results=n_results)
        latency_ms = round((time.time() - start_time) * 1000, 2)
        status = "SUCCESS"
        error_message = None
    except Exception as e:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        status = "FAILED"
        error_message = str(e)
        raw_results = {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    documents_extracted = []
    hits = 0
    
    if raw_results and 'documents' in raw_results and len(raw_results['documents'][0]) > 0:
        for i in range(len(raw_results['documents'][0])):
            distance = round(raw_results['distances'][0][i], 4) if 'distances' in raw_results else 1.0
            doc_date_str = raw_results['metadatas'][0][i].get("last_updated", "")
            
            is_stale = False
            if doc_date_str:
                doc_date = datetime.strptime(doc_date_str, "%Y-%m-%d")
                if datetime.now() - doc_date > timedelta(days=30):
                    is_stale = True

            is_hit = distance < 0.55 
            if is_hit:
                hits += 1

            documents_extracted.append({
                "content_snippet": raw_results['documents'][0][i],
                "source_file": raw_results['metadatas'][0][i].get("source_file", "unknown.pdf"),
                "page_number": raw_results['metadatas'][0][i].get("page_number", 0),
                "semantic_distance": distance,
                "last_updated": doc_date_str,
                "is_stale_document": is_stale,
                "retrieval_hit": is_hit
            })

    total_requested = len(documents_extracted)
    hit_rate_pct = round((hits / total_requested) * 100, 2) if total_requested > 0 else 0.0

    telemetry_payload = {
        "event_type": "KNOWLEDGE_RETRIEVAL",
        "retrieval_query": query_text,  # <--- Added exactly what you wanted!
        "latency_ms": latency_ms,
        "status": status,
        "error_log": error_message,
        "total_documents_found": len(documents_extracted),
        "retrieval_hit_rate_percent": hit_rate_pct,
        "documents": documents_extracted
    }

    return raw_results, telemetry_payload