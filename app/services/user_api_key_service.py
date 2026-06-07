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
        user_id: Optional[UUID] = None, 
        workspace_id: Optional[UUID] = None,
        agent_id: Optional[UUID] = None,
        model_version: Optional[str] = None
    ) -> UserAPIKey:
        """
        Encrypts the raw API key and saves it into the database.
        If a key already exists under the matching unique constraints 
        (Agent-specific, Workspace-specific, or User-specific), it updates cleanly.
        """
        provider_clean = provider.lower().strip()
        model_version_clean = model_version.strip() if model_version else None
        encrypted_str = encrypt_api_key(raw_key)

        # Look for an existing key match based on our new 3-tier tracking constraints
        if agent_id:
            # Tier 1: Agent specific keys are unique per agent + provider
            stmt = select(UserAPIKey).where(
                and_(UserAPIKey.agent_id == agent_id, UserAPIKey.provider == provider_clean)
            )
        elif workspace_id:
            # Tier 2: Workspace keys are unique per workspace + provider + model dropdown selection
            stmt = select(UserAPIKey).where(
                and_(
                    UserAPIKey.workspace_id == workspace_id, 
                    UserAPIKey.provider == provider_clean,
                    UserAPIKey.model_version == model_version_clean
                )
            )
        else:
            # User level fallback key context
            stmt = select(UserAPIKey).where(
                and_(
                    UserAPIKey.user_id == user_id, 
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
        user_id: Optional[UUID] = None, 
        workspace_id: Optional[UUID] = None,
        agent_id: Optional[UUID] = None,
        model_version: Optional[str] = None
    ) -> Optional[str]:
        """
        Fetches the encrypted API key from the database using precise routing targets
        and returns the fully decrypted plain text token string ready for execution runtime.
        """
        provider_clean = provider.lower().strip()
        model_version_clean = model_version.strip() if model_version else None

        if agent_id:
            stmt = select(UserAPIKey).where(
                and_(UserAPIKey.agent_id == agent_id, UserAPIKey.provider == provider_clean)
            )
        elif workspace_id:
            stmt = select(UserAPIKey).where(
                and_(
                    UserAPIKey.workspace_id == workspace_id, 
                    UserAPIKey.provider == provider_clean,
                    UserAPIKey.model_version == model_version_clean
                )
            )
        else:
            stmt = select(UserAPIKey).where(
                and_(
                    UserAPIKey.user_id == user_id, 
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
        user_id: Optional[UUID] = None, 
        workspace_id: Optional[UUID] = None,
        agent_id: Optional[UUID] = None,
        model_version: Optional[str] = None
    ) -> bool:
        """
        Deletes a specific targeted provider API key configuration row cleanly.
        """
        provider_clean = provider.lower().strip()
        model_version_clean = model_version.strip() if model_version else None

        if agent_id:
            stmt = select(UserAPIKey).where(
                and_(UserAPIKey.agent_id == agent_id, UserAPIKey.provider == provider_clean)
            )
        elif workspace_id:
            stmt = select(UserAPIKey).where(
                and_(
                    UserAPIKey.workspace_id == workspace_id, 
                    UserAPIKey.provider == provider_clean,
                    UserAPIKey.model_version == model_version_clean
                )
            )
        else:
            stmt = select(UserAPIKey).where(
                and_(
                    UserAPIKey.user_id == user_id, 
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