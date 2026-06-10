from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from uuid import UUID

from app.models.user_api_key import UserAPIKey
from app.core.crypto import encrypt_api_key, decrypt_api_key


class UserAPIKeyService:
    @staticmethod
    def store_key(
        db: Session, 
        provider: str, 
        raw_key: str, 
        workspace_id: UUID,            # STRICT SECURITY BOUNDARY: MANDATORY
        user_id: Optional[UUID] = None, 
        agent_id: Optional[UUID] = None,
        model_version: Optional[str] = None
    ) -> UserAPIKey:
        """
        EXISTING CORRECT LOGIC (UNTOUCHED):
        Encrypts the raw API key from the frontend dropdown/input and saves it.
        If a key record already exists under the matching hierarchical constraints 
        (Agent-specific or Workspace-default), it cleanly updates it in place.
        """
        if not workspace_id:
            raise ValueError("Security Violation: workspace_id is strictly mandatory for storing credentials.")

        provider_clean = provider.lower().strip()      # Always stores as clean lowercase 'gemini' or 'openai'
        model_version_clean = model_version.strip() if model_version else None
        encrypted_str = encrypt_api_key(raw_key)

        # Look for an existing key match based on our strict hierarchical tracking constraints
        if agent_id:
            # Tier 1: Agent specific keys are unique per agent + workspace + provider
            stmt = select(UserAPIKey).where(
                and_(
                    UserAPIKey.agent_id == agent_id,
                    UserAPIKey.workspace_id == workspace_id,
                    UserAPIKey.provider == provider_clean
                )
            )
        else:
            # Tier 2: Workspace keys are unique per workspace + provider + model version choice
            stmt = select(UserAPIKey).where(
                and_(
                    UserAPIKey.workspace_id == workspace_id, 
                    UserAPIKey.agent_id == None,
                    UserAPIKey.provider == provider_clean,
                    UserAPIKey.model_version == model_version_clean
                )
            )

        existing_record = db.execute(stmt).scalars().first()

        if existing_record:
            existing_record.encrypted_api_key = encrypted_str
            db.commit()
            db.refresh(existing_record)
            return existing_record
        else:
            new_key_entry = UserAPIKey(
                user_id=user_id,
                workspace_id=workspace_id,
                agent_id=agent_id,
                provider=provider_clean,
                model_version=model_version_clean,
                encrypted_api_key=encrypted_str
            )
            db.add(new_key_entry)
            db.commit()
            db.refresh(new_key_entry)
            return new_key_entry

    @staticmethod
    def fetch_decrypted_key(
        db: Session, 
        provider: str, 
        workspace_id: UUID,            # STRICT SECURITY BOUNDARY: MANDATORY
        agent_id: Optional[UUID] = None,
        model_version: Optional[str] = None
    ) -> Optional[str]:
        """
        EXISTING CORRECT LOGIC (UNTOUCHED):
        Fetches the encrypted API key from the database using explicit hierarchical scopes
        and returns the fully decrypted plain text token string ready for client initialization.
        """
        if not workspace_id:
            raise ValueError("Security Violation: workspace_id is strictly mandatory for retrieving credentials.")

        provider_clean = provider.lower().strip()
        model_version_clean = model_version.strip() if model_version else None

        if agent_id:
            stmt = select(UserAPIKey).where(
                and_(
                    UserAPIKey.agent_id == agent_id,
                    UserAPIKey.workspace_id == workspace_id,
                    UserAPIKey.provider == provider_clean
                )
            )
        else:
            stmt = select(UserAPIKey).where(
                and_(
                    UserAPIKey.workspace_id == workspace_id, 
                    UserAPIKey.agent_id == None,
                    UserAPIKey.provider == provider_clean,
                    UserAPIKey.model_version == model_version_clean
                )
            )

        record = db.execute(stmt).scalars().first()
        
        if not record:
            return None

        return decrypt_api_key(record.encrypted_api_key)

    @staticmethod
    def remove_key(
        db: Session, 
        provider: str, 
        workspace_id: UUID,            # STRICT SECURITY BOUNDARY: MANDATORY
        agent_id: Optional[UUID] = None,
        model_version: Optional[str] = None
    ) -> bool:
        """
        EXISTING CORRECT LOGIC (UNTOUCHED):
        Deletes a specific targeted provider API key configuration row cleanly within a workspace scope.
        """
        if not workspace_id:
            raise ValueError("Security Violation: workspace_id is strictly mandatory for removing credentials.")

        provider_clean = provider.lower().strip()
        model_version_clean = model_version.strip() if model_version else None

        if agent_id:
            stmt = select(UserAPIKey).where(
                and_(
                    UserAPIKey.agent_id == agent_id,
                    UserAPIKey.workspace_id == workspace_id,
                    UserAPIKey.provider == provider_clean
                )
            )
        else:
            stmt = select(UserAPIKey).where(
                and_(
                    UserAPIKey.workspace_id == workspace_id, 
                    UserAPIKey.agent_id == None,
                    UserAPIKey.provider == provider_clean,
                    UserAPIKey.model_version == model_version_clean
                )
            )

        record = db.execute(stmt).scalars().first()

        if record:
            db.delete(record)
            db.commit()
            return True
        return False

    # =========================================================================
    # NEW MULTI-PROVIDER ARCHITECTURE UPGRADE LOGIC
    # =========================================================================

    @staticmethod
    def store_workspace_provider(
        db: Session,
        workspace_id: UUID,
        provider_name: str,
        provider_type: str,
        raw_key: Optional[str] = None,
        model_name: Optional[str] = None,
        assigned_agents: Optional[List[str]] = None,
        is_global_default: bool = False,
        user_id: Optional[UUID] = None,
        provider_id: Optional[UUID] = None
    ) -> UserAPIKey:
        """
        Stores or updates an advanced, multi-tenant Workspace provider configuration.
        Ensures strict separation and supports unlimited keys from the same provider engine type.
        """
        if not workspace_id:
            raise ValueError("Security Violation: workspace_id is required to register workspace providers.")

        provider_clean = provider_type.lower().strip()
        
        # Safe default label fallback
        clean_name = provider_name.strip() if provider_name else "Workspace Provider"

        # Safe toggle update: Reset other defaults for this engine type if this row is the new global fallback choice
        if is_global_default:
            db.query(UserAPIKey).filter(
                UserAPIKey.workspace_id == workspace_id,
                UserAPIKey.provider == provider_clean,
                UserAPIKey.agent_id == None
            ).update({"is_default": False}, synchronize_session=False)
            db.commit()

        existing_record = None
        # 1. Look up by ID if updating an existing record configuration
        if provider_id:
            existing_record = db.query(UserAPIKey).filter(UserAPIKey.id == provider_id).first()
        else:
            # 2. Look up by unique combination string name to avoid duplication records
            existing_record = db.query(UserAPIKey).filter(
                UserAPIKey.workspace_id == workspace_id,
                UserAPIKey.provider_name == clean_name,
                UserAPIKey.agent_id == None
            ).first()

        if existing_record:
            existing_record.provider_name = clean_name
            existing_record.provider = provider_clean
            if raw_key and raw_key.strip():
                existing_record.encrypted_api_key = encrypt_api_key(raw_key)
            if model_name:
                existing_record.model_name = model_name.strip()
            existing_record.assigned_agents = assigned_agents or []
            existing_record.is_global_default = is_global_default
            
            db.commit()
            db.refresh(existing_record)
            return existing_record
        else:
            if not raw_key or not raw_key.strip():
                raise ValueError("API Key credential value token is strictly required for new provider integrations.")

            new_provider = UserAPIKey(
                user_id=user_id,
                workspace_id=workspace_id,
                agent_id=None,  # Dedicated workspace configuration instance shared tier
                provider=provider_clean,
                provider_name=clean_name,
                encrypted_api_key=encrypt_api_key(raw_key),
                is_global_default=is_global_default
            )
            if model_name:
                new_provider.model_name = model_name.strip()
            new_provider.assigned_agents = assigned_agents or []
            
            db.add(new_provider)
            db.commit()
            db.refresh(new_provider)
            return new_provider

    @staticmethod
    def resolve_agent_api_key(
        db: Session,
        workspace_id: UUID,
        agent_id: UUID,
        provider_type: str
    ) -> Optional[UserAPIKey]:
        """
        Executes the exact 4-Step Priority Resolution Engine:
        Step 1: Check Agent-Specific API Provider Override.
        Step 2: Check Workspace Providers explicitly assigned to this agent.
        Step 3: Check Workspace Global Fallback Provider (assigned_agents is empty).
        Step 4: Fallback to System Tier (returns None).
        """
        p_type = provider_type.lower().strip()
        ag_id_str = str(agent_id).strip()

        # --- STEP 1: Check Agent-Specific API Provider Override ---
        agent_specific = db.query(UserAPIKey).filter(
            UserAPIKey.agent_id == agent_id,
            UserAPIKey.workspace_id == workspace_id,
            UserAPIKey.provider == p_type
        ).first()
        if agent_specific:
            return agent_specific

        # Fetch all Workspace-managed keys for this provider type
        workspace_keys = db.query(UserAPIKey).filter(
            UserAPIKey.workspace_id == workspace_id,
            UserAPIKey.agent_id == None,
            UserAPIKey.provider == p_type
        ).all()

        # --- STEP 2: Check Workspace Providers Assigned to this Agent ---
        for w_key in workspace_keys:
            if ag_id_str in w_key.assigned_agents:
                return w_key

        # --- STEP 3: Check Workspace Global Provider (assigned_agents empty) ---
        global_fallback = None
        for w_key in workspace_keys:
            # If explicitly marked as global default and has no specific agent constraints
            if w_key.is_global_default and not w_key.assigned_agents:
                return w_key
            # Standby default fallback assignment tracker if row contains an empty assignment pool
            if not w_key.assigned_agents:
                global_fallback = w_key

        if global_fallback:
            return global_fallback

        # --- STEP 4: Fallback to AgentPulse Free Tier Provider ---
        return None