# -*- coding: utf-8 -*-
from datetime import datetime

from configs.database import user_collection
from fastapi import APIRouter
from serializers.user_serializer import users_serializer

router = APIRouter(
    prefix='/api/user',
    tags=['User']
)


@router.get('/get_all')
def get_all_users():
    users = user_collection.find()
    users = users_serializer(users)
    for user in users:
        if user.get('status') == 'online' and (user.get('last_sent') + 300000) < datetime.now().timestamp() * 1000:
            user_collection.update_one({'username': user.get('username')}, {'$set': {'status': 'afk'}})
            user['status'] = 'afk'
    return users_serializer(users)
