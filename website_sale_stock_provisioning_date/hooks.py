# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def pre_init_hook(cr):
    """Precompute all the dates at once"""
    cr.execute("ALTER TABLE stock_move ADD COLUMN IF NOT EXISTS date_provisioning DATE")
    cr.execute(
        """
        UPDATE stock_move sm0
        SET date_provisioning = (
            sm.date_expected AT TIME ZONE COALESCE(rp.tz, 'UTC')
        )::date
        FROM stock_move sm
        LEFT JOIN res_users ru ON sm.write_uid = ru.id
        LEFT JOIN res_partner rp ON ru.partner_id = rp.id
        WHERE
            sm0.id = sm.id
            AND sm.date_expected IS NOT NULL
            AND sm.state NOT IN ('cancel', 'done')
    """
    )
