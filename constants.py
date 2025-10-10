from typing import Literal

OrderStatusType = Literal[
    "Shipped ovrnigh",
    "SHP Await Invoice",
    "DS-Entry hold",
    "DS-Pending Inv Error",
    "DS-SHP Pend Cust Inv",
    "DS-Credit Review",
    "DS-SHP Await Invoice",
    "DS-Await Vend SHP",
    "C.C. Shipped",
    "Awaiting wave",
    "DS-PO Gen Pending",
    "Invoiced",
    "Awaiting stock",
    "Process pending",
    "Shipped",
    "Entry hold",
    "Shipper printed",
    "DS-C.C. Shipped",
    "Pricing Hold",
    "Credit Review",
    "Ready to Print"
]

DeliveryStatusType = Literal[
    "On-Time",
    "Late Delivery",
    "Early Delivery",
    "No POD"
]