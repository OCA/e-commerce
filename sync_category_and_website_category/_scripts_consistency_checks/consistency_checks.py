"""
This script expects to be run on a buildout
"""
import argparse
import logging
import sys

# Flake8 raises F821 and is correctly signaling that session is not defined.
# flake8 does not know this should be called from python-odoo where we \
# already have session so we are silencing the message with # noqa comments

logging.basicConfig()
logger = logging.getLogger(__file__)
if 'session' not in locals():
    logger.error('Run me with python_odoo from a buildout!')
    sys.exit(1)

parser = argparse.ArgumentParser(
    description='Check sync consistency between public and private categs')
parser.add_argument('db', help='The name of your v9 database')
args = parser.parse_args()
session.open(args.db)  # noqa: F821
cr = session.cr  # noqa: F821


p_cats = session.env['product.public.category'].search([])  # noqa: F821
cats = session.env['product.category'].search([])  # noqa: F821

duplicates = []

for cat in cats:
    if len(cat.public_category_id) > 1:
        duplicates.append(
            (cat.id, cat.name, len(cat.public_category_id),
             cat.public_category_id))

logger.info('INTERNAL CATEGORIES WITH MULTIPLE PUBLIC CATEGORIES \n')
duplicate_msgs = [
    'Cat [%s] %s HAS Multiple (%s) PUBLIC CATEGORIES : %s  \n' % x
    for x in duplicates
]
logger.error(duplicate_msgs)


inconsistent = []
for p_cat in p_cats:
    if (len(p_cat.category_products.ids) !=
            len(p_cat.internal_category_id.category_products.ids)):
        inconsistent.append(
            (p_cat.id, p_cat.name, p_cat.category_products or 'None',
             p_cat.internal_category_id.ids, p_cat.internal_category_id.name,
             p_cat.internal_category_id.category_products.ids or 'None')
        )
logger.info('INCONSISTENT CATEGORIES \n')
if inconsistent:
    inconsistencies = ['Pub Cat [%s] %s - with products %s associated with '
                       'Cat [%s] %s with products %s \n'
                       % x for x in inconsistent]
else:
    inconsistencies = ['---------NO INCONSISTENCIES']
logger.error(inconsistencies)

unassigned = []

for cat in cats:
    if not cat.public_category_id:
        unassigned.append((cat.id, cat.name))
logger.info('UNASSIGNED INTERNAL CATEGORIES \n')
unassigned_msgs = [
    'Cat [%s] %s HAS NO PUBLIC CATEGORY  \n' % x for x in unassigned
]
logger.error(unassigned_msgs)


logger.info('Sync check summary------------------ \n'
            'inconsistencies: %s \n'
            'unassigned internal categories: %s \n'
            'int categories with multiple public cats: %s \n'
            '----------------------------------------- \n' %
            (len(inconsistencies), len(unassigned_msgs), len(duplicate_msgs)))
