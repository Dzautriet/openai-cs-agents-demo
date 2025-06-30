"""
Handoff hooks for customer service agents.
"""
import random
import string
from agents import RunContextWrapper
from .context import CustomerServiceContext


async def on_seat_booking_handoff(context: RunContextWrapper[CustomerServiceContext]) -> None:
    """Set a random flight number when handed off to the seat booking agent."""
    context.context.flight_number = f"FLT-{random.randint(100, 999)}"
    context.context.confirmation_number = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


async def on_cancellation_handoff(
    context: RunContextWrapper[CustomerServiceContext]
) -> None:
    """Ensure context has a confirmation and flight number when handing off to cancellation."""
    if context.context.confirmation_number is None:
        context.context.confirmation_number = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )
    if context.context.flight_number is None:
        context.context.flight_number = f"FLT-{random.randint(100, 999)}"


# Hooks registry for easy lookup
HOOKS_REGISTRY = {
    "on_seat_booking_handoff": on_seat_booking_handoff,
    "on_cancellation_handoff": on_cancellation_handoff,
} 