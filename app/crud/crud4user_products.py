from sqlalchemy.orm import Session
from app.models.models import RoleUserMapping, AppRoleMapping, Product
from typing import List

def get_user_products(db: Session, user_id: int, tenant_id: int) -> List[Product]:
    """
    Returns a unique list of products accessible to the user via their roles.
    Includes products that are mapped to any of the roles assigned to the user.
    """
    return (
        db.query(Product)
        .join(AppRoleMapping, AppRoleMapping.product_id == Product.product_id)
        .join(RoleUserMapping, RoleUserMapping.role_id == AppRoleMapping.role_id)
        .filter(
            RoleUserMapping.user_id == user_id,
            RoleUserMapping.tenant_id == tenant_id,
            AppRoleMapping.tenant_id == tenant_id
        )
        .distinct()
        .all()
    )

def check_user_product_access(db: Session, user_id: int, tenant_id: int, product_id: int) -> bool:
    """
    Verifies if a specific user has access to a specific product via their roles.
    Returns True if any user role is mapped to the product.
    """
    count = (
        db.query(Product.product_id)
        .join(AppRoleMapping, AppRoleMapping.product_id == Product.product_id)
        .join(RoleUserMapping, RoleUserMapping.role_id == AppRoleMapping.role_id)
        .filter(
            RoleUserMapping.user_id == user_id,
            RoleUserMapping.tenant_id == tenant_id,
            AppRoleMapping.tenant_id == tenant_id,
            Product.product_id == product_id
        )
        .count()
    )
    return count > 0
