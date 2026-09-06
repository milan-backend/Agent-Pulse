import jwt
from jwt import PyJWKClient
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.workspace_config import WorkspaceConfig

class JWTGuardService:
    # Cache the JWK clients in memory so we don't spam the company's Auth0/Cognito 
    # servers on every single chat message.
    _jwks_clients = {}

    @classmethod
    def get_jwks_client(cls, jwks_url: str) -> PyJWKClient:
        """Retrieves or creates a cached JWKS client for the company's public key URL."""
        if jwks_url not in cls._jwks_clients:
            cls._jwks_clients[jwks_url] = PyJWKClient(jwks_url)
        return cls._jwks_clients[jwks_url]

    @classmethod
    def verify_identity_token(cls, db: Session, workspace_id: str, token: str) -> str:
        """
        The Iron Wall: Validates the frontend token using the company's public key
        and returns the mathematically guaranteed user_id.
        """
        # 1. Look up the company's Vault configuration
        config = db.query(WorkspaceConfig).filter(WorkspaceConfig.workspace_id == workspace_id).first()
        
        if not config or not config.jwks_url:
            raise HTTPException(
                status_code=404, 
                detail="Workspace configuration or JWKS URL not found."
            )
            
        # 2. Initialize the client to fetch their public keys
        jwks_client = cls.get_jwks_client(config.jwks_url)
        
        try:
            # 3. Get the specific public signing key for this token
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            
            # 4. Cryptographically decode and verify the token
            # Note: verify_aud is False here for development, but in production 
            # you would enforce audience validation for strict security.
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={"verify_aud": False} 
            )
            
            # 5. Extract the verified User ID (Standard OIDC claim is 'sub' for subject)
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=401, 
                    detail="Token does not contain a 'sub' (subject) claim."
                )
                
            return user_id
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Identity token has expired.")
        except jwt.InvalidTokenError as e:
            # If a hacker tampers with the token, it fails here instantly.
            raise HTTPException(status_code=401, detail=f"Invalid identity token: {str(e)}")