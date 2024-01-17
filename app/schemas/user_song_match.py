from typing import List, Optional
from pydantic import EmailStr
from pydantic import HttpUrl

from app.schemas.base import Base
from app.models.response import Response

class UserSongMatchBase(Base):
    user_id: int
    song_id: int


# properties to receive via API creation
class UserSongMatchCreate(UserSongMatchBase):
    user_id: int
    song_id: int


# properties to receive via API update
class UserSongMatchUpdate(UserSongMatchBase):
    ...


# properties shared by models stored in DB
class UserSongMatchInDBBase(UserSongMatchBase):
    id: int = None

    class Config:
        orm_mode = True


# additional properties stored in DB bt not returned by API
class UserSongMatchInDB(UserSongMatchInDBBase):
    response: Response = None


# additional properties to return via API
class UserSongMatch(UserSongMatchInDBBase):
    user_id: int
    week_id: int
    response_id: int