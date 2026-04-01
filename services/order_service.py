import random
from instana.singletons import tracer
from services.payment_service import process_payment


def process_order(order, users_db, products_db):
    with tracer.start_as_current_span("order.process") as span:
        span.set_attribute("order.user_id", order.user_id)
        span.set_attribute("order.items_count", len(order.items))
        span.set_attribute("order.payment_method", order.payment_method)

        try:
            user = users_db.get(order.user_id)
            if not user:
                raise Exception("User not found")

            span.set_attribute("order.user_vip", user.get("vip", False))

            total = 0
            items_detail = []
            stock_updates = []

            with tracer.start_as_current_span("order.check_stock") as stock_span:
                stock_span.set_attribute("order.items_count", len(order.items))

                try:
                    for item in order.items:
                        product = products_db.get(item.product_id)

                        if not product:
                            stock_span.set_attribute("product.id", item.product_id)
                            raise Exception(f"Product {item.product_id} not found")

                        if product["stock"] < item.quantity:
                            stock_span.set_attribute("product.id", item.product_id)
                            stock_span.set_attribute("product.requested_quantity", item.quantity)
                            stock_span.set_attribute("product.available_stock", product["stock"])
                            raise Exception("Insufficient stock")

                        subtotal = product["price"] * item.quantity

                        items_detail.append({
                            "product_id": item.product_id,
                            "name": product["name"],
                            "quantity": item.quantity,
                            "unit_price": product["price"],
                            "subtotal": subtotal
                        })

                        total += subtotal

                        stock_updates.append({
                            "product_id": item.product_id,
                            "quantity": item.quantity
                        })

                    stock_span.set_attribute("order.total", total)

                except Exception as e:
                    stock_span.set_attribute("error", True)
                    stock_span.set_attribute("error.message", str(e))
                    stock_span.record_exception(e)
                    raise

            span.set_attribute("order.total", total)

            with tracer.start_as_current_span("payment.process") as payment_span:
                payment_span.set_attribute("payment.user_id", order.user_id)
                payment_span.set_attribute("payment.amount", total)
                payment_span.set_attribute("payment.method", order.payment_method)

                try:
                    payment_status = process_payment(
                        order.user_id,
                        total,
                        order.payment_method
                    )
                    payment_span.set_attribute("payment.status", payment_status)

                except Exception as e:
                    payment_span.set_attribute("payment.status", "failed")
                    payment_span.set_attribute("error", True)
                    payment_span.set_attribute("error.message", str(e))
                    payment_span.record_exception(e)
                    raise

            for update in stock_updates:
                products_db[update["product_id"]]["stock"] -= update["quantity"]

            result = {
                "order_id": random.randint(1000, 9999),
                "user": user,
                "items": items_detail,
                "total": total,
                "payment_status": payment_status
            }

            span.set_attribute("order.id", result["order_id"])
            span.set_attribute("order.status", payment_status)

            return result

        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            span.record_exception(e)
            raise
