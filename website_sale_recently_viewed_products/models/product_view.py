from openerp import api, fields, models, _


class ProductHistory(models.Model):
    _name = 'website.sale.product.view'
    _description = 'Ecommerce Product Views'

    sessionid = fields.Char('Session ID', index=True)
    product_id = fields.Many2one('product.template', 'Product')
    last_view_datetime = fields.Datetime(
        'Last view datetime', default=fields.Datetime.now)

    _sql_constraints = [
        ('unique_session_product', 'UNIQUE(sessionid, product_id)',
         'There is already a record for this product and session')
    ]
    _order = 'last_view_datetime DESC'

    @api.multi
    def human_readable_datetime_difference(self, now=None):
        """
        Return an human readable form of the difference between the supplied
        datetime (or the current datetime if not supplied) and the history
        record ``last_view_datetime``.
        """
        if now is None:
            now = fields.Datetime.from_string(fields.Datetime.now())
        timedifference = now - fields.Datetime.from_string(
            self.last_view_datetime)
        minutes = timedifference.seconds // 60
        hours = timedifference.seconds // 3600
        days = timedifference.days
        # string concatenation and explicit singular/plural
        # to make life easier for translators
        if days > 1:
            return str(days) + ' ' + _('days ago')
        elif days == 1:
            return str(days) + ' ' + _('Yesterday')
        elif hours > 1:
            return str(hours) + ' ' + _('hours ago')
        elif hours == 1:
            return str(hours) + ' ' + _('hour ago')
        elif minutes > 1:
            return str(minutes) + ' ' + _('minutes ago')
        elif minutes == 1:
            return str(minutes) + ' ' + _('minute ago')
        return _('Less than a minute ago')
