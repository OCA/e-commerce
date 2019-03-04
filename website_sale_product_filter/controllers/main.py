# -*- coding: utf-8 -*-

import collections
from openerp import _, http
from openerp.http import request
import openerp.addons.website_sale.controllers.main as main
from openerp.tools.safe_eval import safe_eval
from psycopg2.extensions import AsIs

FILTER_PREFIX = 'webshop_product_filter_'
POLICY_PREFIX = 'policy_' + FILTER_PREFIX


def complete_subtitle(search, domain_sub):
    if search:
        domain_sub = domain_sub + _(" search in name for ") + search
    if search or domain_sub:
        domain_sub = _("Currently active filters: ") + domain_sub + "."
    return domain_sub


def get_domain_for_cat_specific_attributes(
        env, category_specific_attributes, search, allposts):
    domain_product_product = []
    domain_subtitle = ""
    # based on the values posted from form create an extra domain
    # for our new filters.
    # this domain will be passed to website_sale_products.
    # this template will be modified to add this filtering,
    # integrating seamlessley with the main search (on product name)
    # and the variant/attribute search, in case the customer wanted to use
    # those too)
    if not category_specific_attributes:
        domain_subtitle = complete_subtitle(search, domain_subtitle)
        return [], domain_subtitle
    ir_model = env['ir.model.fields']
    for csa in category_specific_attributes:
        # remove FILTER_PREFIX
        # it was added in the template to distinguish from
        # the normal odoo attributes
        csa[0] = csa[0][len(FILTER_PREFIX):]
        # selections and x2x return a tuple with value/name
        # manage that transparently
        if csa[1].startswith('x2x_'):
            name = csa[1][4:].split('_x2x_opt_')[1]
            optid = csa[1][4:].split('_x2x_opt_')[0]
            csa[1] = optid
            #  IMPORTANT, MUST ALLWAYS KEEP CSA of cardinality 2 when
            #  entering in order for this to be csa[2] (third element)
            csa.append(name)
        # because we are working on the ir.fields table
        # we cannot take advantage of odoo inheritance,
        # if it's not in template look in product.
        att = ir_model.search([
            ('name', '=', csa[0]),
            ('model', '=', 'product.template')], limit=1)
        if att.ttype in ['char', 'text']:
            domain_product_product += [(csa[0], 'ilike', csa[1])]
            domain_subtitle = domain_subtitle + \
                att.field_description + _(" contains ") + \
                str(csa[1]) + "        "
        elif att.ttype in ['boolean']:
            convert = {'on': True, 'off': False}
            domain_product_product += [
                (csa[0], '=', convert[csa[1]])
                ]
            domain_subtitle = \
                domain_subtitle + att.field_description + " = " + \
                str(convert[csa[1]]) + "        "
        elif att.ttype in [
                'selection', 'monetary', 'float',
                'integer', 'many2one', 'one2many', 'many2many',
                'datetime', 'date']:
            policy_for_filter = \
                POLICY_PREFIX + csa[0]
            # setting default operator for fields without "policy"
            operator = "="
            # mapping policy options
            mapping_values_to_operator = {
                'disable': '',
                'exact': '=',
                'more': '>',
                'less': '<',
                'is': '=',
                'isnot': '!='}
            if policy_for_filter in allposts.keys():
                operator = \
                    mapping_values_to_operator[
                        allposts[policy_for_filter]]
            # checking for policy disabled
            if operator != '':
                domain_product_product +=\
                    [(csa[0], operator, csa[1])]
                # better feedback for selection and x2x fields
                if att.ttype in ['one2many', 'many2many', 'many2one',
                                 'selection']:
                    display = str(csa[2])
                else:
                    display = str(csa[1])
                domain_subtitle = \
                    domain_subtitle + att.field_description + \
                    " " + operator + " " + display + "        "
    domain_subtitle = complete_subtitle(search, domain_subtitle)
    return domain_product_product, domain_subtitle


def sanitize_post(posts):
    posts_clean = []
    # remove empty keys in our module specific attributes
    # I call this only passing a list of module specific attribute
    # NOTE will not SANITIZE post entries not in our specific namespace!
    for post in posts:
        if post[1]:
            posts_clean.append(post)
    return posts_clean


def get_range(env, category, attr):
    # if the field is not a stored field , skip the DB sql
    # range and use ORM to calc range.
    range_result = None
    prd_info = env['product.product']._fields[attr.name]
    if not prd_info.store:
        return False
    sql = ''
    if not prd_info.related:
        sql = ("select MIN(%s), MAX(%s) FROM "
               "product_product where product_tmpl_id in "
               "(select product_template_id from  "
               "product_public_category_product_template_rel "
               "where product_public_category_id = %s) ")
    elif prd_info.related[0] == 'product_tmpl_id':
        sql = ("select MIN(%s), MAX(%s) FROM "
               "product_template where id in "
               "(select product_template_id from "
               "product_public_category_product_template_rel "
               "where product_public_catgory_id = %s) ")

        # code for non-stored fields removing because doesn't perform
        # prds = env['product.template'].search([])
        # choice_values = (
        #     prds.sorted(
        #     key=lambda x: eval('x.{0}'.format(attr.name))
        #    )[1].read([attr.name])[0][attr.name],
        #    prds.sorted(
        #    key=lambda x: eval('x.{0}'.format(attr.name))
        #    )[-1].read([attr.name])[0][attr.name]
        # )

    if sql:
        env.cr.execute(
            sql, (AsIs(attr.name), AsIs(attr.name), category.id)
        )
        range_result = env.cr.fetchone()
        # managing the case of (none,none) there will never
        # be the (none, value) case because then  min=max
        # note it will never return just None it will allways
        # return at least (none, none)
        if range_result is None:
            return False
        if range_result[0] is None:
            return (0, 0)
        else:
            return (range_result[0], range_result[1])
    return False


