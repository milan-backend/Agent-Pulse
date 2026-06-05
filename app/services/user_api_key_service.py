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
        workspace_id: Optional[UUID] = None
    ) -> UserAPIKey:
        """
        Encrypts the raw API key and saves it into the database.
        If a key already exists for this provider under the given user or workspace,
        it updates the record cleanly.
        """
        provider_clean = provider.lower().strip()
        encrypted_str = encrypt_api_key(raw_key)

        # Look for an existing key match to prevent duplication errors
        if workspace_id:
            stmt = select(UserAPIKey).where(
                and_(UserAPIKey.workspace_id == workspace_id, UserAPIKey.provider == provider_clean)
            )
        else:
            stmt = select(UserAPIKey).where(
                and_(UserAPIKey.user_id == user_id, UserAPIKey.provider == provider_clean)
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
                provider=provider_clean,
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
        workspace_id: Optional[UUID] = None
    ) -> Optional[str]:
        """
        Fetches the encrypted API key from the database and returns the fully 
        decrypted plain text token string ready for execution runtime.
        """
        provider_clean = provider.lower().strip()

        if workspace_id:
            stmt = select(UserAPIKey).where(
                and_(UserAPIKey.workspace_id == workspace_id, UserAPIKey.provider == provider_clean)
            )
        else:
            stmt = select(UserAPIKey).where(
                and_(UserAPIKey.user_id == user_id, UserAPIKey.provider == provider_clean)
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
        workspace_id: Optional[UUID] = None
    ) -> bool:
        """
        Deletes a specific provider API key for a user or workspace configuration.
        """
        provider_clean = provider.lower().strip()

        if workspace_id:
            stmt = select(UserAPIKey).where(
                and_(UserAPIKey.workspace_id == workspace_id, UserAPIKey.provider == provider_clean)
            )
        else:
            stmt = select(UserAPIKey).where(
                and_(UserAPIKey.user_id == user_id, UserAPIKey.provider == provider_clean)
            )

        record = db.execute(stmt).scalars().first()

        if record:
            db.delete(record)
            db.commit()
            return True
        return False