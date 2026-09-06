from celery import shared_task
from app.db.session import SessionLocal
from app.models.workspace_config import WorkspaceConfig
from app.services.schema_service import SchemaSyncService

@shared_task(bind=True, max_retries=3, name="app.tasks.schema_tasks.sync_database_schemas")
def sync_database_schemas(self, workspace_id: str):
    """
    Background worker that connects to client DB, inspects tables,
    and indexes them into ChromaDB.
    """
    db = SessionLocal()
    try:
        config = db.query(WorkspaceConfig).filter_by(workspace_id=workspace_id).first()
        if not config:
            print(f"❌ [SCHEMA SYNC] Configuration missing for workspace: {workspace_id}")
            return False

        print(f"🚀 [SCHEMA SYNC] Syncing schemas for workspace: {workspace_id}")
        indexed_count = SchemaSyncService.sync_workspace_schemas_to_chroma(config)
        print(f"✅ [SCHEMA SYNC] Successfully indexed {indexed_count} tables.")
        return True

    except Exception as e:
        print(f"❌ [SCHEMA SYNC] Error syncing schema: {e}")
        countdown = 5 ** self.request.retries
        raise self.retry(exc=e, countdown=countdown)
    finally:
        db.close()