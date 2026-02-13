from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_user, get_tenant_id
from app.crud.crud4user import update_user as crud_update_user, get_user as crud_get_user
from app.crud import crud4tent as user_crud
from app.schemas.user import UserUpdate
from app.crud.crud4user_products import get_user_products as crud_get_user_products
from app.schemas.product import ProductInDBBase
from app.utils.response import wrap_response
from app.schemas.base import BaseResponse
from typing import List

router = APIRouter()


@router.get("/user-products", response_model=BaseResponse[List[ProductInDBBase]])
def get_user_products_endpoint(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    result = crud_get_user_products(db, user_id, tenant_id)
    return wrap_response(data=result, message="User products fetched successfully")

@router.put("/update-user")
def update_user_endpoint(user_id: int, user: UserUpdate, db: Session = Depends(get_db), tenant_id: int = Depends(get_tenant_id)):
    result = crud_update_user(db, user_id, user, tenant_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return wrap_response(data=result, message="User updated successfully")

@router.get("/get-user")
def get_user_endpoint(user_id: int, db: Session = Depends(get_db), tenant_id: int = Depends(get_tenant_id)):
    result = crud_get_user(db, user_id, tenant_id)
    return wrap_response(data=result, message="User details fetched successfully")

