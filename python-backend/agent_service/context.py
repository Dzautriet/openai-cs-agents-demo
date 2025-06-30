"""
Context definitions for customer service agents.
"""
import random
from pydantic import BaseModel


class CustomerServiceContext(BaseModel):
    """Context for customer service agents."""
    passenger_name: str | None = None
    confirmation_number: str | None = None
    seat_number: str | None = None
    flight_number: str | None = None
    account_number: str | None = None  # Account number associated with the customer


def create_initial_context() -> CustomerServiceContext:
    """
    Factory for a new CustomerServiceContext.
    For demo: generates a fake account number.
    In production, this should be set from real user data.
    """
    ctx = CustomerServiceContext()
    ctx.account_number = str(random.randint(10000000, 99999999))
    return ctx 