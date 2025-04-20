from pydantic import ConfigDict, BaseModel, EmailStr


class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    is_admin: bool
    
    model_config = ConfigDict(from_attributes=True)

class AdminUserRead(UserBase):
    id: int
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)
