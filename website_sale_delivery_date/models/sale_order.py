from datetime import timedelta

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def set_delivery_date(self, delivery_date):
        """Validate the delivery date against carrier constraints."""
        self.ensure_one()
        carrier = self.carrier_id
        if not carrier:
            return True

        # Get current time
        now = fields.Datetime.now()

        # Calculate minimum delivery time based on delay type
        if carrier.min_delivery_delay_type == "hours":
            min_delivery_time = now + timedelta(hours=carrier.min_delivery_delay)
        else:  # days
            min_delivery_time = now + timedelta(days=carrier.min_delivery_delay)
            # Set to start of day
            min_delivery_time = min_delivery_time.replace(
                hour=0, minute=0, second=0, microsecond=0
            )

        # Check if delivery date is after minimum delivery time
        if delivery_date < min_delivery_time:
            raise ValidationError(
                _("Selected delivery date is before the minimum delivery time")
            )

        # Get weekday rule for the delivery date
        weekday_rule = carrier.get_rule_by_weekday(delivery_date)

        if not weekday_rule:
            weekday = delivery_date.strftime("%A").lower()
            raise ValidationError(
                _("Delivery is not available on %(weekday)s", weekday=weekday)
            )

        # Check delivery hours
        delivery_hour = delivery_date.hour + delivery_date.minute / 60
        if not (
            weekday_rule.delivery_start_hour
            <= delivery_hour
            <= weekday_rule.delivery_end_hour
        ):
            raise ValidationError(
                _(
                    "Delivery time must be between "
                    "%(start_hour)d:00 and "
                    "%(end_hour)d:00",
                    start_hour=int(weekday_rule.delivery_start_hour),
                    end_hour=int(weekday_rule.delivery_end_hour),
                )
            )

        # Check cut-off time if defined
        if weekday_rule.cutoff_hour:
            cutoff_time = now.replace(
                hour=int(weekday_rule.cutoff_hour),
                minute=int((weekday_rule.cutoff_hour % 1) * 60),
                second=0,
                microsecond=0,
            )
            if now.hour > weekday_rule.cutoff_hour:
                cutoff_time += timedelta(days=1)
                weekday_rule = carrier.get_rule_by_weekday(cutoff_time)
                cutoff_time = cutoff_time.replace(hour=int(weekday_rule.cutoff_hour))
            if cutoff_time > delivery_date:
                raise ValidationError(
                    _(
                        "Order placed after cut-off time " "%(cutoff_hour)s:00",
                        cutoff_hour=int(weekday_rule.cutoff_hour),
                    )
                )
        self.write({"commitment_date": delivery_date})
        return True

    def _set_delivery_method(self, delivery_method, rate=None):
        result = super()._set_delivery_method(delivery_method, rate)
        if delivery_method and self._has_deliverable_products():
            self.write({"commitment_date": False})
        return result
