from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Inventory, Order, Shipment, Vehicle
from app.services.events import EventService


ORDER_TRANSITIONS = {
    "CREATED": {"PAYMENT_CONFIRMED", "CANCELLED"},
    "PAYMENT_CONFIRMED": {"INVENTORY_RESERVED", "CANCELLED"},
    "INVENTORY_RESERVED": {"PICKED", "CANCELLED"},
    "PICKED": {"PACKED"}, "PACKED": {"SHIPMENT_CREATED"},
    "SHIPMENT_CREATED": {"DISPATCHED"}, "DISPATCHED": {"IN_TRANSIT"},
    "IN_TRANSIT": {"ARRIVED_AT_DC", "DELAYED"}, "ARRIVED_AT_DC": {"AT_DELIVERY_HUB"},
    "AT_DELIVERY_HUB": {"OUT_FOR_DELIVERY"}, "OUT_FOR_DELIVERY": {"DELIVERED"},
    "DELAYED": {"IN_TRANSIT", "CANCELLED"}, "DELIVERED": set(), "CANCELLED": set(),
}


class OperationsService:
    @staticmethod
    def reserve_inventory(db: Session, inventory_id: int, quantity: int, order: Order) -> Inventory:
        inventory = db.get(Inventory, inventory_id)
        if not inventory or quantity <= 0 or inventory.available < quantity:
            raise ValueError("Insufficient available inventory")
        previous = {"available": inventory.available, "reserved": inventory.reserved}
        inventory.available -= quantity
        inventory.reserved += quantity
        EventService.record(db, "INVENTORY_RESERVED", "INVENTORY", "inventory", inventory.id,
                            f"Reserved {quantity} units for {order.number}", order.origin.code,
                            previous_state=previous, new_state={"available": inventory.available, "reserved": inventory.reserved})
        return inventory

    @staticmethod
    def transition_order(db: Session, order_id: int, target_state: str) -> Order:
        order = db.get(Order, order_id)
        if not order:
            raise ValueError("Order not found")
        target_state = target_state.upper()
        if target_state not in ORDER_TRANSITIONS.get(order.status, set()):
            raise ValueError(f"Cannot transition {order.status} to {target_state}")
        previous = order.status
        order.status = target_state
        EventService.record(db, "ORDER_UPDATED", "OPERATIONS", "order", order.id,
                            f"{order.number}: {previous} -> {target_state}", order.origin.code,
                            previous_state={"status": previous}, new_state={"status": target_state})
        if target_state == "DISPATCHED":
            shipment = db.scalar(select(Shipment).where(Shipment.order_id == order.id))
            if shipment:
                shipment.status = "IN_TRANSIT"
                vehicle = db.get(Vehicle, shipment.vehicle_id)
                if vehicle:
                    vehicle.status = "IN_TRANSIT"
                EventService.record(db, "SHIPMENT_DISPATCHED", "LOGISTICS", "shipment", shipment.id,
                                    f"{shipment.code} dispatched on {vehicle.code if vehicle else 'assigned vehicle'}",
                                    order.origin.code)
        return order

