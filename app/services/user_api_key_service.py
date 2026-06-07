from typing import Optional
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