This module extends Odoo's e-commerce checkout process by adding a delivery date selection tied to the chosen delivery method. The selected delivery date is then transferred to the created Sale Order's Delivery Date field (commitment_date).

To support realistic and flexible delivery scheduling, the module introduces configurable constraints on delivery timing, including:

- Available delivery days of the week: Specify which days deliveries can be scheduled
- Available delivery hours: Set start and end hours for daily delivery windows
- Delivery lag / cut-off rules: Control the minimum time between order placement and the earliest possible delivery


The delivery lag is highly customizable by supporting two delay types:

**Days**

Minimum delay is interpreted as full calendar days.
For example, a delay of 1 day means orders placed on Monday can be delivered starting Tuesday at 11:00.

**Hours**

Minimum delay is interpreted as an exact number of hours (including fractional hours) from the time the order is placed.
For example, a delay of 11 hours means an order placed at 23:59 on Monday can be delivered starting Tuesday at 11:00.

This flexibility allows the delivery scheduling logic to closely match real-world logistics, cut-off times, and customer expectations.

**Example Use Cases**

*Example 1: Delay Type = Hours*

**Configuration:**
- Available delivery days: Monday to Friday
- Delivery window: 11:00 to 16:00
- Minimum delivery delay: 11 hours
- Earliest delivery time of day: 11:00

**Results:**
- An order placed Monday at 09:00 can be delivered earliest Tuesday at 11:00
- An order placed Monday at 12:00 can be delivered earliest Wednesday at 11:00

*Example 2: Delay Type = Days*

**Configuration:**
- Available delivery days: Monday to Friday
- Delivery window: 11:00 to 18:00
- Minimum delivery delay: 1 day
- Earliest delivery time of day: 11:00

**Results:**
- Any order placed on Monday can be delivered earliest Tuesday starting from 11:00

The sale order's commitment_date field is automatically updated based on the selected delivery date.
