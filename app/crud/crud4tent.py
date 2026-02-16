from app.models.models import User, RoleUserMapping, Role
from app.schemas.user import UserCreate, UserUpdate
from fastapi import HTTPException
from app.core.security import hash_password
from sqlalchemy.orm import Session, selectinload, joinedload
from typing import Optional, List, Dict, Any

def get_user_by_id(db: Session, user_id: int, tenant_id: int):
    return db.query(User).filter(User.user_id == user_id, User.tenant_id == tenant_id).first()

def create_user(db: Session, user: UserCreate, tenant_id: int):
    # Check if email is already taken in this tenant
    existing_user = db.query(User).filter(User.email == user.email, User.tenant_id == tenant_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists in this tenant")

    hashed_password = hash_password(user.password)
    db_user = User(
        username=user.username, 
        email=user.email,
        hashed_password=hashed_password,
        tenant_id=tenant_id,
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int, tenant_id: int):
    user = db.query(User).filter(User.user_id == user_id, User.tenant_id == tenant_id).first()


    if not user:
        return None
    db.delete(user)
    db.commit()
    return user

def get_all_users(db: Session, tenant_id: int, name: Optional[str] = None, email: Optional[str] = None):
    query = (
        db.query(User)
        .options(
            selectinload(User.user_roles)
            .joinedload(RoleUserMapping.role)
        )
        .filter(User.tenant_id == tenant_id)
    )
    
    if name:
        query = query.filter(User.username.ilike(f"%{name}%"))
    
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))

    users = query.all()

    # Optimized aggregation using list comprehension
    result = []
    for user in users:
        result.append({
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "tenant_id": user.tenant_id,
            # Get unique role names, filtering to ensure we only get roles for THIS tenant
            "roles": list(set([
                mapping.role.role_name 
                for mapping in user.user_roles 
                if mapping.role and mapping.role.tenant_id == tenant_id
            ]))
        })

    return result