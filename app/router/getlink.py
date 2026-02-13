from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.service import product_auth
from app.utils.response import wrap_response
from app.crud import product as product_crud
from app.crud.crud4user_products import check_user_product_access

from app.api.dependencies import get_auth_context

router = APIRouter()

@router.get("/products/{product_id}/get-link")
async def get_link(product_id: int, request: Request, db: Session = Depends(get_db), auth_ctx: dict = Depends(get_auth_context)):
 
    ua = request.headers.get("user-agent")
    ip = request.client.host
    tenant_id = auth_ctx["tenant_id"]
    user_id = auth_ctx.get("user_id")
    
    # 🔒 SECURITY CHECK: Verify access before generating link
    if user_id:
        # Check if user has role-based access to this product
        if not check_user_product_access(db, user_id, tenant_id, product_id):
            raise HTTPException(status_code=403, detail="Access denied: You do not have permission to launch this product")
    else:
        # Direct tenant login - Check if tenant has access to this product
        if not product_crud.get_tenant_product_by_id(db, tenant_id, product_id):
            raise HTTPException(status_code=403, detail="Access denied: Tenant is not subscribed to this product")

    result = await product_auth.generate_product_token(product_id, db, ua, ip, tenant_id, user_id)
    return wrap_response(data=result, message="Magic link generated successfully")

@router.get("/auth/verify-token")
async def verify_token(token: str, request: Request, db: Session = Depends(get_db)):
  
    ua = request.headers.get("user-agent")
    ip = request.client.host
    result = await product_auth.verify_product_token(ua, ip, token, db)
    return wrap_response(data=result, message="Token verified successfully")
