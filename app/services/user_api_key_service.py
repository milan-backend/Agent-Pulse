from typing import Optional, List, Tuple
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
        Fetches the encrypted API key from the database using explicit hierarchical scopes.
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
    # MULTI-PROVIDER UPGRADE STORAGE AND SELECTION LOGIC
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
        """
        if not workspace_id:
            raise ValueError("Security Violation: workspace_id is required to register workspace providers.")

        provider_clean = provider_type.lower().strip()
        clean_name = provider_name.strip() if provider_name else "Workspace Provider"

        if is_global_default:
            db.query(UserAPIKey).filter(
                UserAPIKey.workspace_id == workspace_id,
                UserAPIKey.provider == provider_clean,
                UserAPIKey.agent_id == None
            ).update({"is_global_default": False}, synchronize_session=False)
            db.commit()

        existing_record = None
        if provider_id:
            existing_record = db.query(UserAPIKey).filter(UserAPIKey.id == provider_id).first()
        else:
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
                existing_record.model_version = model_name.strip()
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
                agent_id=None,
                provider=provider_clean,
                provider_name=clean_name,
                encrypted_api_key=encrypt_api_key(raw_key),
                is_global_default=is_global_default
            )
            if model_name:
                new_provider.model_version = model_name.strip()
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
    ) -> Tuple[Optional[UserAPIKey], str]:
        """
        Executes the blueprint hierarchy rules and labels attribution tracking.
        Returns a Tuple of: (UserAPIKey object or None, "agent" | "workspace" | "system")
        """
        p_type = provider_type.lower().strip()
        ag_id_str = str(agent_id).strip()

        # --- RULE 1: Check Agent-Specific Override ---
        agent_specific = db.query(UserAPIKey).filter(
            UserAPIKey.agent_id == agent_id,
            UserAPIKey.workspace_id == workspace_id,
            UserAPIKey.provider == p_type
        ).first()
        if agent_specific:
            return agent_specific, "agent"  # 🎯 Tagged as Agent-Specific Private Key

        # Fetch all workspace-level providers for this engine
        workspace_keys = db.query(UserAPIKey).filter(
            UserAPIKey.workspace_id == workspace_id,
            UserAPIKey.agent_id == None,
            UserAPIKey.provider == p_type
        ).all()

        # --- RULE 2: Check Workspace Key Matching Explicit Agent Allocations ---
        for w_key in workspace_keys:
            current_assignments = w_key.assigned_agents
            if current_assignments and ag_id_str in current_assignments:
                return w_key, "workspace"  # 🎯 Tagged as Workspace-Assigned Key

        # --- RULE 3: Check Workspace Key Open for ALL Agents (Strict Fallback Guard) ---
        for w_key in workspace_keys:
            current_assignments = w_key.assigned_agents
            if not current_assignments or w_key.is_global_default:
                return w_key, "workspace"  # 🎯 Tagged as Workspace Global Fallback Key

        # --- TIER 4: Complete Absence of Database Records ---
        # If no custom keys exist anywhere in PostgreSQL, it shifts down to your Server Process Variables
        return None, "system"  # 🎯 Tagged as System Environment Key (Your Master Wallet!)