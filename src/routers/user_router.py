
from fastapi import APIRouter,Depends,HTTPException,File,UploadFile

from ..dependencies import get_db
from sqlalchemy.orm import Session
from ..crud import user_crud
from ..schemas import user_schema
from typing import List

from ..user_auth import authenticate_user, register_validation,create_access_token,get_current_active_user
from datetime import timedelta
import secrets


router = APIRouter()
FILEPATH = './static/avatar/'


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.get("/",response_model=List[user_schema.User])
async def read_users(limit:int=100,skip:int=0,db:Session=Depends(get_db)):
    return user_crud.get_users(limit=limit,skip=skip,db=db)

@router.post("/",response_model=user_schema.User)
async def create_user(user:user_schema.UserCreate=Depends(register_validation),db:Session=Depends(get_db)):
    try:
        user_db = user_crud.create_user(user=user,db=db)
    except:
        raise HTTPException(
            status_code=400,
            detail="something wrong"
        )
    if not user_crud.user_profile_create(db=db,user=user_db):
        raise HTTPException(
            status_code=400,
            detail="profile is already created !!"
        )
    
    #user_db = user_crud.get_user_by_id(user_id=user_db.pk,db=db)

    return user_db

@router.post("/token",response_model=user_schema.Token)
async def login_for_access_token(user:user_schema.UserLogin=Depends(authenticate_user)):

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user":user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

    


@router.get("/me",response_model=user_schema.User)
async def user_detail(current_user:Session=Depends(get_current_active_user)):
    return current_user

@router.patch("/me/update_profile",response_model=user_schema.Profile)
async def update_user_profile(profile:user_schema.ProfileBase,current_user:Session=Depends(get_current_active_user),db:Session=Depends(get_db)):
    profile_db = user_crud.update_user_profile(db=db,profile=profile,user=current_user)
    if not profile_db:
        raise HTTPException(
            status_code=400,
            detail="something is wrong.. user unable to update ther profile !!!"
        )
    return profile_db

@router.patch("/me/upload_avatar/")
async def upload_avatar(avatar:UploadFile=File(...),current_user:Session=Depends(get_current_active_user),db:Session=Depends(get_db)):
    file_name = avatar.filename
    extension = file_name.split('.')[1]
    if extension not in ['jpg','png']:
        raise HTTPException(
            status_code=400,
            detail="only jpg and png file allowed !!"
        )
    token_name = secrets.token_hex(10)+'.'+extension
    generated_name = FILEPATH + token_name
    file_content = await avatar.read()
    with open(generated_name,"wb") as file:
        file.write(file_content)
    
    user_crud.upload_avatar(db,user=current_user,url=generated_name[1:])

    
    return {"filename":avatar.filename}

@router.patch("/{user_id}/update_user",response_model=user_schema.User)
async def update_user_by_admin(user_id:int,user:user_schema.UserUpdate,db:Session=Depends(get_db),current_user:Session=Depends(get_current_active_user)):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="user not super user!!"
        )
    user_db = user_crud.get_user_by_id(db=db,user_id=user_id)
    if not user_db:
        raise HTTPException(
            status_code=404,
            detail="not found"
        )
    user_db = user_crud.user_update_by_admin(db=db,user_db=user_db,user=user)
    if not user_db:
        raise HTTPException(
            status_code=400,
            detail="unable to update the user"
        )
    return user_db

@router.delete("/{user_id}/",status_code=204)
async def delete_user_by_admin(user_id:int,db:Session=Depends(get_db),current_user:Session=Depends(get_current_active_user)):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="user not superuser !!"
        )
    user_db = user_crud.get_user_by_id(user_id=user_id,db=db)
    if not user_db:
        raise HTTPException(
            status_code=404,
            detail="not found"
        )
    db.delete(user_db)
    db.commit()
    return {"detail":"user successfully delete"}