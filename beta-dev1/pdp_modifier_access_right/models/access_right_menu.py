from odoo import models, fields, api
from odoo import SUPERUSER_ID
import types


class IrUiMenu_common(models.Model):
    _inherit = 'ir.ui.menu'

    def search(self, args, offset=0, limit=None, order=None, count=False):

        if self._uid != SUPERUSER_ID:

            # TODO HIDE MENU WITH SALES GROUP
            if self.env.user.has_group('pdp_modifier_access_right.sales_group'):
                menu_data = [
                    'hr_timesheet.timesheet_menu_root',
                    'sg_hr_employee.menu_root_hr_parent',
                ]
                menu_ids = []
                for menu_item in menu_data:
                    menu = self.env.ref(menu_item)
                    if menu and menu.id:
                        menu_ids.append(menu.id)
                if menu_ids and len(menu_ids) > 0:
                    args.append(('id', 'not in', menu_ids))

        return super(IrUiMenu_common, self).search(args, offset, limit, order, count=count)
