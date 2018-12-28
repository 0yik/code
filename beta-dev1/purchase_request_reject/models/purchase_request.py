from odoo import models, fields, api

class reject_reason(models.Model):
    _name = 'reject.reason'

    name  = fields.Char('Reason')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.name or ''))
        return result

class purchase_request_reject_popup(models.TransientModel):
    _name= 'purchase.request.reject.popup'

    reason_ids = fields.Many2many('reject.reason',string='Reason',required=True)

    @api.multi
    def button_reject(self):
        for record in self:
            if self.env.context.get('active_id',False) and self.env.context.get('active_model',False) == 'purchase.request.line':
                line = self.env['purchase.request.line'].browse(self.env.context.get('active_id',False))
                line.request_state = 'rejected'
                request_id = line.request_id.id
                req_exist = self.env['purchase.request.line'].search([('request_id', '=', request_id),('request_state', '=', 'to_approve')])
                for reason_id in record.reason_ids:
                    line.request_id.write({'reason_ids': [(4,reason_id.id)]})
                if not req_exist:
                    line.request_id.button_rejected()

class purchase_request_line(models.Model):
    _inherit = 'purchase.request'

    reason_ids   = fields.Many2many('reject.reason',string='Rejection Reason')