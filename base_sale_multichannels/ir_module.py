# FIXME: TO REMOVE ONCE (IF) MERGED IN SERVER

from osv import osv


class ir_module_module(osv.osv):

    _inherit = 'ir.module.module'

    def is_installed(self, cr, uid, module_name, context=None):
        if self.search(cr, 1, [['name', '=', module_name], ['state', 'in', ['installed', 'to upgrade']]], context=context):
            return True
        return False

ir_module_module()
