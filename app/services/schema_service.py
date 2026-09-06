from typing import Dict, List, Any
import os
from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from fastapi import HTTPException
import chromadb
from google import genai

from app.models.workspace_config import WorkspaceConfig
from app.core.sql_adapter import sql_adapter

class SchemaIntrospectionService:
    @classmethod
    def introspect_workspace_db(cls, config: WorkspaceConfig) -> Dict[str, Any]:
        """
        Inspects the client's database and extracts a structured catalog of tables,
        columns, and foreign keys.
        """
        try:
            engine: Engine = sql_adapter.get_engine(config)
            inspector = inspect(engine)
            
            table_names = inspector.get_table_names()
            schema_catalog = {}

            for table_name in table_names:
                # Skip system / migration tables
                if table_name in ["alembic_version", "spatial_ref_sys"]:
                    continue

                # 1. Fetch column metadata
                columns = inspector.get_columns(table_name)
                cols_meta = [
                    {
                        "name": col["name"],
                        "type": str(col["type"]),
                        "nullable": col.get("nullable", True)
                    }
                    for col in columns
                ]

                # 2. Fetch foreign keys to understand relationships
                foreign_keys = inspector.get_foreign_keys(table_name)
                fks_meta = [
                    {
                        "constrained_columns": fk.get("constrained_columns", []),
                        "referred_table": fk.get("referred_table"),
                        "referred_columns": fk.get("referred_columns", [])
                    }
                    for fk in foreign_keys
                ]

                schema_catalog[table_name] = {
                    "columns": cols_meta,
                    "foreign_keys": fks_meta
                }

            return schema_catalog

        except Exception as e:
            print(f"Failed to introspect schema for workspace {config.workspace_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Unable to inspect database schema."
            )

    @classmethod
    def format_schema_for_prompt(cls, schema_catalog: Dict[str, Any], relevant_tables: List[str] = None) -> str:
        """
        Prunes and formats the schema catalog into a compact string representation
        to inject into the LLM prompt without token bloat.
        """
        tables_to_include = relevant_tables or list(schema_catalog.keys())
        lines = []

        for table_name in tables_to_include:
            table_info = schema_catalog.get(table_name)
            if not table_info:
                continue

            col_descriptions = [f"{col['name']} ({col['type']})" for col in table_info["columns"]]
            columns_str = ", ".join(col_descriptions)
            
            line = f"Table {table_name}: {columns_str}"
            
            if table_info["foreign_keys"]:
                fk_parts = []
                for fk in table_info["foreign_keys"]:
                    fk_parts.append(
                        f"{fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}"
                    )
                line += f" | Foreign Keys: {'; '.join(fk_parts)}"

            lines.append(line)

        return "\n".join(lines)


# =====================================================================
# 🟢 CHROMA DB SCHEMA CHUNKING & INDEXING SERVICE
# =====================================================================
class SchemaSyncService:
    @classmethod
    def sync_workspace_schemas_to_chroma(cls, config: WorkspaceConfig) -> int:
        """
        Introspects tables, enforces table scope permissions, generates
        a '1 Table = 1 Chunk' Semantic Card, and stores it in ChromaDB.
        """
        workspace_id_str = str(config.workspace_id)
        
        # 1. Introspect client's database
        raw_catalog = SchemaIntrospectionService.introspect_workspace_db(config)
        if not raw_catalog:
            return 0
            
        # 2. Filter allowed tables based on client onboarding preference
        catalog = {}
        if getattr(config, "sync_all_tables", True):
            catalog = raw_catalog
        else:
            allowed = set(getattr(config, "allowed_tables", []) or [])
            for table_name in allowed:
                if table_name in raw_catalog:
                    catalog[table_name] = raw_catalog[table_name]

        if not catalog:
            print(f"⚠️ [SCHEMA SYNC] No valid tables matched allowed_tables for {workspace_id_str}")
            return 0

        # 3. Setup AI Client and ChromaDB Client
        gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
        ai_client = genai.Client(api_key=gemini_key)

        chroma_host = str(os.getenv("CHROMA_HOST", "")).strip().rstrip("/")
        chroma_token = os.getenv("CHROMA_TOKEN")
        chroma_client = chromadb.HttpClient(
            host=chroma_host,
            headers={"Authorization": f"Bearer {chroma_token}"} if chroma_token else None
        )
        
        collection = chroma_client.get_or_create_collection(
            name="rag_enterprise_vectors_v1",
            metadata={"hnsw:space": "cosine"}
        )

        # 4. Remove previous schema entries for this tenant to avoid stale cards
        try:
            collection.delete(
                where={
                    "$and": [
                        {"workspace_id": workspace_id_str},
                        {"content_type": "db_schema"}
                    ]
                }
            )
        except Exception:
            pass

        ids = []
        documents = []
        metadatas = []
        embeddings = []

        # 5. Build 1 Chunk per Table
        for table_name, table_info in catalog.items():
            col_list = [f"{c['name']} ({c['type']})" for c in table_info["columns"]]
            fk_list = [
                f"{fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}"
                for fk in table_info["foreign_keys"]
            ]
            
            schema_text = (
                f"Database Table: {table_name}\n"
                f"Columns: {', '.join(col_list)}\n"
                f"Foreign Keys: {', '.join(fk_list) if fk_list else 'None'}"
            )

            col_names_str = " ".join([c["name"].lower() for c in table_info["columns"]])
            keywords = f"{table_name.lower()} {col_names_str}"

            embed_resp = ai_client.models.embed_content(
                model="models/gemini-embedding-001",
                contents=schema_text
            )
            
            ids.append(f"schema_{workspace_id_str}_{table_name}")
            documents.append(schema_text)
            embeddings.append(embed_resp.embeddings[0].values)
            metadatas.append({
                "workspace_id": workspace_id_str,
                "content_type": "db_schema",
                "table_name": table_name,
                "schema_keywords": keywords
            })

        # 6. Upload Chunks to ChromaDB
        if ids:
            collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            print(f"📦 [CHROMA SYNC] Indexed {len(ids)} table schemas for workspace: {workspace_id_str}")

        return len(ids)