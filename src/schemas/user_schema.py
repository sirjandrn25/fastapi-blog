
from pydantic import BaseModel
from typing import Any, Optional

class UserBase(BaseModel):
    email:str

class UserCreate(UserBase):
    password:str
    re_password:str




class UserLogin(UserBase):
    password:str
    

class ProfileBase(BaseModel):
    full_name:Optional[str]=None
    address:Optional[str]=None
    contact_no :Optional[str]=None


class UploadAvatar(BaseModel):
    avatar:str

class Profile(ProfileBase):
    pk:int
    avatar:Optional[str]=None
    user_id:int
    class Config:
        orm_mode=True

class UserUpdate(BaseModel):
    is_active:Optional[bool]=None
    is_superuser:Optional[bool]=None
    is_staff:Optional[bool]=None


class User(UserBase):
    pk:int
    is_active:bool
    is_superuser:bool
    is_staff:bool
    profile:Optional[Any]=None
    
    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str

