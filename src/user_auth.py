from passlib.context import CryptContext
from .schemas import user_schema
from .dependencies import get_db
from sqlalchemy.orm import Session
from fastapi import Depends,HTTPException,status
from .crud import user_crud
from datetime import datetime,timedelta
from typing import Optional
from jose import JWTError, jwt
from .routers import user_router
from fastapi.security.api_key import APIKeyHeader




oauth2_scheme = APIKeyHeader(name="token")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password:str):
    return pwd_context.hash(password)


def verify_password(plain_password:str,hashed_password:str):
    return pwd_context.verify(plain_password,hashed_password)


def register_validation(user:user_schema.UserCreate,db:Session=Depends(get_db)):
    if user_crud.get_user_by_email(db=db,user_email=user.email):
        raise HTTPException(
            status_code=400,
            detail={"email":"this email id already exists!!"}
        )
    elif user.password != user.re_password:
        raise HTTPException(
            status_code=400,
            detail={"re_password":"both password doesn't match"}
        )
    elif len(user.password)<8:
        raise HTTPException(
            status_code = 400,
            detail={"password":"at least 8 charecters are required !!"}
        )
    elif user.password.isdigit():
        raise HTTPException(
            status_code=400,
            detail = {"password":"only numeric values are not allowed"}
        )
    return user

def authenticate_user(user:user_schema.UserLogin,db:Session=Depends(get_db)):
    user_db = user_crud.get_user_by_email(db=db,user_email=user.email)
    if not user_db:
        raise HTTPException(
            status_code=400,
            detail={"email":"this email id is not exists !!"}
        )
    elif not verify_password(plain_password=user.password,hashed_password=user_db.hashed_password):
        raise HTTPException(
            status_code=400,
            detail={"password":"password doesn't match !!"}
        )
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, user_router.SECRET_KEY, algorithm=user_router.ALGORITHM)
    return encoded_jwt


async def get_current_user(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db)):
    
    credential_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate":"Bearer"}

    )
    token_type_value = token.split(" ")
    # print(token_type_value)
    if token_type_value[0] !="Bearer":
        raise credential_exception
    

    try:
        payload = jwt.decode(token_type_value[1],user_router.SECRET_KEY,algorithms=[user_router.ALGORITHM])
        email:str = payload.get("user")
        if email is None:
            raise credential_exception
    except JWTError:
        raise credential_exception
    user = user_crud.get_user_by_email(user_email=email,db=db)
    if not user:
        raise credential_exception
    return user

async def get_current_active_user(user:Session=Depends(get_current_user)):
    if not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="User is not active",
            headers={"WWW-Authenticate":"Bearer"}
        )
    return user
    