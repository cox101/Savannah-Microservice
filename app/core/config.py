import os
from typing import Optional


class Settings:
    def __init__(self):
        # Database
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./savannah.db")
        
        # Security
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # Auth0 / OpenID Connect
        self.auth0_domain = os.getenv("AUTH0_DOMAIN", "your-auth0-domain.auth0.com")
        self.auth0_audience = os.getenv("AUTH0_AUDIENCE", "your-api-identifier")
        self.auth0_client_id = os.getenv("AUTH0_CLIENT_ID", "your-client-id")
        self.auth0_client_secret = os.getenv("AUTH0_CLIENT_SECRET", "your-client-secret")
        
        # Africa's Talking
        self.africas_talking_username = os.getenv("AFRICAS_TALKING_USERNAME", "sandbox")
        self.africas_talking_api_key = os.getenv("AFRICAS_TALKING_API_KEY", "your-api-key")
        self.africas_talking_sandbox = os.getenv("AFRICAS_TALKING_SANDBOX", "true").lower() == "true"
        
        # Application
        self.debug = os.getenv("DEBUG", "true").lower() == "true"
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))


settings = Settings()