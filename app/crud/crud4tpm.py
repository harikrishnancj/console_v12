from sqlalchemy.orm import Session
from app.models.models import TenantProductMapping
from app.schemas.tenant_product_map import TenantProductMapInDBBase, TenantProductMapCreate, TenantProductMapUpdate


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

