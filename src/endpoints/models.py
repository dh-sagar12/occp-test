from typing import Optional, List
from pydantic import Field, BaseModel


class FieldUserLoginBody(BaseModel):
    username: str = Field(..., example='username', title='username')
    password: str = Field(..., example='password', title='password')


class FieldUserLoginSuccessResponse(BaseModel):
    access_token: Optional[str] = Field(
        None,
        example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
        title='access_token',
    )
    refresh_token: Optional[str] = Field(
        None,
        example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
        title='refresh_token',
    )
    
class FieldRefreshTokenBody(BaseModel):
    refresh_token: str = Field(
        ...,
        example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
        title='refresh_token',
    )


class FieldRefreshTokenResponse(BaseModel):
    access_token: Optional[str] = Field(
        None,
        example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
        title='access_token',
    )
    
class FieldUserCreateBody(BaseModel):
    username: str = Field(..., example='user123', title='username')
    first_name: Optional[str] = Field(None, example='first_name', title='first_name')
    last_name: Optional[str] = Field(None, example='last_name', title='last_name')
    password: str = Field(..., example='userpass', title='password')

class VehicleCreate(BaseModel):
    vehicle_name: str 
    vehicle_number: str
    description: Optional[str]  = None


class VehicleInformation(BaseModel):
    id: Optional[int] = None
    vehicle_name: str = None
    vehicle_number: str =  None
    description: Optional[str]  = None


class UserDetail(BaseModel):
    id: Optional[int] = None
    username: str 
    first_name: str
    last_name: str
    vehicles: Optional[List[VehicleInformation]] =  None
    