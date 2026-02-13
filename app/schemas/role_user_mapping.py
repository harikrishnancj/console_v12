from pydantic import BaseModel
from typing import Optional

class RoleUserMappingBase(BaseModel):
    role_id: int
    user_id: int
    tenant_id: int

class RoleUserMappingCreate(RoleUserMappingBase):
    pass

class RoleUserMappingUpdate(BaseModel):
    role_id: Optional[int] = None
    user_id: Optional[int] = None
    tenant_id: Optional[int] = None

class RoleUserMappingInDBBase(RoleUserMappingBase):
    id: int

    class Config:
        from_attributes = True
