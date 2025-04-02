from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv
import logging
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

# Load environment variables
load_dotenv(override=True)

# Configure logging
logger = logging.getLogger(__name__)

# Load API key from environment variable
API_KEY = os.getenv("API_KEY")

# Security scheme
security = HTTPBearer()

# List of paths that don't require authentication
PUBLIC_PATHS = ["/", "/health", "/docs", "/openapi.json", "/redoc", "/favicon.ico"]

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify the Bearer token against the expected API key.
    
    Args:
        credentials: The authorization credentials containing the token
        
    Returns:
        The token if valid
        
    Raises:
        HTTPException: If the token is invalid
    """

	# Check if API_KEY is configured
    if not API_KEY:
        logger.warning("API_KEY is not configured. Please set up the API_KEY.")
        raise HTTPException(
            status_code=401,
            detail="API_KEY is not configured. Please set up the API_KEY.",
        )

    if credentials.scheme != "Bearer":
        logger.warning(f"Invalid authentication scheme: {credentials.scheme}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme. Expected 'Bearer'"
        )
    
    if credentials.credentials != API_KEY:
        logger.warning("Invalid token provided")
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    
    return credentials.credentials

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce Bearer token authentication on protected routes."""
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ):
        """
        Process each request and enforce authentication for protected paths.
        
        Args:
            request: The incoming request
            call_next: Function to call the next middleware
            
        Returns:
            The response from the next middleware
        """
        # Skip authentication for public paths
        path = request.url.path
        if any(path.startswith(public_path) for public_path in PUBLIC_PATHS):
            return await call_next(request)
        
        # Check for authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logger.warning(f"Unauthorized access attempt to {path}")
            return JSONResponse(
                status_code=401, 
                content={"detail": "Authentication required"},
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Validate token format
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                logger.warning(f"Invalid authentication scheme: {scheme}")
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid authentication scheme. Expected 'Bearer'"}
                )
            
            # Validate token
            if token != API_KEY:
                logger.warning("Invalid token provided")
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid token"}
                )
        except ValueError:
            logger.warning("Invalid authorization header format")
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid authorization header format"}
            )
        
        # If authentication is successful, proceed to the next middleware
        return await call_next(request)