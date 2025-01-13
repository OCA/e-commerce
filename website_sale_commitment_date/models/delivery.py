# Copyright 2025 Binhex - Adasat Torres de León
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import calendar
from datetime import datetime, timedelta

import pytz
from babel.dates import get_month_names

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.base.models.res_partner import _tz_get


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    allow_commitment_date = fields.Boolean(
        string="Allow commitment date",
        help="Allow to set a commitment date on the sale order from to the e-commerce",
    )

    min_commitment_days = fields.Float()
    max_commitment_days = fields.Float()

    max_time = fields.Float(
        help="Maximum time to place the order on the same day.",
    )

    tz = fields.Selection(selection=_tz_get, string="Timezone")

    exclude_weekday_ids = fields.Many2many(
        comodel_name="delivery.carrier.weekday",
        relation="delivery_carrier_weekday_rel",
        string="Exclude Weekdays",
    )

    exclude_date_ids = fields.Many2many(
        comodel_name="delivery.carrier.date",
        relation="delivery_carrier_date_rel",
        string="Exclude Dates",
    )

    def _get_calendar_context(self, start=False):
        today = fields.Date.today()

        if start:
            year, month = start.year, start.month
        else:
            year, month = today.year, today.month
            start = fields.Date.start_of(today, "month")
        lang = self.env["res.lang"]._lang_get(self.env.lang or self.env.user.lang)
        weekday_names = dict(lang.fields_get(["week_start"])["week_start"]["selection"])
        calen = calendar.Calendar(int(lang.week_start) - 1)
        weeks = []
        for week in calen.monthdatescalendar(year, month):
            weeks.append(
                [
                    {
                        "day": day.day,
                        "date": day.strftime(lang.date_format),
                        "is_today": day == today,
                        "is_disabled": self._check_calendar_disabled_day(day),
                    }
                    for day in week
                ]
            )

        return {
            "weekdays": [
                weekday_names[str(day + 1)][:3] for day in calen.iterweekdays()
            ],
            "title": "%s %s"
            % (get_month_names("abbreviated", locale=lang.code)[month], year),
            "month": month,
            "year": year,
            "start": start.strftime(lang.date_format),
            "weeks": weeks,
        }

    def _create_check_datetime(self, date):
        if not date or not self.tz:
            return False
        hours = int(self.max_time)
        minutes = int((self.max_time - hours) * 60)

        dt = datetime.combine(date, datetime.min.time()) + timedelta(
            hours=hours, minutes=minutes
        )
        tz = pytz.timezone(self.tz)
        return tz.localize(dt)

    def _create_datetime_local(self):
        if not self.tz:
            return False
        return datetime.now(pytz.timezone(self.tz))

    def _check_calendar_disabled_day(self, day):
        result = False
        if day == fields.Date.today() and self.max_time and self.tz:
            check_datetime = self._create_check_datetime(day)
            local_datetime = self._create_datetime_local()
            if local_datetime and check_datetime:
                if check_datetime <= local_datetime:
                    result = True
        if day < fields.Date.today():
            result = True
        if day.weekday() in self.exclude_weekday_ids.mapped("value"):
            result = True
        if self.min_commitment_days > 0:
            if day < fields.Date.today() + timedelta(days=self.min_commitment_days):
                result = True
        if self.max_commitment_days > 0:
            if day > fields.Date.today() + timedelta(days=self.max_commitment_days):
                result = True
        if self.exclude_date_ids.filtered(lambda d: d.value == day):
            result = True
        return result

    @api.constrains("max_time")
    def _check_max_time(self):
        for record in self:
            if record.max_time and record.max_time < 0:
                raise ValidationError(_("Max time must be greater than or equal to 0"))
            if record.max_time and record.max_time >= 24:
                raise ValidationError(_("Max time must be less than or equal to 24"))


class DeliveryCarrierWeekday(models.Model):
    _name = "delivery.carrier.weekday"

    name = fields.Char(required=True, translate=True)
    value = fields.Integer(required=True)


class DeliveryCarrierDate(models.Model):
    _name = "delivery.carrier.date"

    name = fields.Char(
        compute="_compute_name", store=True, readonly=False, string="Label"
    )
    value = fields.Date(required=True, string="Date")

    @api.depends("value")
    def _compute_name(self):
        lang = self.env["res.lang"]._lang_get(self.env.lang or self.env.user.lang)
        for record in self:
            if record.value:
                record.name = record.value.strftime(lang.date_format)
            else:
                record.name = False
