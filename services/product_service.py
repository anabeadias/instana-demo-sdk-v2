import random

def create_product(product):
    return random.randint(1000, 9999)

def get_product_by_id(product_id):
    return {"product_id": product_id}