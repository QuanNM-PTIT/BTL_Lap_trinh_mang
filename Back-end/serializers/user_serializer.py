# -*- coding: utf-8 -*-
def user_serializer(user):
    return {
        'username': user.get('username'),
        'full_name': user.get('full_name'),
        'status': user.get('status'),
        'last_sent': user.get('last_sent')
    }


def users_serializer(users):
    response = []
    for user in users:
        response.append(user_serializer(user))
    return response
