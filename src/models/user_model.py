
from ..database import Base
from sqlalchemy import Column,String,Integer,Boolean,ForeignKey
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"
    pk = Column(Integer,primary_key=True,index=True)
    email = Column(String,index=True,unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean,default=True)
    is_superuser = Column(Boolean,default=False)
    is_staff = Column(Boolean,default=False)
    profile = relationship("Profile",back_populates="user",uselist=False)

class Profile(Base):
    __tablename__ = "profiles"
    pk = Column(Integer,primary_key=True,index=True)
    full_name = Column(String,index=True)
    address = Column(String)
    avatar = Column(String)
    contact_no = Column(String)
    user_id = Column(Integer,ForeignKey("users.pk"),unique=True)
    user = relationship("User",back_populates="profile")


