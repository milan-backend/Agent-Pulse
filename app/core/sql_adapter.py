from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from typing import Dict, Any, List
from urllib.parse import quote_plus
from fastapi import HTTPException

from app.models.workspace_config import WorkspaceConfig
from app.core.encryption import decrypt_vault_secret

class UniversalSQLAdapter:
    def __init__(self):
        # Cache active engines in memory: { workspace_id: Engine }
        # This ensures we don't spam the client's database with new connections on every query.
        self.active_engines: Dict[str, Engine] = {}

    def _build_database_url(self, config: WorkspaceConfig) -> str:
        """Constructs the SQLAlchemy connection URL dynamically."""
        
        password = decrypt_vault_secret(config.db_password_encrypted)
        safe_password = quote_plus(password)
        
        dialect_map = {
            "postgresql": "postgresql+psycopg2",
            "mysql": "mysql+pymysql",
        }
        
        driver = dialect_map.get(config.db_type.lower(), config.db_type.lower())
        
        url = f"{driver}://{config.db_username}:{safe_password}@{config.db_host}:{config.db_port}/{config.db_name}"
        
        # 👉 ADD THIS: Hardcode SSL directly into the URL string for SNI compliance
        if config.db_type.lower() == "postgresql":
            url += "?sslmode=require"
            
        return url

    def get_engine(self, config: WorkspaceConfig) -> Engine:
        """Returns a cached SQLAlchemy Engine or creates a new one for the tenant."""
        workspace_id = str(config.workspace_id)
        
        if workspace_id in self.active_engines:
            return self.active_engines[workspace_id]
            
        try:
            db_url = self._build_database_url(config)
            
            # create_engine initializes the connection pool
            engine = create_engine(
                db_url,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10
                # (Notice we removed connect_args from here!)
            )
            
            self.active_engines[workspace_id] = engine
            return engine
            
        except Exception as e:
            print(f"Engine creation failed for workspace {workspace_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to connect to workspace database.")

    def execute_secure_query(self, config: WorkspaceConfig, user_id: str, sql_statement: str, params: dict) -> List[Dict[str, Any]]:
        """
        Executes a query with strict tenant and identity isolation.
        """
        engine = self.get_engine(config)
        
        # THE IRON WALL: We force the authenticated user_id into the query parameters at the backend level.
        # Even if the AI hallucinated a different user_id, it is overwritten here.
        safe_params = params.copy()
        safe_params["auth_user_id"] = user_id
        
        try:
            # We connect to the specific client's database and execute the bound query
            with engine.connect() as connection:
                result = connection.execute(text(sql_statement), safe_params)
                
                # Fetch all rows and convert them to a list of standard dictionaries
                rows = [dict(row._mapping) for row in result]
                return rows
                
        except Exception as e:
            print(f"Query execution failed: {e}")
            raise HTTPException(status_code=400, detail="Failed to execute data query.")

# Create a single global instance for FastAPI to use
sql_adapter = UniversalSQLAdapter()