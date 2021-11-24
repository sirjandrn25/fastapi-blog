from sqlalchemy.orm import Session
from ..models import user_model
from ..schemas import user_schema
from ..user_auth import get_hashed_password


def get_user_by_id(db:Session,user_id:int):
    return db.query(user_model.User).filter(user_model.User.pk == user_id).first()

def get_user_by_email(db:Session,user_email:str):
    return db.query(user_model.User).filter(user_model.User.email==user_email).first()

def get_users(db:Session,limit:int,skip:int):
    return db.query(user_model.User).limit(limit).offset(skip).all()

def create_user(db:Session,user:user_schema.UserCreate):
    user_dict = user.dict()
    user_dict['hashed_password'] = get_hashed_password(user_dict.pop("password"))
    user_dict.pop("re_password")
    
    user_db = user_model.User(**user_dict)
  
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    
    return user_db

def update_user_profile(db:Session,profile:user_schema.ProfileBase,user:Session):
    profile_db = db.query(user_model.Profile).filter(user_model.Profile.user_id==user.pk).first()
    if not profile_db:
        return False
    profile_dict = profile.dict()
    for key,value in profile_dict.items():
        setattr(profile_db,key,value)
    db.add(profile_db)
    db.commit()
    db.refresh(profile_db)
    return profile_db


def upload_avatar(db:Session,url:str,user:Session):
    profile_db = user.profile
    setattr(profile_db,'avatar',url)
    db.add(profile_db)
    db.commit()
    db.refresh(profile_db)
    return True



def user_profile_create(db:Session,user:Session):
    try:
        profile_db = user_model.Profile(**{"user_id":user.pk})
    except:
        return False
    db.add(profile_db)
    db.commit()
    db.refresh(profile_db)
    return profile_db
    
def user_update_by_admin(db:Session,user:user_schema.UserUpdate,user_db:Session):
    user_dict = user.dict()
    for key,value in user_dict:
        if not value:
            setattr(user_db,key,value)
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db



