from datetime import datetime
from typing import List, Optional
from custom_types import OrderNumber, Sku, Carton
from constants import OrderStatusType, DeliveryStatusType

def format_date(date: datetime) -> str:
    """Format a datetime object into a user-friendly string."""
    return date.strftime("%B %d, %Y")

def format_status(status: OrderStatusType) -> str:
    """Format the order status into a more readable format."""
    return status.replace("DS-", "").replace("-", " ").title()

def format_delivery_status(status: Optional[DeliveryStatusType]) -> str:
    """Format the delivery status into a user-friendly string."""
    if not status:
        return "Status Not Available"
    return status.replace("-", " ")

def format_sku_list(skus: Optional[List[Sku]]) -> str:
    """Format a list of SKUs into a readable string."""
    if not skus:
        return "No items in this order"
    
    sku_parts = ["Order Items:"]
    for sku in skus:
        sku_info = f"- SKU: {sku.sku or 'N/A'}"
        if sku.pickQty:
            sku_info += f", Quantity: {sku.pickQty}"
        sku_parts.append(sku_info)
    
    return "\n".join(sku_parts)

def format_cartons(cartons: Optional[List[Carton]]) -> str:
    """Format carton tracking information into a readable string."""
    if not cartons:
        return "No shipping information available"
    
    carton_parts = ["Shipping Information:"]
    for carton in cartons:
        carton_parts.append(f"\nCarton ID: {carton.cartonId or 'N/A'}")
        if carton.carrierDescription:
            carton_parts.append(f"Carrier: {carton.carrierDescription}")
        
        delivery_status = format_delivery_status(carton.deliveryStatusDescription)
        carton_parts.append(f"Delivery Status: {delivery_status}")
        
        if carton.expectedDeliveryDate:
            carton_parts.append(f"Expected Delivery: {format_date(carton.expectedDeliveryDate)}")
        
        if carton.actualDeliveryDate:
            carton_parts.append(f"Actual Delivery: {format_date(carton.actualDeliveryDate)}")
        
        if carton.traceAndTraceLink:
            carton_parts.append(f"Track Your Package: {carton.traceAndTraceLink}")
            
        if carton.skus:
            sku_list = "\n".join(f"  - {sku.sku or 'N/A'}: {sku.pickQty or 0} units" 
                                for sku in carton.skus)
            carton_parts.append(f"Items in this carton:\n{sku_list}")
    
    return "\n".join(carton_parts)

def format_split_orders(orders: Optional[List[OrderNumber]], indent_level: int = 0) -> str:
    """Format split order information into a readable string."""
    if not orders or not isinstance(orders, list):
        return ""
    
    indent = "  " * indent_level
    split_parts = [f"{indent}This order has been split into the following orders:"]
    
    for split_order in orders:
        if not isinstance(split_order, OrderNumber):
            continue
            
        split_parts.append(f"\n{indent}Split Order: {split_order.orderNumber}-{split_order.orderSuffix}")
        split_parts.append(f"{indent}Status: {format_status(split_order.orderStatus)}")
        
        if split_order.skus:
            split_parts.append(f"{indent}{format_sku_list(split_order.skus).replace('Order Items:', 'Items in this split:')}")
        
        if split_order.cartons:
            # Indent the carton information for better readability
            carton_info = format_cartons(split_order.cartons)
            # Handle indentation line by line
            indented_carton_info = "\n".join(f"{indent}{line}" for line in carton_info.split("\n"))
            split_parts.append(indented_carton_info)
            
        if split_order.splitOrders:
            # Recursively format any further split orders with increased indentation
            further_splits = format_split_orders(split_order.splitOrders, indent_level + 1)
            if further_splits:
                split_parts.append(f"\n{indent}{further_splits}")
    
    return "\n".join(split_parts)

def generate_order_email(order: OrderNumber) -> str:
    """Generate an email for the given order."""
    if not isinstance(order, OrderNumber):
        raise TypeError("Expected OrderNumber object but received a different type")
        
    email_parts = []
    
    # Header with order information
    email_parts.append(f"Dear <name>,")
    email_parts.append(f"\nThank you for your order. Here are your order details:")
    email_parts.append(f"\nOrder Number: {order.orderNumber}-{order.orderSuffix}")
    email_parts.append(f"Order Date: {format_date(order.orderBookedDate)}")
    email_parts.append(f"Order Status: {format_status(order.orderStatus)}")
    
    # Customer contact information
    email_parts.append("\nContact Information:")
    email_parts.append(f"Name: {order.orderContactFullName}")
    email_parts.append(f"Email: {order.contactEmailAddress}")
    email_parts.append(f"Phone: {order.contactPhone}")
    
    # Add SKU information
    if order.skus:
        email_parts.append(f"\n{format_sku_list(order.skus)}")
    
    # Add carton tracking information
    if order.cartons:
        email_parts.append(f"\n{format_cartons(order.cartons)}")
    
    # Add split order information
    if order.splitOrders:
        email_parts.append(f"\n{format_split_orders(order.splitOrders)}")
    
    # Add footer
    email_parts.append("\nThank you for your business!")
    email_parts.append("If you have any questions about your order, please contact our customer service.")
    
    return "\n".join(email_parts)