from openupgradelib import openupgrade


def update_template_keys(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_ui_view
        SET key = 'website_sale_suggest_create_account.navigation_buttons'
        WHERE key = 'website_sale_suggest_create_account.cart'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    update_template_keys(env)
