from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.models import AppRoleMapping, Role
from app.schemas.app_role_mapping import AppRoleMappingCreate, AppRoleMappingUpdate, AppRoleMappingInDBBase

from typing import Optional

def create_app_role_mapping(db: Session, app_role_mapping: AppRoleMappingCreate, tenant_id: int):
    # Enforce tenant_id from session
    mapping_data = app_role_mapping.model_dump()
    mapping_data["tenant_id"] = tenant_id
    
    # Verify Role exists in this Tenant
    role = db.query(Role).filter(Role.role_id == mapping_data["role_id"], Role.tenant_id == tenant_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found in this tenant")

    db_app_role_mapping = AppRoleMapping(**mapping_data)
    db.add(db_app_role_mapping)
    db.commit()
    db.refresh(db_app_role_mapping)
    return db_app_role_mapping


def get_all_app_role_mappings(db: Session, tenant_id: int, product_id: Optional[int] = None, role_id: Optional[int] = None):
    query = db.query(AppRoleMapping).filter(AppRoleMapping.tenant_id == tenant_id)
    
    if product_id:
        query = query.filter(AppRoleMapping.product_id == product_id)
    if role_id:
        query = query.filter(AppRoleMapping.role_id == role_id)
        
    return query.all()

def get_app_role_mapping_by_id(db: Session, app_role_mapping_id: int, tenant_id: int):
    return db.query(AppRoleMapping).filter(
        AppRoleMapping.id == app_role_mapping_id,
        AppRoleMapping.tenant_id == tenant_id
    ).first()

def update_app_role_mapping(db: Session, app_role_mapping_id: int, app_role_mapping: AppRoleMappingUpdate, tenant_id: int):
    db_app_role_mapping = db.query(AppRoleMapping).filter(
        AppRoleMapping.id == app_role_mapping_id,
        AppRoleMapping.tenant_id == tenant_id
    ).first()
    if db_app_role_mapping is None:
        raise HTTPException(status_code=404, detail="App role mapping not found")
    
    update_data = app_role_mapping.model_dump(exclude_unset=True)
    
    # If updating role_id, verify ownership
    if "role_id" in update_data:
        role = db.query(Role).filter(Role.role_id == update_data["role_id"], Role.tenant_id == tenant_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found in this tenant")

    # Force tenant_id consistency
    update_data["tenant_id"] = tenant_id

    for key, value in update_data.items():
        setattr(db_app_role_mapping, key, value)
    
    db.commit()
    db.refresh(db_app_role_mapping)
    return db_app_role_mapping

def delete_app_role_mapping(db: Session, app_role_mapping_id: int, tenant_id: int):
    db_app_role_mapping = db.query(AppRoleMapping).filter(
        AppRoleMapping.id == app_role_mapping_id,
        AppRoleMapping.tenant_id == tenant_id
    ).first()
    if db_app_role_mapping is None:
        raise HTTPException(status_code=404, detail="App role mapping not found")
    db.delete(db_app_role_mapping)
    db.commit()
    return db_app_role_mapping
