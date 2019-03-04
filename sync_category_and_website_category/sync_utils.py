# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def syncronize(env, vals, current_main_cat=False, current_extra_cats=False):
    """
    Pylint improvement: this code is used in 4 different functions and 2
    different models actually makes sense to centralize.

    TO BE USED ON product.category (INTERNAL)


    categ_id   MAIN  INTERNAL CATEGORY ON product.template
    categ_ids  Extra INTERNAL CATEGORIES on product.template

    current_main_cat: record of type product.category
    current_extra_cats: recordset of type product.category

    returns an updated dictionary to be used on a product, the new dictionary
    will be the old dict + extra commands to sync the public ids

    """
    categ_model = env['product.category']
    # one way syncing, just pop it out
    if vals.get('public_categ_ids'):
        vals.pop('public_categ_ids')
    if vals.get('categ_id'):
        cat = categ_model.browse(vals['categ_id'])
        pub_cat = cat.public_category_id
        # Add support for product_multi_category
        if current_main_cat:
            vals['public_categ_ids'] = [
                (4, pub_cat.id), (3, current_main_cat.public_category_id.id)]
        else:
            vals['public_categ_ids'] = [(4, pub_cat.id)]
    extra_int_categories = vals.get('categ_ids')
    if not extra_int_categories:
        return vals
    if not vals.get('public_categ_ids'):
        vals['public_categ_ids'] = []
    for extra_command in extra_int_categories:
        if extra_command[0] == 6:
            pub_extra_cat = env['product.category'].browse(
                extra_command[2]).mapped('public_category_id.id')
            vals['public_categ_ids'].append((6, False, pub_extra_cat))
        # we care only about the add/remove commands not modify
        # if a 0 is in the mix it will create also a new public category, taken
        # care by sync_fields in create.
        # if a 1 is in the mix that means we are just modifying something in
        # the category, the syncing of the public category is also taken
        # care in sync_fields.
        if extra_command[0] in [4, 3, 2]:
            pub_extra_cat = env['product.category'].browse(
                extra_command[1]).public_category_id.id
            # append the command directly
            vals['public_categ_ids'].append([extra_command[0], pub_extra_cat])
        # if we receive the command to remove all categs_id  we remove
        # from public association all current categs_id.
        if extra_command[0] == 5 and current_extra_cats:
            vals['public_categ_ids'].append(
                [(3, x) for x in current_extra_cats.ids])

    return vals


def find_associated_pub_translation(env, int_translation, oldname=False):
    """
     takes a translation of a internal category and returns a translation of
     the public category.
    """
    translation_model = env['ir.translation']
    res = translation_model.search([
        ('name', '=', 'product.category,name'),
        ('res_id', '=', int_translation.id)
    ])
    if res:
        return res
    return translation_model.search([
        ('source', '=', oldname or int_translation.source),
        ('name', '=', 'product.public.category,name'),
        ('type', '=', int_translation.type),
        ('lang', '=', int_translation.lang)
    ])


def sync_translation(env, int_categories, oldname=False):
    """ syncs the internal category translations with the public category
        translation, completely, for first run
    """
    translation_model = env['ir.translation']
    for int_category in int_categories:
        int_translations = translation_model.search([
            ('res_id', '=', int_category.id),
            ('name', '=', 'product.category,name')])
        for int_translation in int_translations:
            # check if exists already public
            pub_trans = find_associated_pub_translation(
                env, int_translation, oldname or int_translation.source)
            if pub_trans:
                pub_trans.write({
                    'source': int_translation.source
                })
                continue
            translation_model.create({
                'source': int_translation.source,
                'name': 'product.public.category,name',
                'value': int_translation.value,
                'type': int_translation.type,
                'lang': int_translation.lang,
                'res_id': int_category.public_category_id.id
            })
