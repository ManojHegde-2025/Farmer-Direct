"""Net proceeds calculation service.

PHASE 13 specification:
Gross sale value: Accepted quantity × agreed price per unit
Estimated net proceeds:
  Gross sale value
  - seller-borne transportation costs
  - seller-borne packaging and handling costs
  - applicable disclosed seller charges
Display each component separately.
If any important cost is unknown, label the estimate as incomplete.
Do not claim that estimated net proceeds are guaranteed profit.
"""

from decimal import Decimal
from typing import Dict, Any, Optional

from app.models.order import Order
from app.models.delivery import Delivery, CostBorneBy


def calculate_estimated_net_proceeds(
    order: Order,
    delivery: Optional[Delivery] = None,
    packaging_cost: Optional[Decimal] = None,
    platform_fee_percent: Decimal = Decimal("0.00"),  # Transparent / zero by default
) -> Dict[str, Any]:
    """Calculate the transparent financial breakdown for a seller's order."""
    quantity = order.quantity
    price_per_unit = order.price_per_unit
    gross_value = quantity * price_per_unit

    is_complete = True
    missing_items = []

    # Transport deductions
    transport_deduction = Decimal("0.00")
    if delivery:
        if delivery.cost_borne_by in [CostBorneBy.SELLER, CostBorneBy.SHARED]:
            factor = Decimal("1.0") if delivery.cost_borne_by == CostBorneBy.SELLER else Decimal("0.5")
            if delivery.transport_cost is not None:
                transport_deduction = delivery.transport_cost * factor
            else:
                is_complete = False
                missing_items.append("Transportation cost agreed but exact amount pending")
    else:
        # If order fulfillment requires delivery and no record exists
        if order.fulfilment_method and "DELIVERY" in order.fulfilment_method.value:
            is_complete = False
            missing_items.append("Delivery transport cost has not yet been logged")

    # Packaging deductions
    pkg_deduction = packaging_cost if packaging_cost is not None else Decimal("0.00")
    if packaging_cost is None:
        missing_items.append("Packaging & handling expenses not individually specified")

    # Disclosed platform / handling charges
    platform_charge = gross_value * (platform_fee_percent / Decimal("100.00"))

    total_deductions = transport_deduction + pkg_deduction + platform_charge
    net_proceeds = gross_value - total_deductions

    return {
        "order_id": order.id,
        "quantity": float(quantity),
        "price_per_unit": float(price_per_unit),
        "gross_sale_value": float(gross_value),
        "deductions": {
            "seller_transport_cost": float(transport_deduction),
            "packaging_and_handling": float(pkg_deduction),
            "disclosed_platform_charges": float(platform_charge),
            "total_deductions": float(total_deductions),
        },
        "estimated_net_proceeds": float(net_proceeds),
        "is_estimate_complete": is_complete,
        "missing_cost_notes": missing_items,
        "disclaimer": (
            "Estimated net proceeds are indicative calculations based on agreed contract prices "
            "and declared seller expenses. This calculation does not represent guaranteed farmer profit."
        ),
    }
