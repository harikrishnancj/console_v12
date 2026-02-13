import secrets
import json
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.redis import redis_client
from app.models.models import Product, TokenUsageStorage

async def generate_product_token(product_id: int, db: Session, user_agent: str, client_ip: str, tenant_id: int, user_id: int = None):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    token = secrets.token_urlsafe(32)
    
    data = {
        "pid": product_id, 
        "ua": user_agent,
        "ip": client_ip,
        "tid": tenant_id,
        "uid": user_id
    }
    redis_client.setex(f"p_access:{token}", 10, json.dumps(data))
    
    # Store in database
    db_token = TokenUsageStorage(
        token=token,
        tenant_id=tenant_id,
        user_id=user_id,
        product_id=product_id
    )
    db.add(db_token)
    db.commit()
    
    # Simple logic to append token to URL
    separator = "&" if "?" in product.launch_url else "?"
    full_url = f"{product.launch_url}{separator}magic_token={token}"
    
    return full_url

async def verify_product_token(user_agent: str, client_ip: str, token: str, db: Session):
    """
    Verifies the magic token and burns it immediately (one-time use).
    Prevents URL reuse by deleting the token from Redis.
    """
    try:
        # getdel is available in Redis 6.2+
        raw_data = redis_client.getdel(f"p_access:{token}")
    except AttributeError:
        # Fallback for older Redis versions
        raw_data = redis_client.get(f"p_access:{token}")
        if raw_data:
            redis_client.delete(f"p_access:{token}")

    if not raw_data:
        raise HTTPException(status_code=400, detail="Token expired, invalid, or already used")
    
    stored = json.loads(raw_data)
    product = db.query(Product).filter(Product.product_id == stored["pid"]).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if stored.get("ua") != user_agent:
        raise HTTPException(status_code=403, detail="Security error: Use the same browser")
    
    if stored.get("ip") != client_ip:
        raise HTTPException(status_code=403, detail="Security error: Use the same network/IP")
    
    return {"status": "success", "valid": True}