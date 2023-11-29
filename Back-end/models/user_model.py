# -*- coding: utf-8 -*-
from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str
    full_name: str
    status: str = 'offline'
    last_sent: int = 0
