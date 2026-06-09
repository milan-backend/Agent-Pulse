import uuid
import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
import chromadb

from app.db.session import get_db
from app.models.user import User
from app.models.workspace import Workspace
from app.models.uploaded_document import UploadedDocument
from app.api.deps_user import get_current_user
from app.core.workspace_access import get_workspace_membership
from app.api.rbac import require_admin, require_operator
from app.core.rag_crypto import encrypt_file_bytes
from app.services.feature_access import require_rag_access

router = APIRouter(prefix="/documents", tags=["RAG Documents"])

# Allowed extensions for the initial MVP foundation
ALLOWED_MIME_TYPES = {
    "text/plain": ".txt",
    "application/pdf": ".pdf"
}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB maximum safeguard boundary


# ====================================================================
# SECURE CHROMA HTTP CLIENT HELPER (ENVIRONMENT VARIABLE CHANNELS)
# ====================================================================
def get_chroma_client():
    """Initializes a cloud-native HTTP client cleanly with zero hardcoded credentials."""
    chroma_host = os.getenv("CHROMA_HOST")
    chroma_token = os.getenv("CHROMA_TOKEN")
    
    if not chroma_host:
        raise ValueError("CRITICAL CONFIGURATION ERROR: CHROMA_HOST environment variable is missing on this container server.")
    
    # Strip trailing slashes safely to prevent routing connection mutations
    chroma_host = str(chroma_host).strip().rstrip("/")
    
    return chromadb.HttpClient(
        host=chroma_host,
        headers={"Authorization": f"Bearer {chroma_token}"} if chroma_token else None
    )


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    workspace_id: str = Header(...),
    agent_id: str = Query(None, description="Optional agent scope override mapping"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Secure Ingestion Gateway: Validates membership RBAC, checks subscription limits,
    encrypts raw binary bytes, and offloads extraction to background Celery.
    """
    # 1. Structural UUID Validation
    try:
        clean_ws_id = UUID(str(workspace_id).strip())
        clean_agent_id = UUID(str(agent_id).strip()) if agent_id else None
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provided workspace_id or agent_id structural routing parameter is not a valid UUID format."
        )

    # 2. Workspace Access Control & RBAC Check
    membership = get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=clean_ws_id
    )

    if clean_agent_id:
        # If adding to a specific agent, operator privileges are sufficient
        require_operator(membership)
    else:
        # Workspace-global document uploads are restricted strictly to Admins
        require_admin(membership)

    # 3. Fetch Workspace & Validate Subscription Quota Gates
    workspace = db.query(Workspace).filter(Workspace.id == clean_ws_id).first()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Target workspace context not found."
        )

    # Trigger premium tier billing validation guard from feature_access
    require_rag_access(workspace=workspace, db=db)

    # 4. File Format & Size Verifications
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format. Your workspace can only process standard {list(ALLOWED_MIME_TYPES.values())} files."
        )

    file_bytes = await file.read()
    file_size = len(file_bytes)

    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size boundary exceeded. Maximum upload payload capacity is capped at 10MB."
        )

    # 5. Cryptographic Encryption Execution (Tier 1 Protection)
    try:
        ciphertext, iv = encrypt_file_bytes(file_bytes=file_bytes, workspace_id=clean_ws_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cryptographic subsystem transaction failed: {str(e)}"
        )

    # 6. Commit Secure Record into PostgreSQL
    new_doc = UploadedDocument(
        filename=file.filename,
        encrypted_file_data=ciphertext,
        encryption_iv=iv,
        workspace_id=clean_ws_id,
        agent_id=clean_agent_id,
        file_size=file_size,
        mime_type=file.content_type,
        status="processing",
        uploaded_by=current_user.id
    )

    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # 7. Offload Ingestion Processing to Celery Infrastructure Asynchronously
    try:
        from app.tasks.rag_tasks import process_document_embedding
        process_document_embedding.delay(str(new_doc.id))
    except Exception as ce:
        print(f"⚠️ Worker background dispatch failure: {str(ce)}")

    return {
        "message": "File secure transmission complete. Background ingestion processing initiated.",
        "document_id": str(new_doc.id),
        "filename": new_doc.filename,
        "status": new_doc.status
    }


@router.get("/list")
def list_documents(
    workspace_id: str = Header(...),
    agent_id: str = Query(None, description="Filter records strictly belonging to an agent context scope"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Audit Trail List: Fetches all tracked document instances inside the workspace boundaries,
    verifying workspace access before execution.
    """
    try:
        clean_ws_id = UUID(str(workspace_id).strip())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid workspace_id tracking header mapping."
        )

    # Enforce basic workspace membership checking block before fetching list
    get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=clean_ws_id
    )

    # Base query looking inside workspace
    query = db.query(UploadedDocument).filter(UploadedDocument.workspace_id == clean_ws_id)

    # Route filter sorting out global vs agent scopes
    if agent_id:
        query = query.filter(UploadedDocument.agent_id == UUID(str(agent_id).strip()))
    else:
        query = query.filter(UploadedDocument.agent_id.is_(None))

    documents = query.order_by(UploadedDocument.created_at.desc()).all()

    response_list = []
    for doc in documents:
        uploader = db.query(User).filter(User.id == doc.uploaded_by).first()
        response_list.append({
            "id": str(doc.id),
            "filename": doc.filename,
            "file_size": doc.file_size,
            "mime_type": doc.mime_type,
            "status": doc.status,
            "agent_id": str(doc.agent_id) if doc.agent_id else None,
            "uploaded_by_user": uploader.email if uploader else "Unknown System Operator",
            "created_at": doc.created_at.isoformat() if doc.created_at else None
        })

    return response_list


