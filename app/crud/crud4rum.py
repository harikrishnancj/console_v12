from fastapi import HTTPException
from app.models.models import RoleUserMapping, User, Role
from app.schemas.role_user_mapping import RoleUserMappingCreate, RoleUserMappingUpdate

from typing import Optional

def create_role_user_mapping(db: Session, role_user_mapping: RoleUserMappingCreate, tenant_id: int):
    # Enforce tenant_id from session
    mapping_data = role_user_mapping.model_dump()
    mapping_data["tenant_id"] = tenant_id
    
    # Verify User exists in this Tenant
    user = db.query(User).filter(User.user_id == mapping_data["user_id"], User.tenant_id == tenant_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found in this tenant")
        
    # Verify Role exists in this Tenant
    role = db.query(Role).filter(Role.role_id == mapping_data["role_id"], Role.tenant_id == tenant_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found in this tenant")

    db_role_user_mapping = RoleUserMapping(**mapping_data)
    db.add(db_role_user_mapping)
    db.commit()
    db.refresh(db_role_user_mapping)
    return db_role_user_mapping


def get_role_user_mapping_by_id(db: Session, role_user_mapping_id: int, tenant_id: int):
    return db.query(RoleUserMapping).filter(
        RoleUserMapping.id == role_user_mapping_id,
        RoleUserMapping.tenant_id == tenant_id
    ).first()


def get_all_role_user_mappings(db: Session, tenant_id: int, user_id: Optional[int] = None, role_id: Optional[int] = None):
    query = db.query(RoleUserMapping).filter(RoleUserMapping.tenant_id == tenant_id)
    
    if user_id:
        query = query.filter(RoleUserMapping.user_id == user_id)
    if role_id:
        query = query.filter(RoleUserMapping.role_id == role_id)
        
    return query.all()


def update_role_user_mapping(db: Session, role_user_mapping_id: int, role_user_mapping: RoleUserMappingUpdate, tenant_id: int):
    db_role_user_mapping = db.query(RoleUserMapping).filter(
        RoleUserMapping.id == role_user_mapping_id,
        RoleUserMapping.tenant_id == tenant_id
    ).first()
    if not db_role_user_mapping:
        return None
    
    update_data = role_user_mapping.model_dump(exclude_unset=True)
    
    # If updating user_id, verify ownership
    if "user_id" in update_data:
        user = db.query(User).filter(User.user_id == update_data["user_id"], User.tenant_id == tenant_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found in this tenant")
            
    # If updating role_id, verify ownership
    if "role_id" in update_data:
        role = db.query(Role).filter(Role.role_id == update_data["role_id"], Role.tenant_id == tenant_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found in this tenant")

    # Force tenant_id consistency
    update_data["tenant_id"] = tenant_id

    for key, value in update_data.items():
        setattr(db_role_user_mapping, key, value)
    
    db.commit()
    db.refresh(db_role_user_mapping)
    return db_role_user_mapping


def delete_role_user_mapping(db: Session, role_user_mapping_id: int, tenant_id: int):
    db_role_user_mapping = db.query(RoleUserMapping).filter(
        RoleUserMapping.id == role_user_mapping_id,
        RoleUserMapping.tenant_id == tenant_id
    ).first()
    if not db_role_user_mapping:
        return None
    db.delete(db_role_user_mapping)
    db.commit()
    return db_role_user_mapping
