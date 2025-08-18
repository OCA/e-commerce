import logging

from odoo import api, models, tools

from ..helpers import get_active_saleor_account

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model_create_multi
    def create(self, vals_list):
        quants = super().create(vals_list)
        # Recursion guard: allow callers to skip Saleor sync
        if not tools.config["test_enable"]:
            quants._trigger_saleor_sync()
        return quants

    def write(self, vals):
        res = super().write(vals)

        if ("quantity" in vals or "inventory_quantity" in vals) and not tools.config[
            "test_enable"
        ]:
            self._trigger_saleor_sync()
        return res

    def _trigger_saleor_sync(self):
        # No-op if called in a protected context
        if tools.config["test_enable"]:
            return

        account = get_active_saleor_account(self.env, raise_if_missing=True)

        # Collect affected variants
        variants = self.mapped("product_id").filtered("saleor_variant_id")
        if not variants:
            return

        variant_by_id = {v.id: v for v in variants}
        variant_ids = list(variant_by_id.keys())

        saleor_whs = self.env["stock.warehouse"].search(
            [
                ("is_saleor_warehouse", "=", True),
                ("include_in_saleor_inventory", "=", True),
            ]
        )
        saleor_locs = self.env["stock.location"].search(
            [
                ("is_saleor_warehouse", "=", True),
                ("include_in_saleor_inventory", "=", True),
            ]
        )

        Quant = self.env["stock.quant"].sudo()

        # Batch by warehouse (child_of view_location) using _read_group
        for wh in saleor_whs:
            domain = [
                ("location_id", "child_of", wh.view_location_id.id),
                ("product_id", "in", variant_ids),
            ]
            rows = Quant._read_group(
                domain, groupby=["product_id"], aggregates=["quantity:sum"]
            )
            for group_val, qty in rows:
                prod_id = group_val and group_val.id
                if not prod_id:
                    continue
                prod = variant_by_id.get(prod_id)
                if not prod:
                    continue
                qty = qty or 0.0
                try:
                    # Queue job if available
                    if hasattr(account, "with_delay"):
                        account.with_delay().job_variant_stock_update(
                            variant_id=prod.saleor_variant_id,
                            warehouse_id=wh.saleor_warehouse_id,
                            quantity=qty,
                        )
                    else:
                        account.job_variant_stock_update(
                            variant_id=prod.saleor_variant_id,
                            warehouse_id=wh.saleor_warehouse_id,
                            quantity=qty,
                        )
                    prod._notify_saleor_sync(wh, success=True)
                except Exception as e:
                    prod._notify_saleor_sync(wh, success=False, error_msg=str(e))

        # Batch by exact locations using _read_group
        for loc in saleor_locs:
            domain = [("location_id", "=", loc.id), ("product_id", "in", variant_ids)]
            rows = Quant._read_group(
                domain, groupby=["product_id"], aggregates=["quantity:sum"]
            )
            for group_val, qty in rows:
                prod_id = group_val and group_val.id
                if not prod_id:
                    continue
                prod = variant_by_id.get(prod_id)
                if not prod:
                    continue
                qty = qty or 0.0
                try:
                    if hasattr(account, "with_delay"):
                        account.with_delay().job_variant_stock_update(
                            variant_id=prod.saleor_variant_id,
                            warehouse_id=loc.saleor_warehouse_id,
                            quantity=qty,
                        )
                    else:
                        account.job_variant_stock_update(
                            variant_id=prod.saleor_variant_id,
                            warehouse_id=loc.saleor_warehouse_id,
                            quantity=qty,
                        )
                    prod._notify_saleor_sync(loc, success=True)
                except Exception as e:
                    prod._notify_saleor_sync(loc, success=False, error_msg=str(e))
