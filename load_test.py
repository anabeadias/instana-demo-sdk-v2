import requests
import random
import time

BASE_URL = "http://127.0.0.1:8000"

users = []
products = {}  # agora guarda estoque também

# CREATE USERS
def create_users(n=10):
    for i in range(n):
        payload = {
            "name": f"user_{i}",
            "email": f"user_{i}@test.com",
            "vip": random.choice([True, False])
        }

        r = requests.post(f"{BASE_URL}/users", json=payload)
        if r.status_code == 200:
            users.append(r.json()["user_id"])


# CREATE PRODUCTS 
def create_products(n=10):
    for i in range(n):
        stock = random.randint(10, 30)  # mais estoque inicial

        payload = {
            "name": f"product_{i}",
            "price": random.randint(50, 200),
            "stock": stock
        }

        r = requests.post(f"{BASE_URL}/products", json=payload)
        if r.status_code == 200:
            product_id = r.json()["product_id"]
            products[product_id] = stock


# ---------------- CREATE ORDERS ----------------
def create_order():
    if not users or not products:
        return

    items = []
    selected_products = random.sample(list(products.keys()), k=random.randint(1, 2))

    for product_id in selected_products:
        stock_available = products[product_id]

        if stock_available <= 0:
            continue  # pula produto sem estoque

        quantity = random.randint(1, min(3, stock_available))

        items.append({
            "product_id": product_id,
            "quantity": quantity
        })

    if not items:
        return

    payload = {
        "user_id": random.choice(users),
        "items": items,
        "payment_method": random.choice(["credit_card", "pix"])
    }

    r = requests.post(f"{BASE_URL}/orders", json=payload)

    # 🔥 Atualiza estoque local se deu certo
    if r.status_code == 200:
        for item in items:
            products[item["product_id"]] -= item["quantity"]

    else:
        print(f"Error: {r.status_code} - {r.text}")


# ---------------- MAIN ----------------

if __name__ == "__main__":
    print("Creating users...")
    create_users(10)

    print("Creating products...")
    create_products(10)

    print("Generating orders...")

    for _ in range(80):
        create_order()
        time.sleep(0.1)