import uuid
from datetime import datetime

def generate_order_number() -> str:
    """Generates a human-friendly unique order number, e.g. ORD-2026-8910."""
    suffix = uuid.uuid4().hex[:6].upper()
    return f"ORD-{datetime.now().year}-{suffix}"

def generate_transaction_id() -> str:
    """Generates a unique payment transaction ID."""
    return f"TXN-{uuid.uuid4().hex[:10].upper()}"
