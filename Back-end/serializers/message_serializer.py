def message_serializer(message):
    return {
        "username": message["username"],
        "message": message["message"],
        "type": message["type"],
    }


def messages_serializer(messages):
    return [message_serializer(message) for message in messages]