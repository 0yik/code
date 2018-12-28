from odoo import models, fields,api,tools
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class ResPartner(models.Model):
    _inherit = "res.partner"

    customer_edit_check = fields.Boolean(string="Customer Profile")
    customer_edit_date = fields.Datetime(string="Schedule Date")

    @api.multi
    def action_edit(self):
        if any([record.customer_edit_check for record in self]):
            raise UserError('This Profile is being edited now')
        self.write({'customer_edit_check': True, 'customer_edit_date': datetime.today()})

    @api.multi
    def action_discard(self):
        self.write({'customer_edit_check': False})

    @api.multi
    def action_save(self):
        self.write({'customer_edit_check': False})

    @api.model
    def customer_view_schedule(self):
        current_date = datetime.now()
        scheduler_date = fields.Datetime.to_string(current_date - relativedelta(minutes=2))
        partners = self.search([('customer_edit_date','<=',scheduler_date)])
        partners.write({'customer_edit_check': False})

ResPartner()