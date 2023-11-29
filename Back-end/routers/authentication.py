# -*- coding: utf-8 -*-
from datetime import timedelta

from configs import jwt_token
from configs.database import user_collection
from configs.hashing import Hash
from configs.jwt_token import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models.user_model import User
from serializers.user_serializer import user_serializer

router = APIRouter(
    tags=['Auth'],
    prefix='/auth'
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post('/register')
def register(user: User):
    new_user = {
        'username': user.username,
        'password': Hash.bcrypt(user.password),
        'full_name': user.full_name,
        'status': user.status,
        'last_sent': user.last_sent
    }
    existing_user = user_collection.find_one({'username': user.username})

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
            detail='Tên người dùng đã được sử dụng.'
        )

    _id = user_collection.insert_one(new_user)
    new_user = user_collection.find_one({'_id': _id.inserted_id})

    return {
        'status': status.HTTP_200_OK,
        'data': user_serializer(new_user)
    }


@router.post('/login')
async def login(request: OAuth2PasswordRequestForm = Depends()):
    user = user_collection.find_one({'username': request.username})
    if not user or not Hash.verify(request.password, user.get('password')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Thông tin đăng nhập không chính xác.')
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            'sub': user.get('username'),
        },
        expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get('/get_current_user')
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return jwt_token.verify_token(token, credentials_exception)