def manage_attribute_types(env, category, attr):
    choice_values = []
    if attr.ttype in ['text', 'char', 'boolean']:
        return True
    if attr.ttype in [
            'float', 'integer', 'datetime', 'date', 'monetary']:
        choice_values = get_range(env, category, attr)
        if not choice_values:
            return False
    elif attr.ttype == 'selection':
        options = env[attr.model].fields_get(attr.name)[attr.name]['selection']
        choice_values = options
    elif attr.ttype in ['many2one', 'one2many', 'many2many']:
        relation = attr.relation
        possible_domain = attr.domain or []
        if isinstance(possible_domain, basestring):
            possible_domain = safe_eval(possible_domain)
        if isinstance(possible_domain, (list, collections.Iterable)):
            choice_values = env[str(relation)].search(
                possible_domain).read(['id', 'display_name'])
    return choice_values


class WebsiteSale(main.website_sale):
    """
    overwrite the website sale domain generator, to take in
    account all the new stuff we are filtering for
    """
    def _get_search_domain(self, search, category, attrib_values):
        domain = super(WebsiteSale, self)._get_search_domain(
            search=search, category=category, attrib_values=attrib_values)
        webshop_product_filter_domain = request.context.get(
            'webshop_product_filter_domain', []
        )
        domain += webshop_product_filter_domain
        return domain

    def get_category_attributes(self, category):
        """
         this apparently empty modularization is here to allow
         preprocess filtering of the category attributes, for future
         extensions (for example we want to extend to attributes of many types)
         of wich only some are filters, we can do it here.
        """
        return category.category_attributes

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        env = request.env
        attributes_dict = {}
        category_specific_attributes = []
        if category:
            category_specific_attributes = self.get_category_attributes(
                category
            )
        # Do not use the previous attribute_value or
        # product.attribute.value model. that is for standard attribute
        # variants. What we did in this module was to give product product
        # new attributes. we must add thoste to our querystring and interpret
        # them as a domain filter.
        website_product_filter_attributes = []
        for attr_name in post:
            # using the  prefix and then removing it
            # to allow product variants and our new product fields to
            # work together
            if attr_name.startswith(FILTER_PREFIX):
                website_product_filter_attributes.append(
                    [attr_name, post[attr_name]]
                )
        # remove empty char searches from ONLY the
        # FILTER_PREFIXed posts
        website_product_filter_attributes = sanitize_post(
            website_product_filter_attributes
        )
        website_product_filter_names = [
            x[0] for x in website_product_filter_attributes]
        for attr in category_specific_attributes:
            choice_values = manage_attribute_types(env, category, attr)
            # Note: this is a cool option to manage all together
            # selection fields without options, or other invalid choices
            # just pop them out
            if choice_values:
                attributes_dict[attr] = choice_values
            elif attr.name in website_product_filter_names:
                # so will also pop the option out of the view
                website_product_filter_attributes.remove(
                    [attr.name, post[attr.name]]
                )
                del post[attr.name]
        extra_domain_product_product, extra_domain_subtitle = \
            get_domain_for_cat_specific_attributes(
                env, website_product_filter_attributes, search, post
            )
        if extra_domain_product_product:
            # TODO optimization,  Can't you prepend every left hand member of
            # the extras domain with 'product_variant_ids.' and just join this
            # domain with the one _get_search_domain returns? Then you'd also
            # save this request.
            # could not figure out this particular idea reverting to previous
            filtered_pp = env['product.product'].search(
                extra_domain_product_product).read(['product_tmpl_id'])
            associated_templates = []
            # generate a list of ids of the template ids of found products
            for product in filtered_pp:
                associated_templates.append(product['product_tmpl_id'][0])
            # plugging in our new filter in _get_search_domain
            # in website sale put extra domain in the context keys
            # will be used in the _get_search_domain overwrite
            if associated_templates:
                request.context['webshop_product_filter_domain'] = [
                    ('id', 'in', associated_templates)]
        result = super(WebsiteSale, self).shop(
            page=page, category=category, search=search, ppg=ppg, **post
        )
        result.qcontext.update({
            'extra_domain_subtitle': extra_domain_subtitle,
            'filters': attributes_dict or None,
            'FILTER_PREFIX': FILTER_PREFIX,
            'POLICY_PREFIX': POLICY_PREFIX,
            })
        return result
