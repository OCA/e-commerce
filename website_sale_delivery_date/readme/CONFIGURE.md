**Delivery Method Time and Date Constraints Configuration**

**Delivery Method Setup**

1. Go to Sales → Configuration → Delivery Methods
2. Open an existing Delivery Method or create a new one
3. Under the Availability tab, find the Weekly Delivery Schedule section

**Minimum Delivery Delay (min_delivery_delay)**

Defines the minimal lead time between order placement and the earliest possible delivery.

**Minimum Delivery Delay Type (min_delivery_delay_type)**

Controls how the delay is interpreted:
- **days**: Delay is in full calendar days (e.g., 1 = next day)
- **hours**: Delay is in exact hours from the moment of order

**Weekday Configuration**

For each weekday, configure the following parameters:

- **Weekday**: Select the day of the week (Monday to Sunday)
- **Active**: Enable or disable delivery on this weekday
- **Delivery Start Hour**: Earliest hour deliveries may be scheduled (e.g., 11.0 for 11:00)
- **Delivery End Hour**: Latest hour deliveries may be scheduled (e.g., 18.0 for 18:00)
- **Cut-off Hour** (Optional): Defines a cut-off time for next-day delivery eligibility

