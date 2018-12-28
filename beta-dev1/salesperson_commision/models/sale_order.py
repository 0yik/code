from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class sale_order(models.Model):
    _inherit = 'sale.order'

    employee_id = fields.Many2one('hr.employee', string='Salesperson')
    commission = fields.Float(string="Commission",default=0)

    @api.onchange('employee_id','amount_total')
    def commission_onchange_user_id(self):
        for record in self:
            # if record.user_id and record.amount_total:
                # employee_id = self.env['hr.employee'].search([('user_id','=',record.user_id.id)],limit=1)
            record.commission = record.amount_total * (record.employee_id and record.employee_id.commission or 0) / 100
            # else:
                # record.commission = 0

