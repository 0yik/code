# from odoo import models, fields, api, SUPERUSER_ID
#
# class ir_ui_menu(models.Model):
#     _inherit = 'ir.ui.menu'
#
#     def search(self,  args, offset=0, limit=0, order=None, count=False):
#         report_menu_ids = []
#         model,report_menu = self.env['ir.model.data'].get_object_reference('point_of_sale', 'menu_point_rep')
#         if report_menu:
#             report_menu_ids.append(report_menu)
#         # model, report_orders_id = self.env['ir.model.data'].get_object_reference('point_of_sale', 'menu_report_pos_order_all')
#         # if report_orders_id:
#         #     report_menu_ids.append(report_orders_id)
#         # model, report_sale_detail_id = self.env['ir.model.data'].get_object_reference('point_of_sale', 'menu_report_order_details')
#         # if report_sale_detail_id:
#         #     report_menu_ids.append(report_sale_detail_id)
#         # model, report_combo_id = self.env['ir.model.data'].get_object_reference('pos_combo', 'menu_analytic_report_pos_pack_customize')
#         # if report_combo_id:
#         #     report_menu_ids.append(report_combo_id)
#         model, pos_report_menu = self.env['ir.model.data'].get_object_reference('report_tax_auditor', 'menu_pos_sale_report')
#         if pos_report_menu:
#             report_menu_ids.append(pos_report_menu)
#         group_auditor_id = self.env['ir.model.data'].xmlid_to_res_id('report_tax_auditor.group_auditor')
#         if group_auditor_id and self._uid != SUPERUSER_ID:
#             if self._uid and self.env['res.users'].browse(self._uid).has_group('report_tax_auditor.group_auditor'):
#                 args.append(('id','in',report_menu_ids))
#         res = super(ir_ui_menu, self).search(args=args, offset=offset, limit=limit, order=order, count=count)
#         return res