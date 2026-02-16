from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud import product as product_crud
from app.schemas.product import ProductInDBBase, ProductCreate, ProductUpdate
from app.utils.response import wrap_response
from app.schemas.base import BaseResponse

router = APIRouter()

@router.post("/products", response_model=BaseResponse[ProductInDBBase])
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    result = product_crud.create_product(schema=product, db=db)
    return wrap_response(data=result, message="Product created successfully")

@router.put("/products/{product_id}", response_model=BaseResponse[ProductInDBBase])
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    result = product_crud.update_product(schema=product, db=db, product_id=product_id)
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return wrap_response(data=result, message="Product updated successfully")

@router.delete("/products/{product_id}", response_model=BaseResponse[ProductInDBBase])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    result = product_crud.delete_product(db=db, product_id=product_id)
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return wrap_response(data=result, message="Product deleted successfully")


