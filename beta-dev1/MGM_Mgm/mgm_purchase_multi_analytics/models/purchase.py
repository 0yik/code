from odoo import api, fields, models, _



class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    @api.multi
    def analytic_account(self):
        ir_model_data = self.env['ir.model.data']
        try:
            compose_form_id = ir_model_data.get_object_reference('mgm_multi_assign_analytics', 'mgm_multi_assign_analytics_form')[1]
        except ValueError:
            compose_form_id = False

        res = {
            'type': 'ir.actions.act_window',
            'name': 'Analytics Accounting',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mgm.multi.assign.analytics',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': {}
        }
        return res

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def analytic_account(self):
        ir_model_data = self.env['ir.model.data']
        try:
            compose_form_id = ir_model_data.get_object_reference('mgm_multi_assign_analytics', 'mgm_multi_assign_analytics_form')[1]
        except ValueError:
            compose_form_id = False

        res = {
            'type': 'ir.actions.act_window',
            'name': 'Analytics Accounting',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mgm.multi.assign.analytics',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': {}
        }
        return res



    @api.multi
    def action_view_invoice(self):
        result = super(PurchaseOrder, self).action_view_invoice()
        result['context']['default_purchase_order_id'] = self.id
        return result

