from fastapi import FastAPI, HTTPException
from models.order import OrderRequest
from models.user import UserRequest
from models.product import ProductRequest

from services.order_service import process_order
from services.user_service import create_user
from services.product_service import create_product

app = FastAPI(
    title="Orders API",
    description="API completa da loja (usuários, produtos e pedidos)",
    version="2.0.0"
)

# bancos fake
USERS_DB = {}
PRODUCTS_DB = {}
ORDERS_DB = {}


# Users

@app.post("/users", tags=["Users"])
def create_new_user(user: UserRequest):
    user_id = create_user(user)
    USERS_DB[user_id] = user.dict()
    return {"user_id": user_id, **user.dict()}


@app.get("/users/{user_id}", tags=["Users"])
def get_user(user_id: int):
    user = USERS_DB.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Products

@app.post("/products", tags=["Products"])
def create_new_product(product: ProductRequest):
    product_id = create_product(product)
    PRODUCTS_DB[product_id] = product.dict()
    return {"product_id": product_id, **product.dict()}


@app.get("/products/{product_id}", tags=["Products"])
def get_product(product_id: int):
    product = PRODUCTS_DB.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# Orders

@app.post("/orders", tags=["Orders"])
def create_order(order: OrderRequest):
    try:
        result = process_order(order, USERS_DB, PRODUCTS_DB)

        order_id = result["order_id"]
        ORDERS_DB[order_id] = result

        return result

    except Exception as e:
        message = str(e)

        if message == "User not found":
            raise HTTPException(status_code=404, detail=message)

        if message.startswith("Product ") and message.endswith(" not found"):
            raise HTTPException(status_code=404, detail=message)

        if message == "Insufficient stock":
            raise HTTPException(status_code=400, detail=message)

        if message == "Payment failed":
            raise HTTPException(status_code=402, detail=message)

        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/orders/{order_id}", tags=["Orders"])
def get_order(order_id: int):
    order = ORDERS_DB.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# Health

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}