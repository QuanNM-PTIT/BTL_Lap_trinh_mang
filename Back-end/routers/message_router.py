from fastapi import APIRouter, Depends
from starlette.responses import FileResponse

from configs.database import message_collection
from models.user_model import User
from routers.authentication import get_current_user
from serializers.message_serializer import messages_serializer

router = APIRouter(
    prefix='/message',
    tags=['Message']
)


@router.get('/get_all')
def get_all_messages(current_user: User = Depends(get_current_user)):
    return messages_serializer(message_collection.find())


@router.get('/file/{file_name}')
def get_file(file_name: str):
    return FileResponse(f"files/{file_name}")