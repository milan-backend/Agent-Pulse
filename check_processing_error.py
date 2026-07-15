import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Let's inspect the absolute latest document you uploaded after the restart
    query = text("""
        SELECT filename, status, error_message, knowledge_metadata 
        FROM uploaded_documents 
        ORDER BY created_at DESC 
        LIMIT 1;
    """)
    row = conn.execute(query).fetchone()
    
    if row:
        print(f"📄 File Checked: {row.filename}")
        print(f"🔹 Status:       {row.status}")
        print(f"🔹 Error Msg:   {row.error_message}")
        print(f"🔹 Meta Keys:   {list(row.knowledge_metadata.keys()) if row.knowledge_metadata else 'Empty JSONB'}")