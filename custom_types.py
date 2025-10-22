from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from constants import OrderStatusType, DeliveryStatusType

class Sku(BaseModel):
    orderNumber: int
    orderSuffix: int
    sku: Optional[str]
    pickQty: Optional[int] = Field(description="quantity of sku")

class Carton(BaseModel):
    orderNumber: int
    orderSuffix: int
    cartonId: Optional[int]
    deliveryStatusDescription: Optional[DeliveryStatusType]
    expectedDeliveryDate: Optional[datetime] = Field(description="the expected date of delivery")
    actualDeliveryDate: Optional[datetime] = Field(description="date it was delivered, None means that it has not been delivered yet")
    carrierCode: Optional[str]
    carrierDescription: Optional[str] = Field(description="name of the carrier")
    traceAndTraceLink: Optional[str] =Field(description="This is the link to track the package")
    skus: List['Sku'] = Field(description="This is a list of the skus in the order")

class OrderNumber(BaseModel):
    orderNumber: int = Field(description="The main order number")
    orderBookedDate: datetime = Field(description="The date the order was booked")
    orderSuffix: int = Field(description='this is the backorder level, a order number might have multiple backorder levels this is when we have some of the items in stock and some not so the ones that are not in stock are moved to a higher back order level to be delivered later')
    orderStatus: str = Field(description="Status of the order")
    orderContactFullName: str 
    contactEmailAddress: str
    contactPhone: int
    shipTo: int
    shipToName: str
    splitOrders: Optional[List['OrderNumber']] = Field(description="This is the list of all the orders that this order has been split into. When an order splits into other orders it is commonly because we don't have it and it is being fufilled by someone else. Some of the items go to the split order and some remain in the original")
    skus: Optional[List['Sku']] = Field(description="this is the skus associated with this order, not including its split orders")
    cartons: Optional[List['Carton']] = Field(description="this is the cartons associated with this order, cartons are the units that we deliver in, each carton is delivered as a separate entity")

class ProductRequest(BaseModel):
    skus: List[str]

class Product(BaseModel):
    sku : str
    hfaDescription : str
    manufacturerName : str


# Rebuild models to resolve forward references
OrderNumber.model_rebuild()