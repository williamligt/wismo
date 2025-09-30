def generate_email(order_number, orders, cartons, skus, is_split):
    """
    Generate an email string for an order, split or not.
    """
    if is_split:
        subject = f"Subject: Update: Original Order {order_number} — Split Shipments and Tracking"
        body = f"""Hello,

This is an update for original order {order_number}, which was split into {len(orders)} sub-orders. Details are below.

Sub-orders
"""
        for order in orders:
            body += f"""
{order['postsplitordernumber']}
Booked date: {order['orderbookeddate']}
Status: {order['orderstatus']}
Order contact: {order['ordercontactfullname']}
Email: {order['contactemailaddress']}
Phone: {order['contactphone']}
"""
    else:
        subject = f"Subject: Update: Order {order_number} — Shipment and Tracking"
        body = f"""Hello,

This is an update for order {order_number}. Details are below.

Order Details
"""
        order = orders[0]  # Assuming one order
        body += f"""
{order['postsplitordernumber']}
Booked date: {order['orderbookeddate']}
Status: {order['orderstatus']}
Order contact: {order['ordercontactfullname']}
Email: {order['contactemailaddress']}
Phone: {order['contactphone']}
"""

    body += """
Carton Details
"""
    # Group cartons by sub-order (or order)
    carton_dict = {}
    for carton in cartons:
        sub_order = carton['postsplitordernumber']
        if sub_order not in carton_dict:
            carton_dict[sub_order] = []
        carton_dict[sub_order].append(carton)

    # Group SKUs by carton ID
    sku_dict = {}
    for sku in skus:
        carton_id = sku['cartonid']
        if carton_id not in sku_dict:
            sku_dict[carton_id] = []
        sku_dict[carton_id].append(sku['sku'])

    for sub_order, cartons_list in carton_dict.items():
        for carton in cartons_list:
            carton_id = carton['cartonid']
            body += f"""
Carton ID: {carton_id} (associated with order {sub_order})
Delivery status: {carton['deliverystatusdescription']}
Expected delivery date: {carton['expecteddeliverydate']}
Actual delivery date: {carton['actualdeliverydate']}
Carrier: {carton['carrierdescription'].strip()} ({carton['carriercode']})
Tracking link: {carton['trace_and_trace_link']}
SKUs: {', '.join(sku_dict.get(carton_id, []))}
"""
    body += """
If you need any additional information, please let me know.

Best regards,
[Your Name]
"""
    return subject + "\n\n" + body