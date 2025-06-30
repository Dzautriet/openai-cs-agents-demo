"""
Customer service specific tools.
These tools handle direct customer service actions like seat updates, cancellations, etc.
"""
import random
import string
from agents import function_tool, RunContextWrapper
from ..context import CustomerServiceContext


@function_tool
async def update_seat(
    context: RunContextWrapper[CustomerServiceContext], confirmation_number: str, new_seat: str
) -> str:
    """Update the seat for a given confirmation number."""
    context.context.confirmation_number = confirmation_number
    context.context.seat_number = new_seat
    assert context.context.flight_number is not None, "Flight number is required"
    return f"Updated seat to {new_seat} for confirmation number {confirmation_number}"


@function_tool(
    name_override="display_seat_map",
    description_override="Display an interactive seat map to the customer so they can choose a new seat."
)
async def display_seat_map(
    context: RunContextWrapper[CustomerServiceContext]
) -> str:
    """Trigger the UI to show an interactive seat map to the customer."""
    # The returned string will be interpreted by the UI to open the seat selector.
    return "DISPLAY_SEAT_MAP"


@function_tool(
    name_override="cancel_flight",
    description_override="Cancel a flight."
)
async def cancel_flight(
    context: RunContextWrapper[CustomerServiceContext]
) -> str:
    """Cancel the flight in the context."""
    fn = context.context.flight_number
    assert fn is not None, "Flight number is required"
    return f"Flight {fn} successfully cancelled" 