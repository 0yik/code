# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ir_ui_menu(models.Model):
    _inherit = 'ir.ui.menu'

    def search(self, args, offset=0, limit=None, order=None, count=False):
        model, group_developer = self.env['ir.model.data'].get_object_reference('mgm_modifer_access_right', 'group_stevedoring_menu')
        if group_developer:
            group_developer_id = self.env[str(model)].browse(group_developer)
            if group_developer_id:
                user_all_ids = [us.id for us in group_developer_id.users]
                if self._uid in user_all_ids:
                    model, menu_id1 = self.env['ir.model.data'].get_object_reference('mgm_sales_contract', 'menu_sale_requisition_stevedoring')
                    args.append(('id','not in',[menu_id1]))

        model, group_developer = self.env['ir.model.data'].get_object_reference('mgm_modifer_access_right', 'group_flf_menu')
        if group_developer:
            group_developer_id = self.env[str(model)].browse(group_developer)
            if group_developer_id:
                user_all_ids = [us.id for us in group_developer_id.users]
                if self._uid in user_all_ids:
                    model, menu_id2 = self.env['ir.model.data'].get_object_reference('mgm_sales_contract','menu_sale_requisition_ferry')
                    model, menu_id3 = self.env['ir.model.data'].get_object_reference('mgm_sales_contract',
                                                                                     'menu_sale_requisition_fls')
                    model, menu_id4 = self.env['ir.model.data'].get_object_reference('mgm_sales_contract',
                                                                                     'menu_sale_requisition_tug_barge')
                    model, menu_id5 = self.env['ir.model.data'].get_object_reference('mgm_sales_contract',
                                                                                     'menu_sale_requisition_others')

                    args.append(('id','not in',[menu_id2,menu_id3,menu_id4,menu_id5]))

        return super(ir_ui_menu, self).search(args, offset, limit, order, count=count)