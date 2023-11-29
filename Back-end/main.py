# -*- coding: utf-8 -*-
import base64
import json
import asyncio
import os
from datetime import datetime

from fastapi import FastAPI, WebSocket
from routers.authentication import router as AuthRouter
from routers.user_router import router as UserRouter
from routers.message_router import router as MessageRouter
from starlette.middleware.cors import CORSMiddleware
from configs.websocket_manager import ConnectionManager
from starlette.websockets import WebSocketDisconnect
from configs.database import message_collection, user_collection

app = FastAPI()

app.include_router(UserRouter)
app.include_router(AuthRouter)
app.include_router(MessageRouter)

manager = ConnectionManager()
file_manager = ConnectionManager()


async def insert_into_database(username, message, type):
    message_collection.insert_one({
        "username": username,
        "message": message,
        "type": type
    })


@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(websocket)
    user_collection.update_one({'username': username}, {'$set': {'status': 'online'}})
    user_collection.update_one({'username': username},
                               {'$set': {'last_sent': datetime.now().timestamp() * 1000}})
    try:
        while True:
            data = await websocket.receive_text()

            parsed_data = json.loads(data)

            message_content = parsed_data['content']
            await manager.broadcast(json.dumps({
                "username": username,
                "message": message_content,
                "type": 'text'
            }, ensure_ascii=False))
            asyncio.create_task(insert_into_database(username, message_content, 'text'))
            user_collection.update_one({'username': username},
                                       {'$set': {'last_sent': datetime.now().timestamp() * 1000}})
            user_collection.update_one({'username': username}, {'$set': {'status': 'online'}})


    except WebSocketDisconnect:
        manager.disconnect(websocket)
        user_collection.update_one({'username': username}, {'$set': {'status': 'offline'}})


@app.websocket("/ws/file/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await file_manager.connect(websocket)
    user_collection.update_one({'username': username}, {'$set': {'status': 'online'}})
    user_collection.update_one({'username': username},
                               {'$set': {'last_sent': datetime.now().timestamp() * 1000}})
    try:
        while True:
            data = await websocket.receive_text()

            parsed_data = json.loads(data)

            file_name = parsed_data['name']
            file_content = parsed_data['content']
            offset = parsed_data['offset']
            file_path = f"files/{file_name}"
            mode = 'ab' if offset > 0 else 'wb'

            with open(file_path, mode) as file:
                file.write(base64.b64decode(file_content.split(',')[1]))
            file_size = os.path.getsize(file_path)
            if file_size == parsed_data['totalSize']:
                await file_manager.broadcast(json.dumps({
                    "username": username,
                    "message": file_name,
                    "type": 'file'
                }, ensure_ascii=False))
                asyncio.create_task(insert_into_database(username, file_name, 'file'))
                user_collection.update_one({'username': username},
                                           {'$set': {'last_sent': datetime.now().timestamp() * 1000}})
                user_collection.update_one({'username': username}, {'$set': {'status': 'online'}})


    except WebSocketDisconnect:
        file_manager.disconnect(websocket)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
