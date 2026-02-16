from sqlalchemy.orm import Session
from app.models.models import TenantProductMapping, Tenant, Product
from fastapi import HTTPException
from app.schemas.tenant_product_map import TenantProductMapInDBBase, TenantProductMapCreate


from typing import Optional


def get_all_tenant_product_maps(db: Session, tenant_id: int, product_id: Optional[int] = None):
    query = db.query(TenantProductMapping).filter(TenantProductMapping.tenant_id == tenant_id)
    if product_id:
        query = query.filter(TenantProductMapping.product_id == product_id)
    return query.all()


def get_tenant_product_map_by_id(db: Session, tenant_product_map_id: int, tenant_id: int):
    return db.query(TenantProductMapping).filter(
        TenantProductMapping.id == tenant_product_map_id,
        TenantProductMapping.tenant_id == tenant_id
    ).first()

def create_tenant_product_map(db: Session, tenant_product_map: TenantProductMapCreate, tenant_id: int):
    mapping_data = tenant_product_map.model_dump()
    mapping_data["tenant_id"] = tenant_id
    
    # Check if Product exists
    product = db.query(Product).filter(Product.product_id == mapping_data["product_id"]).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check for existing mapping
    existing_mapping = db.query(TenantProductMapping).filter(
        TenantProductMapping.tenant_id == tenant_id,
        TenantProductMapping.product_id == mapping_data["product_id"]
    ).first()
    if existing_mapping:
        raise HTTPException(status_code=400, detail="This tenant is already subscribed to this product")

    db_tenant_product_map = TenantProductMapping(**mapping_data)
    db.add(db_tenant_product_map)
    db.commit()
    db.refresh(db_tenant_product_map)
    return db_tenant_product_map


def delete_tenant_product_map(db: Session, tenant_product_map_id: int, tenant_id: int):
    db_tenant_product_map = db.query(TenantProductMapping).filter(
        TenantProductMapping.id == tenant_product_map_id,
        TenantProductMapping.tenant_id == tenant_id
    ).first()
    if db_tenant_product_map:
        db.delete(db_tenant_product_map)
        db.commit()
    return db_tenant_product_map

