from odoo import fields, models, api
from odoo.exceptions import ValidationError


class purchase_request_inherit(models.Model):
    _inherit = 'purchase.request'

    approve_sub = fields.Char('Approver')

    @api.onchange('product_ctg')
    def onchange_product_ctg_pr(self):
        if self.product_ctg:
            self.approve_sub = self.setup_approver(self.product_ctg.line_ids)

    def setup_approver(self,lines):
        approve_status = ''
        fla_line = 0
        for line in lines:
            approve_status_line = ''
            if line.employee_ids:
                fla_emplyee = 0
                for employee in line.employee_ids:
                    fla_emplyee += 1
                    approve_status_line += employee.name
                    if fla_emplyee != len(line.employee_ids):
                        approve_status_line += '/'
            fla_line += 1
            approve_status += approve_status_line
            if fla_line != len(lines):
                approve_status += '/'
        return approve_status