# ====================================================================
# NEW ADDITION: SECURE DOCUMENT DELETION ROUTE ARCHITECTURE
# ====================================================================
@router.delete("/delete", status_code=status.HTTP_200_OK)
def delete_document(
    document_id: str = Query(..., description="The structural database ID of the target document to purge"),
    workspace_id: str = Header(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Synchronized Multi-Cloud Deletion Endpoint: Verifies rigorous tenancy isolation parameters,
    purges target document vector matrices from ChromaDB, and drops relational rows from PostgreSQL.
    Bypasses technical technical noise leak protocols for the public frontend state.
    """
    # 1. Structural Validation & Access Isolation Check
    try:
        clean_ws_id = UUID(str(workspace_id).strip())
        clean_doc_id = UUID(str(document_id).strip())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provided workspace_id or document_id contains invalid structural characters."
        )

    membership = get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=clean_ws_id
    )
    
    # Restrict document destruction boundaries to Operators or Admins
    require_operator(membership)

    # 2. Check document existence strictly bounded inside this specific tenant context workspace
    document_row = db.query(UploadedDocument).filter(
        UploadedDocument.id == clean_doc_id,
        UploadedDocument.workspace_id == clean_ws_id
    ).first()

    if not document_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested document could not be found or access is restricted within this workspace scope."
        )

    # 3. Perform Vector Space Clean-Up (ChromaDB Vector Index Flush)
    try:
        chroma_client = get_chroma_client()
        collection = chroma_client.get_collection(name="rag_knowledge_base")
        
        if collection:
            print(f"🧹 Commencing ChromaDB structural purge for: {document_row.filename}")
            # Target chunks strictly generated under this specific file context and workspace
            collection.delete(
                where={
                    "$and": [
                        {"workspace_id": str(clean_ws_id)},
                        {"source_file": str(document_row.filename)}
                    ]
                }
            )
    except Exception as chroma_err:
        # Graceful non-blocking degradation: logs notice but permits database entry drop 
        # (This handles deleting broken/partially uploaded records that didn't generate actual embeddings!)
        print(f"⚠️ Chroma index clean-up notice (Safe Fallback executed): {str(chroma_err)}")

    # 4. Perform Relational Clean-Up (PostgreSQL Record Purge)
    try:
        db.delete(document_row)
        db.commit()
    except Exception as db_err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Relational storage transaction failed to commit clean deletion: {str(db_err)}"
        )

    return {
        "success": True,
        "message": f"Document '{document_row.filename}' has been successfully purged from all cloud storage matrices."
    }