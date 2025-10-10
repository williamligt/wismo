from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from constants import OrderStatusType, DeliveryStatusType

class Sku(BaseModel):
    orderNumber: int
    orderSuffix: int
    sku: str
    pickQty: int

class Carton(BaseModel):
    orderNumber: int
    orderSuffix: int
    cartonId: Optional[int]
    deliveryStatusDescription: Optional[DeliveryStatusType]
    expectedDeliveryDate: datetime
    actualDeliveryDate: Optional[datetime]
    carrierCode: str
    carrierDescription: str
    traceAndTraceLink: str
    skus: List['Sku']

class OrderNumber(BaseModel):
    orderNumber: int = Field(description="The main order number")
    orderBookedDate: datetime
    orderSuffix: int
    orderStatus: OrderStatusType
    orderContactFullName: str
    contactEmailAddress: str
    contactPhone: int
    splitOrders: Optional[List['OrderNumber']]
    skus: Optional[List['Sku']]
    cartons: Optional[List['Carton']]


# Rebuild models to resolve forward references
OrderNumber.model_rebuild()