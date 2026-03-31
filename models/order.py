from pydantic import BaseModel

class OrderItem(BaseModel):
    product_id: int
    quantity: int

class OrderRequest(BaseModel):
    user_id: int
    items: list[OrderItem]
    payment_method: str
