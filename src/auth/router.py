from fastapi import APIRouter, Depends, HTTPException, status, Response, Body
from sqlalchemy import exists

from src.auth.models import User
from src.auth.services import find_user_by_username
from src.config.database import get_db
from src.endpoints.models import FieldRefreshTokenBody, FieldRefreshTokenResponse, FieldUserCreateBody, FieldUserLoginBody, FieldUserLoginSuccessResponse, UserDetail, VehicleInformation
from sqlalchemy.orm import Session

from src.utils.auth_utils import decode_access_token, encode_access_token, encode_refresh_token, get_current_user, get_new_access_token, hash_password, verify_password
from src.vehicles.model import UserVehicle


router  =  APIRouter(tags=['Auth'])
public_router  =  APIRouter(tags=['Auth'])

@public_router.post('/auth/login', response_model=FieldUserLoginSuccessResponse,)
def login(payload: FieldUserLoginBody,
    db: Session = Depends(get_db),
):
    user = find_user_by_username(db, payload.username)
    if not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Password!!",
        )

    access_token = encode_access_token(payload.username)
    refresh_token = encode_refresh_token(payload.username)
    return FieldUserLoginSuccessResponse(access_token=access_token, refresh_token=refresh_token)

@public_router.post("/refresh-token", response_model=FieldRefreshTokenResponse)
def refresh_token(
    request: FieldRefreshTokenBody, db: Session = Depends(get_db)
):
    """Get new access token from a valid refresh token."""

    new_access_token = get_new_access_token(request.refresh_token)

    return {"access_token": new_access_token}
    
    
@public_router.post('/auth/sign-up')
def create_user(payload: FieldUserCreateBody, db: Session  = Depends(get_db)):
    
    is_user_exists  =  db.query(exists().where(User.username == payload.username)).scalar()
    if is_user_exists:
        raise HTTPException(status_code=409, detail="User already exists...")
    else:
        hashed_password =  hash_password(payload.password)
        new_user =  User(
            username=payload.username,
            first_name=payload.first_name, 
            last_name=payload.last_name,
            password= hashed_password
            )
        db.add(new_user)
        db.commit()
    
    return {"result": "User created successfully"}



@router.get("/auth/me", response_model =UserDetail)
def current_user_detail(db:Session =  Depends(get_db), current_user = Depends(get_current_user)):
    
    vehicles  = db.query(UserVehicle).filter(UserVehicle.user_id  == current_user.id, UserVehicle.deleted_at.is_(None)).all()

    vehicles_response =  [ VehicleInformation( 
        id= vehicle.id,
        vehicle_name  = vehicle.vehicle_name,
        vechicle_number  = vehicle.vehicle_number, 
        description = vehicle.description, 
        )  for vehicle in vehicles]
    
    return UserDetail(
        id=  current_user.id, 
        username= current_user.username, 
        first_name = current_user.first_name, 
        last_name = current_user.last_name, 
        vehicles= vehicles_response
    )
