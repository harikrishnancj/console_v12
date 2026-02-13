from fastapi import HTTPException, Request
from app.core.security import verify_token
from app.core.redis import redis_client
import json


def _parse_authorization_header(request: Request) -> str:
    """Parse and validate Authorization header, returning the token."""
    auth = request.headers.get("Authorization")
    if not auth:
        raise HTTPException(401, "Missing token")
    
    parts = auth.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(401, "Invalid authorization header format")
    
    return parts[1]


def get_current_user(request: Request):
    session_id = _parse_authorization_header(request)
    
    # 1. Lookup Session in Redis
    vault_json = redis_client.get(f"session:{session_id}")
    if not vault_json:
        raise HTTPException(401, "Invalid Session")
        
    # 2. Open Vault
    try:
        vault = json.loads(vault_json)
    except json.JSONDecodeError:
        raise HTTPException(401, "Invalid Session Data")

    # 3. Verify Internal Access Token 
    # (This ensures expiration is respected even if session key exists)
    access_token = vault.get("access_token")
    payload = verify_token(access_token)
    
    if not payload:
        # Internal token expired, so session is invalid
        raise HTTPException(401, "Session Expired")

    if payload.get("type") != "access":
        raise HTTPException(401, "Invalid token type")
        
    # 4. Return User ID
    user_id = vault.get("user_id")
    if user_id is None:
        raise HTTPException(401, "User ID not found in session")

    try:
        return int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(401, "Invalid User ID format in session")


def get_tenant_id(request: Request):
    session_id = _parse_authorization_header(request)
    
    # 1. Lookup Session
    vault_json = redis_client.get(f"session:{session_id}")
    if not vault_json:
        raise HTTPException(401, "Invalid Session")
        
    try:
        vault = json.loads(vault_json)
    except:
        raise HTTPException(401, "Invalid Session Data")

    # 2. Verify Token
    access_token = vault.get("access_token")
    payload = verify_token(access_token)
    
    if not payload:
         raise HTTPException(401, "Session Expired")
    
    if payload.get("type") != "access":
        raise HTTPException(401, "Invalid token type")
    
    # 3. Extract Tenant ID
    tenant_id = vault.get("tenant_id")
    
    if tenant_id is None:
        # Fallback/Legacy Logic inside vault context if needed
        tenant_id = payload.get("tenant_id")
        
    if tenant_id is None:
        # Check if role is tenant and user_id is the tenant_id
        role = vault.get("role")
        if role == "tenant":
             tenant_id = vault.get("user_id")
             
    if tenant_id is None:
        raise HTTPException(401, "Tenant ID not found in session")
        
    try:
        return int(tenant_id)
    except (ValueError, TypeError):
        raise HTTPException(401, "Invalid Tenant ID format in session")


def get_auth_context(request: Request):
    session_id = _parse_authorization_header(request)
    
    vault_json = redis_client.get(f"session:{session_id}")
    if not vault_json:
        raise HTTPException(401, "Invalid Session")
        
    try:
        vault = json.loads(vault_json)
    except:
        raise HTTPException(401, "Invalid Session Data")

    access_token = vault.get("access_token")
    payload = verify_token(access_token)
    
    if not payload:
         raise HTTPException(401, "Session Expired")
    
    if payload.get("type") != "access":
        raise HTTPException(401, "Invalid token type")
    
    tenant_id = vault.get("tenant_id")
    user_id = vault.get("user_id") if vault.get("type") == "user" else None
    
    # Fallback/Legacy Logic
    if tenant_id is None:
        tenant_id = payload.get("tenant_id")
        
    if tenant_id is None and vault.get("role") == "tenant":
        tenant_id = vault.get("user_id")

    if tenant_id is None:
        raise HTTPException(401, "Tenant ID not found in session")
        
    return {
        "tenant_id": int(tenant_id),
        "user_id": int(user_id) if user_id else None
    }
