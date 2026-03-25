# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def post_init_hook(env):
    env.cr.execute(
        """
        INSERT INTO product_template_website_rel (
            product_template_id,
            website_id
        )
        SELECT id, website_id
        FROM product_template
        WHERE website_id IS NOT NULL
        ON CONFLICT DO NOTHING
        """
    )
