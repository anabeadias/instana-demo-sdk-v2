import time
import random
from instana.singletons import tracer


def process_payment(user_id, amount, method):
    with tracer.start_as_current_span("payment.gateway") as span:
        span.set_attribute("payment.user_id", user_id)
        span.set_attribute("payment.amount", amount)
        span.set_attribute("payment.method", method)

        time.sleep(0.5)

        approved = random.choice([True, True, True, False])

        if approved:
            span.set_attribute("payment.status", "approved")
            return "approved"

        span.set_attribute("payment.status", "failed")
        span.set_attribute("error", True)
        span.set_attribute("error.message", "Payment failed")
        raise Exception("Payment failed")