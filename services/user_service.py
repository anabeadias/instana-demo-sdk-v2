import random

def create_user(user):
    return random.randint(1000, 9999)

def get_user_by_id(user_id):
    return {"user_id": user_id}