from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
import httpx
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()


class AuthService:
    def __init__(self):
        self.domain = settings.auth0_domain
        self.audience = settings.auth0_audience
        self.algorithm = "RS256"
        self.jwks_url = f"https://{self.domain}/.well-known/jwks.json"
        self._jwks_cache = None
        self._jwks_cache_time = None

    async def get_jwks(self):
        """Get JWKS from Auth0 with caching"""
        now = datetime.utcnow()
        
        # Cache JWKS for 1 hour
        if (self._jwks_cache is None or 
            self._jwks_cache_time is None or 
            (now - self._jwks_cache_time).total_seconds() > 3600):
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(self.jwks_url)
                    response.raise_for_status()
                    self._jwks_cache = response.json()
                    self._jwks_cache_time = now
            except Exception as e:
                logger.error(f"Failed to fetch JWKS: {e}")
                if self._jwks_cache is None:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Unable to verify token"
                    )
        
        return self._jwks_cache

    async def verify_token(self, token: str) -> dict:
        """Verify JWT token from Auth0"""
        try:
            # Get the signing key
            jwks = await self.get_jwks()
            
            # Decode token header to get key ID
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = {}
            
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
                    break
            
            if rsa_key:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=[self.algorithm],
                    audience=self.audience,
                    issuer=f"https://{self.domain}/"
                )
                return payload
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unable to find appropriate key"
                )
                
        except JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token verification failed"
            )


auth_service = AuthService()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = await auth_service.verify_token(token)
    return payload


# Optional: Create a mock auth service for development/testing
class MockAuthService:
    """Mock authentication service for development"""
    
    async def verify_token(self, token: str) -> dict:
        # In development, accept any token and return a mock user
        if settings.debug and token == "mock-token":
            return {
                "sub": "mock-user-123",
                "email": "test@example.com",
                "name": "Test User"
            }
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


async def get_current_user_mock(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Mock dependency for development"""
    token = credentials.credentials
    mock_auth = MockAuthService()
    payload = await mock_auth.verify_token(token)
    return payload